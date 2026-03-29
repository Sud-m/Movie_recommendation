import numpy as np
import pandas as pd
import pickle
import logging
from tqdm import tqdm

try:
    from config import *
    from baseline_itemknn import ItemKNN
    from graphrag_reranker_simple import SimpleGraphRAGReranker
except ImportError:
    from src.config import *
    from baseline_itemknn import ItemKNN
    from graphrag_reranker_simple import SimpleGraphRAGReranker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridGraphRAG:
    """
    Hybrid recommender combining ItemKNN (collaborative) with GraphRAG (content)
    Stage 1: ItemKNN generates Top-100 candidates
    Stage 2: GraphRAG re-ranks them
    """

    def __init__(self, itemknn_model=None, graphrag_model=None, alpha=0.7):
        """
        Args:
            itemknn_model: Trained ItemKNN model
            graphrag_model: GraphRAG reranker
            alpha: Weight for ItemKNN score (1-alpha for GraphRAG)
        """
        self.alpha = alpha  # 0.7 means 70% ItemKNN, 30% GraphRAG

        # Load models
        if itemknn_model is None:
            logger.info("Loading ItemKNN model...")
            self.itemknn = ItemKNN.load()
        else:
            self.itemknn = itemknn_model

        if graphrag_model is None:
            logger.info("Loading GraphRAG model...")
            self.graphrag = SimpleGraphRAGReranker()
        else:
            self.graphrag = graphrag_model

        logger.info(f"✓ Hybrid model initialized (α={self.alpha})")

    def recommend(self, user_id, user_history, n=10, exclude_seen=True):
        """
        Generate hybrid recommendations

        Args:
            user_id: User ID
            user_history: List of user's watched movies
            n: Number of recommendations
            exclude_seen: Whether to exclude watched movies
        """
        # Stage 1: Get Top-100 from ItemKNN (collaborative filtering)
        top_k_candidates = 100
        itemknn_recs, itemknn_scores = self.itemknn.recommend(
            user_id,
            user_history,
            n=top_k_candidates,
            exclude_seen=exclude_seen
        )

        if not itemknn_recs:
            # Fallback to pure GraphRAG
            return self.graphrag.recommend(user_id, user_history, n=n)

        # Normalize ItemKNN scores to [0, 1]
        itemknn_scores = np.array(itemknn_scores)
        if itemknn_scores.max() > 0:
            itemknn_scores_norm = (itemknn_scores - itemknn_scores.min()) / (
                        itemknn_scores.max() - itemknn_scores.min())
        else:
            itemknn_scores_norm = np.zeros_like(itemknn_scores)

        # Stage 2: Re-rank with GraphRAG
        graphrag_recs, graphrag_scores = self.graphrag.rerank(
            user_id,
            user_history,
            itemknn_recs,
            top_k=top_k_candidates
        )

        # Normalize GraphRAG scores to [0, 1]
        graphrag_scores = np.array(graphrag_scores)
        if graphrag_scores.max() > 0:
            graphrag_scores_norm = (graphrag_scores - graphrag_scores.min()) / (
                        graphrag_scores.max() - graphrag_scores.min())
        else:
            graphrag_scores_norm = np.zeros_like(graphrag_scores)

        # Create mapping for GraphRAG scores
        graphrag_score_map = dict(zip(graphrag_recs, graphrag_scores_norm))

        # Combine scores
        hybrid_scores = []
        for i, movie_id in enumerate(itemknn_recs):
            cf_score = itemknn_scores_norm[i]
            graph_score = graphrag_score_map.get(movie_id, 0.0)

            # Weighted combination
            hybrid_score = self.alpha * cf_score + (1 - self.alpha) * graph_score
            hybrid_scores.append((movie_id, hybrid_score))

        # Sort by hybrid score
        hybrid_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top-N
        final_recs = [movie_id for movie_id, _ in hybrid_scores[:n]]
        final_scores = [score for _, score in hybrid_scores[:n]]

        return final_recs, final_scores


def main():
    """Test hybrid model"""
    logger.info("\n" + "=" * 70)
    logger.info("Hybrid GraphRAG Test")
    logger.info("=" * 70)

    # Initialize
    hybrid = HybridGraphRAG(alpha=0.7)  # 70% CF, 30% Graph

    # Load user history
    with open(PROCESSED_DATA_DIR / "user_history.pkl", 'rb') as f:
        user_history = pickle.load(f)

    # Find test user
    test_user = None
    for user_id, history in user_history['train'].items():
        if len(history) >= 20:
            test_user = user_id
            break

    if test_user is None:
        logger.error("No suitable test user found!")
        return

    user_train_history = user_history['train'][test_user]

    logger.info(f"\nTest User: {test_user}")
    logger.info(f"Training history: {len(user_train_history)} movies")

    # Get recommendations
    logger.info("\nGenerating hybrid recommendations...")
    recommendations, scores = hybrid.recommend(test_user, user_train_history, n=10)

    # Display results
    logger.info("\n" + "=" * 70)
    logger.info("Top 10 Hybrid Recommendations")
    logger.info("=" * 70)

    movies_df = pd.read_csv(PROCESSED_DATA_DIR / "movies.csv")
    movie_id_to_title = dict(zip(movies_df['movieId'], movies_df['title']))

    for i, (movie_id, score) in enumerate(zip(recommendations, scores), 1):
        title = movie_id_to_title.get(movie_id, f"Movie {movie_id}")
        genres = movies_df[movies_df['movieId'] == movie_id]['genres'].values
        genre_str = genres[0] if len(genres) > 0 else "Unknown"
        logger.info(f"{i:2d}. {title[:45]:<45} [{genre_str[:20]:<20}] (score: {score:.4f})")

    logger.info("=" * 70)
    logger.info("✓ Hybrid test complete")


if __name__ == "__main__":
    main()
