import numpy as np
import pandas as pd
import pickle
from collections import Counter
from tqdm import tqdm
import logging

from .config import KG_DIR, PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)


class GraphRAGReranker:
    def __init__(self, kg_path=None):
        if kg_path is None:
            kg_path = KG_DIR / "movie_kg.gpickle"

        logger.info("Loading knowledge graph...")
        with open(kg_path, "rb") as f:
            self.kg = pickle.load(f)
        logger.info(
            f"Loaded KG: {self.kg.number_of_nodes():,} nodes, "
            f"{self.kg.number_of_edges():,} edges"
        )

        self.movies_df = pd.read_csv(PROCESSED_DATA_DIR / "movies.csv")
        self.movie_id_to_title = dict(
            zip(self.movies_df["movieId"], self.movies_df["title"])
        )

        self._precompute_movie_features()

    def _precompute_movie_features(self):
        logger.info("Extracting movie features from KG...")
        self.movie_features = {}

        for node, data in tqdm(self.kg.nodes(data=True), desc="Processing movies", leave=False):
            if data.get("type") != "movie":
                continue

            movie_id = data.get("movie_id")
            if movie_id is None:
                continue

            genres = set()
            tags = set()
            decades = set()
            similar_movies = set()

            for neighbor in self.kg.neighbors(node):
                neighbor_data = self.kg.nodes[neighbor]
                neighbor_type = neighbor_data.get("type")

                if neighbor_type == "genre":
                    genres.add(neighbor_data.get("name", ""))
                elif neighbor_type == "tag":
                    tags.add(neighbor_data.get("name", ""))
                elif neighbor_type == "decade":
                    decades.add(neighbor_data.get("decade", 0))
                elif neighbor_type == "movie":
                    edge_data = self.kg.get_edge_data(node, neighbor)
                    if edge_data and edge_data.get("relation") == "SIMILAR_TO":
                        similar_movies.add(neighbor_data.get("movie_id"))

            self.movie_features[movie_id] = {
                "genres": genres,
                "tags": tags,
                "decades": decades,
                "similar_movies": similar_movies
            }

        logger.info(f"Extracted features for {len(self.movie_features):,} movies")

    def compute_similarity(self, movie1_id, movie2_id):
        if movie1_id not in self.movie_features or movie2_id not in self.movie_features:
            return 0.0

        feat1 = self.movie_features[movie1_id]
        feat2 = self.movie_features[movie2_id]

        scores = []

        if feat1["genres"] or feat2["genres"]:
            genre_intersection = len(feat1["genres"] & feat2["genres"])
            genre_union = len(feat1["genres"] | feat2["genres"])
            genre_sim = genre_intersection / genre_union if genre_union > 0 else 0
            scores.append(("genre", genre_sim, 3.0))

        if feat1["tags"] or feat2["tags"]:
            tag_intersection = len(feat1["tags"] & feat2["tags"])
            tag_union = len(feat1["tags"] | feat2["tags"])
            tag_sim = tag_intersection / tag_union if tag_union > 0 else 0
            scores.append(("tag", tag_sim, 1.0))

        if feat1["decades"] and feat2["decades"]:
            decade_match = 1.0 if feat1["decades"] & feat2["decades"] else 0.0
            scores.append(("decade", decade_match, 0.5))

        if movie2_id in feat1["similar_movies"]:
            scores.append(("direct", 1.0, 2.0))

        if not scores:
            return 0.0

        total_weight = sum(w for _, _, w in scores)
        weighted_sum = sum(s * w for _, s, w in scores)

        return weighted_sum / total_weight

    def create_user_profile(self, user_history):
        profile = {
            "genres": Counter(),
            "tags": Counter(),
            "decades": Counter()
        }

        for movie_id in user_history:
            if movie_id in self.movie_features:
                feat = self.movie_features[movie_id]

                for genre in feat["genres"]:
                    profile["genres"][genre] += 1

                for tag in feat["tags"]:
                    profile["tags"][tag] += 1

                for decade in feat["decades"]:
                    profile["decades"][decade] += 1

        return profile

    def score_candidate(self, user_profile, candidate_id):
        if candidate_id not in self.movie_features:
            return 0.0

        candidate_feat = self.movie_features[candidate_id]

        scores = []

        genre_score = sum(user_profile["genres"].get(g, 0) for g in candidate_feat["genres"])
        if genre_score > 0:
            scores.append(genre_score * 3.0)

        tag_score = sum(user_profile["tags"].get(t, 0) for t in candidate_feat["tags"])
        if tag_score > 0:
            scores.append(tag_score * 1.0)

        decade_score = sum(
            user_profile["decades"].get(d, 0) for d in candidate_feat["decades"]
        )
        if decade_score > 0:
            scores.append(decade_score * 0.5)

        total_user_interactions = sum(user_profile["genres"].values())
        if total_user_interactions > 0:
            return sum(scores) / total_user_interactions
        else:
            return 0.0

    def rerank(self, user_id, user_history, candidates, top_k=10):
        user_profile = self.create_user_profile(user_history[-50:])

        scored_candidates = []

        for candidate_id in candidates:
            profile_score = self.score_candidate(user_profile, candidate_id)

            history_scores = []
            for hist_movie in user_history[-10:]:
                sim = self.compute_similarity(hist_movie, candidate_id)
                history_scores.append(sim)

            history_score = np.mean(history_scores) if history_scores else 0.0
            final_score = 0.6 * profile_score + 0.4 * history_score

            scored_candidates.append((candidate_id, final_score))

        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        recommendations = [movie_id for movie_id, _ in scored_candidates[:top_k]]
        scores = [score for _, score in scored_candidates[:top_k]]

        return recommendations, scores

    def recommend(self, user_id, user_history, n=10, exclude_seen=True):
        all_movies = list(self.movie_features.keys())

        if exclude_seen:
            candidates = [m for m in all_movies if m not in user_history]
        else:
            candidates = all_movies

        return self.rerank(user_id, user_history, candidates, top_k=n)
