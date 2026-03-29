import os
import pickle
import time
import threading
import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pathlib import Path

import pandas as pd

from tmdb_service import TMDBService
from ml_models import config as ml_config
from ml_models.itemknn import ItemKNN
from ml_models.hybrid_recommender import HybridRecommender
from ml_models.graphrag_reranker import GraphRAGReranker

logger = logging.getLogger(__name__)


class RecommendationError(Exception):
    pass


class RecommendationDataMissing(RecommendationError):
    pass


class RecommendationEngine:
    def __init__(self, assets_path: str, cache_ttl: int = 3600):
        self.assets_path = Path(assets_path)
        self.cache_ttl = cache_ttl
        self._ready = False
        self._lock = threading.Lock()

        self.itemknn_model: Optional[ItemKNN] = None
        self.hybrid_model: Optional[HybridRecommender] = None
        self.graph_model: Optional[GraphRAGReranker] = None

        self.user_history: Dict[str, Dict[int, List[int]]] = {}
        self.ml_to_tmdb: Dict[int, int] = {}
        self.tmdb_to_ml: Dict[int, int] = {}
        self.tmdb_cache: Dict[int, Tuple[float, Dict[str, Any]]] = {}

    def _ensure_resources(self):
        if self._ready:
            return

        with self._lock:
            if self._ready:
                return

            if not self.assets_path.is_dir():
                raise RecommendationDataMissing(
                    f"ML models directory not found at {self.assets_path}"
                )

            original_base = ml_config.BASE_DIR
            ml_config.BASE_DIR = self.assets_path
            ml_config.PROCESSED_DATA_DIR = self.assets_path / "data" / "processed"
            ml_config.KG_DIR = self.assets_path / "data" / "knowledge_graph"
            ml_config.MODELS_DIR = self.assets_path / "models"

            user_history_path = ml_config.PROCESSED_DATA_DIR / "user_history.pkl"
            links_path = ml_config.PROCESSED_DATA_DIR / "links.csv"

            if not user_history_path.exists() or not links_path.exists():
                raise RecommendationDataMissing(
                    f"Required data files missing: {user_history_path}, {links_path}"
                )

            logger.info(f"Loading user history from {user_history_path}")
            with open(user_history_path, "rb") as f:
                self.user_history = pickle.load(f)

            logger.info(f"Loading movie ID mappings from {links_path}")
            links_df = pd.read_csv(links_path)
            links_df = links_df.dropna(subset=["tmdbId"])
            links_df["movieId"] = links_df["movieId"].astype(int)
            links_df["tmdbId"] = links_df["tmdbId"].astype(float).astype(int)

            self.ml_to_tmdb = dict(zip(links_df["movieId"], links_df["tmdbId"]))
            self.tmdb_to_ml = {tmdb: ml for ml, tmdb in self.ml_to_tmdb.items()}

            logger.info("Loading ItemKNN model")
            self.itemknn_model = ItemKNN.load()

            logger.info("Loading GraphRAG reranker")
            self.graph_model = GraphRAGReranker()

            logger.info("Initializing hybrid recommender")
            self.hybrid_model = HybridRecommender(
                itemknn_model=self.itemknn_model,
                graphrag_model=self.graph_model
            )

            ml_config.BASE_DIR = original_base
            self._ready = True
            logger.info("Recommendation engine ready")

    def _extract_watchlist_history(self, watchlist_items: Sequence[Any]) -> List[int]:
        history = []
        seen = set()
        for entry in watchlist_items:
            tmdb_id = getattr(entry, "movie_id", None)
            if tmdb_id is None and isinstance(entry, dict):
                tmdb_id = entry.get("movie_id")

            if tmdb_id is None:
                continue

            try:
                tmdb_id = int(tmdb_id)
            except (TypeError, ValueError):
                continue

            ml_id = self.tmdb_to_ml.get(tmdb_id)
            if ml_id and ml_id not in seen:
                history.append(ml_id)
                seen.add(ml_id)

        return history

    def _resolve_user_history(
        self,
        ml_user_id: Optional[int],
        watchlist_items: Sequence[Any]
    ) -> Tuple[List[int], Optional[str], Optional[int]]:
        history: List[int] = []
        source: Optional[str] = None
        effective_user_id: Optional[int] = None

        if ml_user_id is not None:
            ml_user_id = int(ml_user_id)
            train_history = self.user_history.get("train", {}).get(ml_user_id)
            if train_history:
                history = list(train_history)
                source = "movielens"
                effective_user_id = ml_user_id

        if not history and watchlist_items:
            history = self._extract_watchlist_history(watchlist_items)
            if history:
                source = "watchlist"
                effective_user_id = None

        return history, source, effective_user_id

    def _add_context_movie(self, history: List[int], tmdb_movie_id: Optional[int]):
        if tmdb_movie_id is None:
            return

        try:
            tmdb_movie_id = int(tmdb_movie_id)
        except (TypeError, ValueError):
            return

        ml_id = self.tmdb_to_ml.get(tmdb_movie_id)
        if ml_id and ml_id not in history:
            history.append(ml_id)

    def _get_tmdb_movie(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        cached = self.tmdb_cache.get(tmdb_id)
        now = time.time()

        if cached:
            cached_time, payload = cached
            if now - cached_time <= self.cache_ttl:
                return payload

        details = TMDBService.get_movie_details(tmdb_id)
        if details:
            self.tmdb_cache[tmdb_id] = (now, details)
        return details

    def _build_recommendation_payload(
        self,
        movie_ids: List[int],
        scores: List[float],
        limit: int
    ) -> List[Dict[str, Any]]:
        payload = []

        for movie_id, score in zip(movie_ids, scores):
            tmdb_id = self.ml_to_tmdb.get(int(movie_id))
            if not tmdb_id:
                continue

            tmdb_data = self._get_tmdb_movie(tmdb_id)
            if not tmdb_data:
                continue

            payload.append({
                "id": int(tmdb_id),
                "movieId": int(movie_id),
                "title": tmdb_data.get("title"),
                "overview": tmdb_data.get("overview"),
                "poster_path": tmdb_data.get("poster_path"),
                "backdrop_path": tmdb_data.get("backdrop_path"),
                "release_date": tmdb_data.get("release_date"),
                "vote_average": tmdb_data.get("vote_average"),
                "score": round(float(score), 4) if score is not None else None
            })

            if len(payload) >= limit:
                break

        return payload

    def recommend(
        self,
        *,
        limit: int = 10,
        mode: str = "hybrid",
        ml_user_id: Optional[int] = None,
        watchlist_items: Sequence[Any] = (),
        movie_context_tmdb: Optional[int] = None
    ) -> Dict[str, Any]:
        self._ensure_resources()

        limit = max(1, min(limit, 20))
        requested_mode = (mode or "hybrid").lower()

        history, history_source, effective_user_id = self._resolve_user_history(
            ml_user_id,
            watchlist_items
        )

        self._add_context_movie(history, movie_context_tmdb)

        fallback_reason = None
        if not history:
            fallback_reason = "missing_history"

        model_used = requested_mode
        rec_ids: List[int] = []
        scores: List[float] = []

        if not fallback_reason:
            if requested_mode == "itemknn":
                if (
                    effective_user_id is not None and
                    effective_user_id in self.itemknn_model.user_to_idx
                ):
                    rec_ids, scores = self.itemknn_model.recommend(
                        effective_user_id,
                        history,
                        n=limit,
                        exclude_seen=True
                    )
                else:
                    fallback_reason = "unknown_user"

            elif requested_mode == "hybrid":
                if (
                    effective_user_id is not None and
                    effective_user_id in self.hybrid_model.itemknn.user_to_idx
                ):
                    rec_ids, scores = self.hybrid_model.recommend(
                        effective_user_id,
                        history,
                        n=limit,
                        exclude_seen=True
                    )
                else:
                    fallback_reason = "unknown_user"

            if fallback_reason is None and requested_mode == "graph":
                rec_ids, scores = self.graph_model.recommend(
                    effective_user_id or -1,
                    history,
                    n=limit,
                    exclude_seen=True
                )

        if (fallback_reason or not rec_ids) and history:
            model_used = "graph"
            fallback_reason = fallback_reason or "graph_fallback"
            rec_ids, scores = self.graph_model.recommend(
                effective_user_id or -1,
                history,
                n=limit,
                exclude_seen=True
            )

        payload = self._build_recommendation_payload(rec_ids, scores, limit)

        fallback = False
        if not payload:
            fallback = True
            fallback_reason = fallback_reason or "tmdb_lookup_failed"
            trending = TMDBService.get_trending_movies()
            payload = (trending or {}).get("results", [])[:limit]

        return {
            "mode": model_used,
            "requested_mode": requested_mode,
            "history_source": history_source,
            "count": len(payload),
            "fallback": fallback,
            "fallback_reason": fallback_reason,
            "recommendations": payload
        }


_engine: Optional[RecommendationEngine] = None
_engine_lock = threading.Lock()


def get_recommendation_engine(
    assets_path: str,
    cache_ttl: int
) -> RecommendationEngine:
    global _engine

    with _engine_lock:
        if _engine is None:
            _engine = RecommendationEngine(assets_path, cache_ttl)
        else:
            _engine.cache_ttl = cache_ttl
        return _engine
