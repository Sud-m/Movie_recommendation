import pandas as pd
import pickle
import logging
from pathlib import Path
import sys

try:
    from config import *
    from baseline_itemknn import ItemKNN
    from hybrid_graphrag import HybridGraphRAG  # Use hybrid!
    from evaluation import RecommenderEvaluator
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from config import *
    from baseline_itemknn import ItemKNN
    from hybrid_graphrag import HybridGraphRAG
    from evaluation import RecommenderEvaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Complete evaluation pipeline"""
    print("\n" + "=" * 70)
    print("COMPLETE EVALUATION PIPELINE")
    print("MovieLens-32M: ItemKNN vs Hybrid GraphRAG")
    print("=" * 70)

    # Load data
    logger.info("\nLoading data...")
    test_df = pd.read_csv(PROCESSED_DATA_DIR / "test.csv")

    with open(PROCESSED_DATA_DIR / "user_history.pkl", 'rb') as f:
        user_history = pickle.load(f)

    # Filter to users with sufficient history
    logger.info("Filtering users with sufficient history...")
    users_with_history = []
    for user_id in test_df['userId'].unique():
        train_history = user_history['train'].get(user_id, [])
        if len(train_history) >= 10:
            users_with_history.append(user_id)

    logger.info(f"✓ Found {len(users_with_history):,} users with ≥10 training ratings")

    # Sample users
    import random
    random.seed(RANDOM_SEED)

    if len(users_with_history) > 1000:
        eval_users = random.sample(users_with_history, 1000)
        logger.info(f"✓ Sampling 1,000 users for evaluation")
    else:
        eval_users = users_with_history

    test_df_filtered = test_df[test_df['userId'].isin(eval_users)]
    logger.info(f"✓ Test set: {len(test_df_filtered):,} interactions from {len(eval_users):,} users")

    # Initialize evaluator
    evaluator = RecommenderEvaluator()

    # ============================================
    # 1. EVALUATE ITEMKNN BASELINE
    # ============================================
    logger.info("\n" + "=" * 70)
    logger.info("1/2: Evaluating ItemKNN Baseline")
    logger.info("=" * 70)
    itemknn = ItemKNN.load()

    evaluator.evaluate_model(
        itemknn,
        test_df_filtered,
        user_history,
        model_name="ItemKNN",
        k_values=[5, 10, 20],
        max_users=len(eval_users)
    )

    # ============================================
    # 2. EVALUATE HYBRID GRAPHRAG
    # ============================================
    logger.info("\n" + "=" * 70)
    logger.info("2/2: Evaluating Hybrid GraphRAG (70% CF + 30% Graph)")
    logger.info("=" * 70)

    # Try different alpha values
    for alpha in [0.7, 0.5]:
        hybrid = HybridGraphRAG(itemknn_model=itemknn, alpha=alpha)

        evaluator.evaluate_model(
            hybrid,
            test_df_filtered,
            user_history,
            model_name=f"HybridGraphRAG (α={alpha})",
            k_values=[5, 10, 20],
            max_users=len(eval_users)
        )

    # ============================================
    # 3. COMPARE ALL MODELS
    # ============================================
    logger.info("\n" + "=" * 70)
    logger.info("FINAL COMPARISON")
    logger.info("=" * 70)
    comparison_df = evaluator.compare_models()

    evaluator.save_results('hybrid_evaluation_results.json')

    print("\n" + "=" * 70)
    print("✓ EVALUATION COMPLETE!")
    print("=" * 70)
    print(f"\nResults saved to: {RESULTS_DIR / 'tables'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
