import pandas as pd
import numpy as np
import os
from pathlib import Path
from tqdm import tqdm
import pickle
import json
from collections import defaultdict
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.config import *


class MovieLensPreprocessor:
    """
    Preprocessor for MovieLens-32M dataset
    Handles loading, filtering, splitting, and format conversion
    """

    def __init__(self, sample_size=None):
        self.sample_size = sample_size or SAMPLE_SIZE
        self.ratings = None
        self.movies = None
        self.links = None
        self.tags = None
        self.train = None
        self.val = None
        self.test = None

    def verify_data_exists(self):
        """Verify that MovieLens data exists"""
        print("Checking for MovieLens dataset...")

        # Check if dataset directory exists
        if not DATASET_DIR.exists():
            raise FileNotFoundError(
                f"\n❌ ERROR: {DATASET_DIR} does not exist!\n\n"
                f"Please create the directory and copy your dataset:\n"
                f"  mkdir -p {DATASET_DIR}\n"
                f"  cp -r /path/to/your/ml-32m/* {DATASET_DIR}/\n\n"
                f"Your directory should contain:\n"
                f"  - ratings.csv (required)\n"
                f"  - movies.csv (required)\n"
                f"  - links.csv (required)\n"
                f"  - tags.csv (optional)\n"
                f"  - README.txt (optional)"
            )

        # Check required files
        required_files = ['ratings.csv', 'movies.csv', 'links.csv']
        missing_files = []

        for file in required_files:
            if not (DATASET_DIR / file).exists():
                missing_files.append(file)

        if missing_files:
            raise FileNotFoundError(
                f"\n❌ ERROR: Missing required files in {DATASET_DIR}:\n"
                f"  {', '.join(missing_files)}\n\n"
                f"Please ensure all required files are present."
            )

        print(f"✓ Found MovieLens dataset in {DATASET_DIR}")

        # Display file sizes
        print(f"\nDataset files:")
        for file in ['ratings.csv', 'movies.csv', 'links.csv', 'tags.csv']:
            file_path = DATASET_DIR / file
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  {file:<15} {size_mb:>8.1f} MB")

        return DATASET_DIR

    def load_data(self):
        """Load MovieLens data"""
        print("\n" + "=" * 70)
        print("Loading MovieLens Dataset")
        print("=" * 70)

        dataset_dir = self.verify_data_exists()

        # Load ratings with optional sampling
        print("\nLoading ratings.csv...")
        if self.sample_size:
            print(f"  (Sampling {self.sample_size:,} ratings for faster processing)")
            self.ratings = pd.read_csv(
                dataset_dir / "ratings.csv",
                nrows=self.sample_size
            )
        else:
            print("  (Loading full dataset - this may take a minute...)")
            self.ratings = pd.read_csv(dataset_dir / "ratings.csv")

        print(f"✓ Loaded {len(self.ratings):,} ratings")

        # Load movies
        print("Loading movies.csv...")
        self.movies = pd.read_csv(dataset_dir / "movies.csv")
        print(f"✓ Loaded {len(self.movies):,} movies")

        # Load links
        print("Loading links.csv...")
        self.links = pd.read_csv(dataset_dir / "links.csv")
        print(f"✓ Loaded {len(self.links):,} movie links")

        # Load tags (optional)
        if (dataset_dir / "tags.csv").exists():
            print("Loading tags.csv...")
            self.tags = pd.read_csv(dataset_dir / "tags.csv")
            print(f"✓ Loaded {len(self.tags):,} tags")

        # Display basic statistics
        print("\n" + "-" * 70)
        print("Dataset Overview:")
        print("-" * 70)
        print(f"{'Metric':<30} {'Value':>20}")
        print("-" * 70)
        print(f"{'Total Ratings':<30} {len(self.ratings):>20,}")
        print(f"{'Unique Users':<30} {self.ratings['userId'].nunique():>20,}")
        print(f"{'Unique Movies':<30} {self.ratings['movieId'].nunique():>20,}")
        print(f"{'Rating Scale':<30} {self.ratings['rating'].min():>10.1f} to {self.ratings['rating'].max():.1f}")
        print(f"{'Avg Ratings per User':<30} {len(self.ratings) / self.ratings['userId'].nunique():>20.1f}")
        print(f"{'Avg Ratings per Movie':<30} {len(self.ratings) / self.ratings['movieId'].nunique():>20.1f}")

        # Date range
        self.ratings['datetime'] = pd.to_datetime(self.ratings['timestamp'], unit='s')
        print(f"{'Date Range':<30} {self.ratings['datetime'].min().date()} to")
        print(f"{'':<30} {self.ratings['datetime'].max().date()}")

        # Sparsity
        sparsity = 1 - len(self.ratings) / (
                self.ratings['userId'].nunique() * self.ratings['movieId'].nunique()
        )
        print(f"{'Matrix Sparsity':<30} {sparsity:>19.4%}")
        print("-" * 70)

        return self.ratings, self.movies, self.links

    def filter_sparse_data(self):
        """
        Filter out users/items with too few interactions
        Uses iterative filtering until convergence
        """
        print("\n" + "=" * 70)
        print("Filtering Sparse Data")
        print("=" * 70)
        print(f"Minimum user interactions: {MIN_USER_INTERACTIONS}")
        print(f"Minimum item interactions: {MIN_ITEM_INTERACTIONS}")
        print(f"\nInitial: {len(self.ratings):,} ratings")

        prev_size = 0
        iteration = 0

        while prev_size != len(self.ratings):
            prev_size = len(self.ratings)
            iteration += 1

            # Filter users
            user_counts = self.ratings['userId'].value_counts()
            valid_users = user_counts[user_counts >= MIN_USER_INTERACTIONS].index
            self.ratings = self.ratings[self.ratings['userId'].isin(valid_users)]

            # Filter items
            item_counts = self.ratings['movieId'].value_counts()
            valid_items = item_counts[item_counts >= MIN_ITEM_INTERACTIONS].index
            self.ratings = self.ratings[self.ratings['movieId'].isin(valid_items)]

            print(f"Iteration {iteration}: {len(self.ratings):,} ratings remaining")

            # Safety check
            if iteration > 10:
                print("⚠ Warning: More than 10 iterations, stopping")
                break

        # Update related dataframes
        valid_movies = self.ratings['movieId'].unique()
        self.movies = self.movies[self.movies['movieId'].isin(valid_movies)]
        self.links = self.links[self.links['movieId'].isin(valid_movies)]

        if self.tags is not None:
            self.tags = self.tags[self.tags['movieId'].isin(valid_movies)]

        # Final statistics
        print("\n" + "-" * 70)
        print("Filtered Dataset:")
        print("-" * 70)
        print(f"{'Users':<30} {self.ratings['userId'].nunique():>20,}")
        print(f"{'Movies':<30} {self.ratings['movieId'].nunique():>20,}")
        print(f"{'Ratings':<30} {len(self.ratings):>20,}")
        print(
            f"{'Density':<30} {len(self.ratings) / (self.ratings['userId'].nunique() * self.ratings['movieId'].nunique()):>19.4%}")
        print("-" * 70)

    def create_temporal_split(self):
        """
        Split data temporally into train/val/test
        80% train, 10% val, 10% test
        """
        print("\n" + "=" * 70)
        print("Creating Temporal Train/Val/Test Split")
        print("=" * 70)
        print(f"Ratios: Train={TRAIN_RATIO:.0%}, Val={VAL_RATIO:.0%}, Test={TEST_RATIO:.0%}")

        # Sort by timestamp
        self.ratings = self.ratings.sort_values('timestamp').reset_index(drop=True)

        n = len(self.ratings)
        train_end = int(n * TRAIN_RATIO)
        val_end = int(n * (TRAIN_RATIO + VAL_RATIO))

        self.train = self.ratings.iloc[:train_end].copy()
        self.val = self.ratings.iloc[train_end:val_end].copy()
        self.test = self.ratings.iloc[val_end:].copy()

        # Helper function to get date range
        def get_date_range(df):
            dates = pd.to_datetime(df['timestamp'], unit='s')
            return dates.min().date(), dates.max().date()

        # Display splits
        print("\n" + "-" * 70)
        print(f"{'Split':<15} {'Count':>15} {'Date Range':>35}")
        print("-" * 70)

        train_start, train_end_date = get_date_range(self.train)
        print(f"{'Train':<15} {len(self.train):>15,} {str(train_start):>15} to {str(train_end_date)}")

        val_start, val_end_date = get_date_range(self.val)
        print(f"{'Validation':<15} {len(self.val):>15,} {str(val_start):>15} to {str(val_end_date)}")

        test_start, test_end_date = get_date_range(self.test)
        print(f"{'Test':<15} {len(self.test):>15,} {str(test_start):>15} to {str(test_end_date)}")
        print("-" * 70)

    def create_user_history(self):
        """Create user interaction history for evaluation"""
        print("\nCreating user history mappings...")

        # Create history dictionaries
        train_history = defaultdict(list)
        for _, row in tqdm(self.train.iterrows(), total=len(self.train), desc="Train history"):
            train_history[row['userId']].append(row['movieId'])

        val_history = defaultdict(list)
        for _, row in tqdm(self.val.iterrows(), total=len(self.val), desc="Val history"):
            val_history[row['userId']].append(row['movieId'])

        test_history = defaultdict(list)
        for _, row in tqdm(self.test.iterrows(), total=len(self.test), desc="Test history"):
            test_history[row['userId']].append(row['movieId'])

        # Save
        user_history = {
            'train': dict(train_history),
            'val': dict(val_history),
            'test': dict(test_history)
        }

        with open(PROCESSED_DATA_DIR / "user_history.pkl", 'wb') as f:
            pickle.dump(user_history, f)

        print(f"✓ User history saved ({len(train_history)} users)")

    def create_recbole_format(self):
        """
        Convert to RecBole format (.inter files)
        RecBole requires: user_id:token, item_id:token, rating:float, timestamp:float
        """
        print("\n" + "=" * 70)
        print("Converting to RecBole Format")
        print("=" * 70)

        recbole_dir = PROCESSED_DATA_DIR / "recbole"
        recbole_dir.mkdir(exist_ok=True)

        def save_inter_file(df, filename):
            """Save dataframe in RecBole .inter format"""
            df_recbole = df[['userId', 'movieId', 'rating', 'timestamp']].copy()
            df_recbole.columns = ['user_id:token', 'item_id:token', 'rating:float', 'timestamp:float']
            output_path = recbole_dir / filename
            df_recbole.to_csv(output_path, sep='\t', index=False)
            print(f"✓ Saved {filename} ({len(df_recbole):,} rows)")

        # Save individual splits
        save_inter_file(self.train, 'train.inter')
        save_inter_file(self.val, 'val.inter')
        save_inter_file(self.test, 'test.inter')

        # Save full dataset
        save_inter_file(self.ratings, f'{DATASET_NAME}.inter')

        print(f"\n✓ RecBole format saved to {recbole_dir}")

    def save_processed_data(self):
        """Save all processed data and metadata"""
        print("\n" + "=" * 70)
        print("Saving Processed Data")
        print("=" * 70)

        # Save CSV files
        files_to_save = {
            'train.csv': self.train,
            'val.csv': self.val,
            'test.csv': self.test,
            'movies.csv': self.movies,
            'links.csv': self.links,
        }

        if self.tags is not None:
            files_to_save['tags.csv'] = self.tags

        for filename, df in files_to_save.items():
            output_path = PROCESSED_DATA_DIR / filename
            df.to_csv(output_path, index=False)
            print(f"✓ Saved {filename} ({len(df):,} rows)")

        # Create and save metadata
        metadata = {
            'dataset_name': DATASET_NAME,
            'n_users': int(self.ratings['userId'].nunique()),
            'n_items': int(self.ratings['movieId'].nunique()),
            'n_ratings': int(len(self.ratings)),
            'n_train': int(len(self.train)),
            'n_val': int(len(self.val)),
            'n_test': int(len(self.test)),
            'density': float(
                len(self.ratings) / (self.ratings['userId'].nunique() * self.ratings['movieId'].nunique())),
            'min_user_interactions': MIN_USER_INTERACTIONS,
            'min_item_interactions': MIN_ITEM_INTERACTIONS,
            'train_ratio': TRAIN_RATIO,
            'val_ratio': VAL_RATIO,
            'test_ratio': TEST_RATIO,
            'sample_size': self.sample_size,
            'rating_min': float(self.ratings['rating'].min()),
            'rating_max': float(self.ratings['rating'].max()),
            'rating_mean': float(self.ratings['rating'].mean()),
            'rating_std': float(self.ratings['rating'].std()),
        }

        # Save as pickle
        with open(PROCESSED_DATA_DIR / "metadata.pkl", 'wb') as f:
            pickle.dump(metadata, f)

        # Save as JSON (human-readable)
        with open(PROCESSED_DATA_DIR / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n✓ Metadata saved to {PROCESSED_DATA_DIR}")

        return metadata

    def run_pipeline(self):
        """Run complete preprocessing pipeline"""
        print("\n" + "=" * 70)
        print(f"{'MOVIELENS DATA PREPROCESSING PIPELINE':^70}")
        print("=" * 70)

        try:
            # Run pipeline
            self.load_data()
            self.filter_sparse_data()
            self.create_temporal_split()
            self.create_user_history()
            self.create_recbole_format()
            metadata = self.save_processed_data()

            # Success summary
            print("\n" + "=" * 70)
            print(f"{'✓ PREPROCESSING COMPLETE!':^70}")
            print("=" * 70)
            print(f"\n{'Summary Statistics':^70}")
            print("-" * 70)
            print(f"{'Dataset':<30} {metadata['dataset_name']:>35}")
            print(f"{'Total Users':<30} {metadata['n_users']:>35,}")
            print(f"{'Total Movies':<30} {metadata['n_items']:>35,}")
            print(f"{'Total Ratings':<30} {metadata['n_ratings']:>35,}")
            print(f"{'Train Ratings':<30} {metadata['n_train']:>35,}")
            print(f"{'Validation Ratings':<30} {metadata['n_val']:>35,}")
            print(f"{'Test Ratings':<30} {metadata['n_test']:>35,}")
            print(f"{'Matrix Density':<30} {metadata['density']:>34.4%}")
            print(f"{'Avg Rating':<30} {metadata['rating_mean']:>34.2f}")
            print("-" * 70)
            print(f"\n{'Output Location':<30} {PROCESSED_DATA_DIR}")
            print("=" * 70)

            return metadata

        except Exception as e:
            print(f"\n{'❌ ERROR DURING PREPROCESSING':^70}")
            print("=" * 70)
            print(f"\nError: {str(e)}")
            print("\nPlease check:")
            print("  1. Dataset files are in the correct location")
            print("  2. Files are not corrupted")
            print("  3. You have enough disk space")
            print("  4. You have read/write permissions")
            raise


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Preprocess MovieLens dataset')
    parser.add_argument('--sample', type=int, default=None,
                        help='Sample size for testing (e.g., 1000000)')
    args = parser.parse_args()

    preprocessor = MovieLensPreprocessor(sample_size=args.sample)
    metadata = preprocessor.run_pipeline()

    return metadata


if __name__ == "__main__":
    metadata = main()
