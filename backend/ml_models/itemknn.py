import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import logging

from .config import MODELS_DIR

logger = logging.getLogger(__name__)


class ItemKNN:
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
        self.user_ids = train_df["userId"].unique()
        self.item_ids = train_df["movieId"].unique()

        self.user_to_idx = {u: i for i, u in enumerate(self.user_ids)}
        self.item_to_idx = {i: idx for idx, i in enumerate(self.item_ids)}
        self.idx_to_item = {idx: i for i, idx in self.item_to_idx.items()}

        rows = train_df["userId"].map(self.user_to_idx).values
        cols = train_df["movieId"].map(self.item_to_idx).values
        data = train_df["rating"].values

        self.user_item_matrix = csr_matrix(
            (data, (rows, cols)),
            shape=(len(self.user_ids), len(self.item_ids))
        )

        self.similarity_matrix = cosine_similarity(
            self.user_item_matrix.T, dense_output=True
        )

    def predict_score(self, user_id, item_id):
        if user_id not in self.user_to_idx or item_id not in self.item_to_idx:
            return 0.0

        user_idx = self.user_to_idx[user_id]
        item_idx = self.item_to_idx[item_id]

        user_ratings = self.user_item_matrix[user_idx].toarray().flatten()
        rated_items = user_ratings.nonzero()[0]

        if len(rated_items) == 0:
            return 0.0

        item_sims = self.similarity_matrix[item_idx, rated_items]
        rated_values = user_ratings[rated_items]

        if len(item_sims) > self.k:
            top_k_indices = np.argsort(item_sims)[-self.k:]
            item_sims = item_sims[top_k_indices]
            rated_values = rated_values[top_k_indices]

        sim_sum = np.sum(np.abs(item_sims))
        if sim_sum > 0:
            score = np.dot(item_sims, rated_values) / sim_sum
        else:
            score = 0.0

        return float(score)

    def recommend(self, user_id, user_history, n=10, exclude_seen=True):
        candidate_items = list(self.item_ids)

        if exclude_seen:
            candidate_items = [i for i in candidate_items if i not in user_history]

        scores = []
        for item in candidate_items:
            score = self.predict_score(user_id, item)
            scores.append((item, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        recommendations = [item for item, _ in scores[:n]]
        rec_scores = [score for _, score in scores[:n]]

        return recommendations, rec_scores

    def save(self, path=None):
        if path is None:
            path = MODELS_DIR / "itemknn.pkl"

        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path=None):
        if path is None:
            path = MODELS_DIR / "itemknn.pkl"

        with open(path, "rb") as f:
            model = pickle.load(f)
        return model
