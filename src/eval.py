import numpy as np
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
import pickle
import json
from pathlib import Path
import logging

try:
    from config import *
except ImportError:
    from src.config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommenderEvaluator:
    """Comprehensive evaluation framework for recommender systems"""

    def __init__(self):
        self.results = defaultdict(dict)

    @staticmethod
    def recall_at_k(predictions, ground_truth, k=10):
        """Recall@K: Proportion of relevant items in top-K"""
        if not ground_truth:
            return 0.0

        top_k = predictions[:k]
        hits = len(set(top_k) & set(ground_truth))
        return hits / len(ground_truth)

    @staticmethod
    def precision_at_k(predictions, ground_truth, k=10):
        """Precision@K: Proportion of top-K that are relevant"""
        if k == 0:
            return 0.0

        top_k = predictions[:k]
        hits = len(set(top_k) & set(ground_truth))
        return hits / k

    @staticmethod
    def ndcg_at_k(predictions, ground_truth, k=10):
        """Normalized Discounted Cumulative Gain@K"""

        def dcg_at_k(r, k):
            r = np.asfarray(r)[:k]
            if r.size:
                return np.sum(r / np.log2(np.arange(2, r.size + 2)))
            return 0.0

        # Create relevance list
        relevance = [1 if item in ground_truth else 0 for item in predictions[:k]]

        # Ideal relevance (all 1s)
        ideal_relevance = [1] * min(len(ground_truth), k) + [0] * max(0, k - len(ground_truth))

        dcg = dcg_at_k(relevance, k)
        idcg = dcg_at_k(ideal_relevance, k)

        if idcg == 0:
            return 0.0

        return dcg / idcg

    @staticmethod
    def mrr(predictions, ground_truth):
        """Mean Reciprocal Rank"""
        for i, item in enumerate(predictions, 1):
            if item in ground_truth:
                return 1.0 / i
        return 0.0

    @staticmethod
    def hit_rate_at_k(predictions, ground_truth, k=10):
        """Hit Rate@K: Whether any relevant item is in top-K"""
        top_k = predictions[:k]
        return 1.0 if len(set(top_k) & set(ground_truth)) > 0 else 0.0

    def evaluate_ranking(self, predictions, ground_truth, k_values=[5, 10, 20]):
        """Evaluate ranking metrics for a single user"""
        metrics = {}

        for k in k_values:
            metrics[f'Recall@{k}'] = self.recall_at_k(predictions, ground_truth, k)
            metrics[f'Precision@{k}'] = self.precision_at_k(predictions, ground_truth, k)
            metrics[f'NDCG@{k}'] = self.ndcg_at_k(predictions, ground_truth, k)
            metrics[f'Hit@{k}'] = self.hit_rate_at_k(predictions, ground_truth, k)

        metrics['MRR'] = self.mrr(predictions, ground_truth)

        return metrics

    @staticmethod
    def catalog_coverage(all_recommendations, total_items):
        """Catalog Coverage: Percentage of items recommended at least once"""
        unique_items = set()
        for recs in all_recommendations:
            unique_items.update(recs)

        return len(unique_items) / total_items if total_items > 0 else 0.0

    @staticmethod
    def gini_coefficient(recommendation_counts):
        """Gini Coefficient: Measure of recommendation fairness (0=fair, 1=unfair)"""
        if len(recommendation_counts) == 0:
            return 0.0

        sorted_counts = np.sort(recommendation_counts)
        n = len(sorted_counts)
        index = np.arange(1, n + 1)

        return (2 * np.sum(index * sorted_counts)) / (n * np.sum(sorted_counts)) - (n + 1) / n

    @staticmethod
    def intra_list_diversity(recommendations, item_similarity_matrix=None):
        """Intra-List Diversity: Average dissimilarity within recommendation list"""
        if item_similarity_matrix is None or len(recommendations) < 2:
            return 0.0

        diversity_sum = 0.0
        count = 0

        for i in range(len(recommendations)):
            for j in range(i + 1, len(recommendations)):
                item1, item2 = recommendations[i], recommendations[j]
                if item1 in item_similarity_matrix and item2 in item_similarity_matrix[item1]:
                    similarity = item_similarity_matrix[item1][item2]
                    diversity_sum += (1 - similarity)
                    count += 1

        return diversity_sum / count if count > 0 else 0.0

    def evaluate_model(self, model, test_data, user_history, model_name="Model",
                       k_values=[5, 10, 20], max_users=None):
        """
        Evaluate a recommendation model

        Args:
            model: Recommender model with recommend() method
            test_data: DataFrame with userId and movieId columns
            user_history: Dict mapping userId to list of seen items
            model_name: Name for results
            k_values: K values for metrics
            max_users: Maximum users to evaluate (for speed)
        """
        logger.info(f"\n{'=' * 70}")
        logger.info(f"Evaluating {model_name}")
        logger.info(f"{'=' * 70}")

        # Group test data by user
        test_by_user = test_data.groupby('userId')['movieId'].apply(list).to_dict()

        # Limit users if specified
        if max_users and len(test_by_user) > max_users:
            import random
            test_users = random.sample(list(test_by_user.keys()), max_users)
            test_by_user = {u: test_by_user[u] for u in test_users}

        logger.info(f"Evaluating on {len(test_by_user):,} users")

        # Collect all metrics
        all_metrics = defaultdict(list)
        all_recommendations = []
        recommendation_counts = defaultdict(int)

        # Evaluate each user
        for user_id in tqdm(test_by_user.keys(), desc=f"Evaluating {model_name}"):
            # Get user's history and ground truth
            user_train_history = user_history['train'].get(user_id, [])
            ground_truth = test_by_user[user_id]

            if not user_train_history:
                continue

            # Get recommendations
            try:
                if hasattr(model, 'rerank'):
                    # GraphRAG-style: needs candidates
                    # Get top candidates from training data (simple heuristic)
                    all_items = set(pd.read_csv(PROCESSED_DATA_DIR / "movies.csv")['movieId'])
                    candidates = list(all_items - set(user_train_history))[:100]
                    recommendations, _ = model.rerank(user_id, user_train_history, candidates, top_k=20)
                else:
                    # Standard recommender
                    recommendations, _ = model.recommend(user_id, user_train_history, n=20)

                if not recommendations:
                    continue

                # Evaluate metrics
                user_metrics = self.evaluate_ranking(recommendations, ground_truth, k_values)

                for metric_name, value in user_metrics.items():
                    all_metrics[metric_name].append(value)

                # Track recommendations for beyond-accuracy metrics
                all_recommendations.append(recommendations[:10])
                for item in recommendations[:10]:
                    recommendation_counts[item] += 1

            except Exception as e:
                logger.warning(f"Error evaluating user {user_id}: {e}")
                continue

        # Aggregate metrics
        results = {}
        for metric_name, values in all_metrics.items():
            results[metric_name] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'median': float(np.median(values))
            }

        # Beyond-accuracy metrics
        total_items = len(pd.read_csv(PROCESSED_DATA_DIR / "movies.csv"))
        results['Coverage'] = self.catalog_coverage(all_recommendations, total_items)

        rec_count_values = list(recommendation_counts.values())
        if rec_count_values:
            results['Gini'] = self.gini_coefficient(rec_count_values)
        else:
            results['Gini'] = 0.0

        # Store results
        self.results[model_name] = results

        # Print summary
        self._print_results(model_name, results, k_values)

        return results

    def _print_results(self, model_name, results, k_values):
        """Print evaluation results"""
        logger.info(f"\n{model_name} Results:")
        logger.info("-" * 70)

        # Accuracy metrics
        logger.info("\nAccuracy Metrics:")
        for k in k_values:
            logger.info(f"  K={k}:")
            for metric in ['Recall', 'Precision', 'NDCG', 'Hit']:
                key = f'{metric}@{k}'
                if key in results:
                    logger.info(f"    {metric:>10}: {results[key]['mean']:.4f} ± {results[key]['std']:.4f}")

        if 'MRR' in results:
            logger.info(f"\n  {'MRR':>10}: {results['MRR']['mean']:.4f} ± {results['MRR']['std']:.4f}")

        # Beyond-accuracy metrics
        logger.info("\nBeyond-Accuracy Metrics:")
        logger.info(f"  {'Coverage':>15}: {results['Coverage']:.4f} ({results['Coverage'] * 100:.2f}%)")
        logger.info(f"  {'Gini Coefficient':>15}: {results['Gini']:.4f}")

        logger.info("-" * 70)

    def compare_models(self):
        """Compare all evaluated models"""
        if len(self.results) < 2:
            logger.warning("Need at least 2 models to compare")
            return

        logger.info("\n" + "=" * 70)
        logger.info("Model Comparison")
        logger.info("=" * 70)

        # Create comparison table
        comparison_df = []

        for model_name, results in self.results.items():
            row = {'Model': model_name}

            # Key metrics
            if 'NDCG@10' in results:
                row['NDCG@10'] = results['NDCG@10']['mean']
            if 'Recall@10' in results:
                row['Recall@10'] = results['Recall@10']['mean']
            if 'MRR' in results:
                row['MRR'] = results['MRR']['mean']

            row['Coverage'] = results.get('Coverage', 0.0)
            row['Gini'] = results.get('Gini', 0.0)

            comparison_df.append(row)

        comparison_df = pd.DataFrame(comparison_df)

        print("\n", comparison_df.to_string(index=False))

        # Save comparison
        comparison_df.to_csv(RESULTS_DIR / 'tables' / 'model_comparison.csv', index=False)
        logger.info(f"\n✓ Comparison saved to {RESULTS_DIR / 'tables' / 'model_comparison.csv'}")

        return comparison_df

    def save_results(self, filename='evaluation_results.json'):
        """Save all results to file"""
        output_path = RESULTS_DIR / 'tables' / filename

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"✓ Results saved to {output_path}")


def main():
    """Test evaluation framework"""
    from baseline_itemknn import ItemKNN

    # Load model
    model = ItemKNN.load()

    # Load test data
    test_df = pd.read_csv(PROCESSED_DATA_DIR / "test.csv")

    # Load user history
    with open(PROCESSED_DATA_DIR / "user_history.pkl", 'rb') as f:
        user_history = pickle.load(f)

    # Evaluate
    evaluator = RecommenderEvaluator()
    evaluator.evaluate_model(
        model,
        test_df,
        user_history,
        model_name="ItemKNN",
        max_users=1000  # Quick test on 1000 users
    )

    evaluator.save_results('itemknn_results.json')


if __name__ == "__main__":
    main()
