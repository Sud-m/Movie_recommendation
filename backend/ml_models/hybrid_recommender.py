import numpy as np
import logging

from .itemknn import ItemKNN
from .graphrag_reranker import GraphRAGReranker

logger = logging.getLogger(__name__)


class HybridRecommender:
    def __init__(self, itemknn_model=None, graphrag_model=None, alpha=0.7):
        self.alpha = alpha

        if itemknn_model is None:
            logger.info("Loading ItemKNN model...")
            self.itemknn = ItemKNN.load()
        else:
            self.itemknn = itemknn_model

        if graphrag_model is None:
            logger.info("Loading GraphRAG model...")
            self.graphrag = GraphRAGReranker()
        else:
            self.graphrag = graphrag_model

        logger.info(f"Hybrid model initialized (α={self.alpha})")

    def recommend(self, user_id, user_history, n=10, exclude_seen=True):
        top_k_candidates = 100
        itemknn_recs, itemknn_scores = self.itemknn.recommend(
            user_id,
            user_history,
            n=top_k_candidates,
            exclude_seen=exclude_seen
        )

        if not itemknn_recs:
            return self.graphrag.recommend(user_id, user_history, n=n)

        itemknn_scores = np.array(itemknn_scores)
        if itemknn_scores.max() > 0:
            itemknn_scores_norm = (
                (itemknn_scores - itemknn_scores.min()) /
                (itemknn_scores.max() - itemknn_scores.min())
            )
        else:
            itemknn_scores_norm = np.zeros_like(itemknn_scores)

        graphrag_recs, graphrag_scores = self.graphrag.rerank(
            user_id,
            user_history,
            itemknn_recs,
            top_k=top_k_candidates
        )

        graphrag_scores = np.array(graphrag_scores)
        if graphrag_scores.max() > 0:
            graphrag_scores_norm = (
                (graphrag_scores - graphrag_scores.min()) /
                (graphrag_scores.max() - graphrag_scores.min())
            )
        else:
            graphrag_scores_norm = np.zeros_like(graphrag_scores)

        graphrag_score_map = dict(zip(graphrag_recs, graphrag_scores_norm))

        hybrid_scores = []
        for i, movie_id in enumerate(itemknn_recs):
            cf_score = itemknn_scores_norm[i]
            graph_score = graphrag_score_map.get(movie_id, 0.0)
            hybrid_score = self.alpha * cf_score + (1 - self.alpha) * graph_score
            hybrid_scores.append((movie_id, hybrid_score))

        hybrid_scores.sort(key=lambda x: x[1], reverse=True)

        final_recs = [movie_id for movie_id, _ in hybrid_scores[:n]]
        final_scores = [score for _, score in hybrid_scores[:n]]

        return final_recs, final_scores
