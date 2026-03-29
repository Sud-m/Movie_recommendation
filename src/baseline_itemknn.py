import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from pathlib import Path
from tqdm import tqdm
import logging

try:
    from config import *
except ImportError:
    from src.config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ItemKNN:
    """Item-based K-Nearest Neighbors Collaborative Filtering"""

    def __init__(self, k=20):
        self.k = k
        self.similarity_matrix = None
        self.user_item_matrix = None
        self.item_ids = None
        self.user_ids = None
        self.item_to_idx = None
        self.user_to_idx = None
        self.idx_to_item = None

    def fit(self, train_df):
        """Train ItemKNN on interaction data"""
        logger.info("\n" + "=" * 70)
        logger.info("Training ItemKNN")
        logger.info("=" * 70)

        # Create mappings
        self.user_ids = train_df['userId'].unique()
        self.item_ids = train_df['movieId'].unique()

        self.user_to_idx = {u: i for i, u in enumerate(self.user_ids)}
        self.item_to_idx = {i: idx for idx, i in enumerate(self.item_ids)}
        self.idx_to_item = {idx: i for i, idx in self.item_to_idx.items()}

        logger.info(f"Users: {len(self.user_ids):,}")
        logger.info(f"Items: {len(self.item_ids):,}")

        # Create sparse user-item matrix
        rows = train_df['userId'].map(self.user_to_idx).values
        cols = train_df['movieId'].map(self.item_to_idx).values
        data = train_df['rating'].values

        self.user_item_matrix = csr_matrix(
            (data, (rows, cols)),
            shape=(len(self.user_ids), len(self.item_ids))
        )

        logger.info(
            f"Matrix density: {self.user_item_matrix.nnz / (self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]):.4%}")

        # Compute item-item similarity
        logger.info("Computing item-item similarity...")
        self.similarity_matrix = cosine_similarity(self.user_item_matrix.T, dense_output=True)

        logger.info("✓ ItemKNN training complete")

    def predict_score(self, user_id, item_id):
        """Predict rating for user-item pair"""
        if user_id not in self.user_to_idx or item_id not in self.item_to_idx:
            return 0.0

        user_idx = self.user_to_idx[user_id]
        item_idx = self.item_to_idx[item_id]

        # Get user's ratings
        user_ratings = self.user_item_matrix[user_idx].toarray().flatten()
        rated_items = user_ratings.nonzero()[0]

        if len(rated_items) == 0:
            return 0.0

        # Get similarities to rated items
        item_sims = self.similarity_matrix[item_idx, rated_items]
        rated_values = user_ratings[rated_items]

        # Get top-k most similar
        if len(item_sims) > self.k:
            top_k_indices = np.argsort(item_sims)[-self.k:]
            item_sims = item_sims[top_k_indices]
            rated_values = rated_values[top_k_indices]

        # Weighted average
        sim_sum = np.sum(np.abs(item_sims))
        if sim_sum > 0:
            score = np.dot(item_sims, rated_values) / sim_sum
        else:
            score = 0.0

        return float(score)

    def recommend(self, user_id, user_history, n=10, exclude_seen=True):
        """Generate top-N recommendations for a user"""
        # Get all items
        candidate_items = list(self.item_ids)

        # Exclude seen items
        if exclude_seen:
            candidate_items = [i for i in candidate_items if i not in user_history]

        # Score all candidates
        scores = []
        for item in candidate_items:
            score = self.predict_score(user_id, item)
            scores.append((item, score))

        # Sort and return top-N
        scores.sort(key=lambda x: x[1], reverse=True)
        recommendations = [item for item, _ in scores[:n]]
        rec_scores = [score for _, score in scores[:n]]

        return recommendations, rec_scores

    def save(self, path=None):
        """Save model"""
        if path is None:
            path = MODELS_DIR / "itemknn.pkl"

        with open(path, 'wb') as f:
            pickle.dump(self, f)
        logger.info(f"✓ Model saved to {path}")

    @staticmethod
    def load(path=None):
        """Load model"""
        if path is None:
            path = MODELS_DIR / "itemknn.pkl"

        with open(path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"✓ Model loaded from {path}")
        return model


def train_itemknn():
    """Train ItemKNN baseline"""
    # Load data
    train_df = pd.read_csv(PROCESSED_DATA_DIR / "train.csv")

    # Train model
    model = ItemKNN(k=20)
    model.fit(train_df)

    # Save
    model.save()

    return model


if __name__ == "__main__":
    model = train_itemknn()
