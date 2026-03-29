import pandas as pd
import numpy as np
import networkx as nx
import pickle
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

try:
    from config import *
except ImportError:
    from src.config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """Build Knowledge Graph from MovieLens data """

    def __init__(self):
        self.graph = nx.Graph()
        self.movies_df = None
        self.ratings_df = None
        self.tags_df = None
        self.movie_similarities = None

    def load_data(self):
        """Load processed MovieLens data"""
        logger.info("Loading processed data...")

        self.movies_df = pd.read_csv(PROCESSED_DATA_DIR / "movies.csv")
        self.ratings_df = pd.read_csv(PROCESSED_DATA_DIR / "train.csv")

        # Load tags if available
        tags_path = PROCESSED_DATA_DIR / "tags.csv"
        if tags_path.exists():
            self.tags_df = pd.read_csv(tags_path)
            logger.info(f"✓ Loaded {len(self.tags_df):,} tags")

        logger.info(f"✓ Loaded {len(self.movies_df):,} movies")
        logger.info(f"✓ Loaded {len(self.ratings_df):,} ratings")

        return self.movies_df, self.ratings_df

    def extract_genres(self):
        """Extract genre information"""
        logger.info("\nExtracting genres...")

        all_genres = set()
        movie_genres = {}

        for _, row in self.movies_df.iterrows():
            movie_id = row['movieId']
            genres = row['genres'].split('|')
            movie_genres[movie_id] = genres
            all_genres.update(genres)

        # Remove "(no genres listed)"
        all_genres = {g for g in all_genres if g != "(no genres listed)"}

        logger.info(f"✓ Found {len(all_genres)} unique genres")
        return movie_genres, all_genres

    def extract_years(self):
        """Extract release years from titles"""
        logger.info("Extracting release years...")

        import re
        movie_years = {}

        for _, row in self.movies_df.iterrows():
            movie_id = row['movieId']
            title = row['title']

            # Extract year from title (format: "Movie Title (YYYY)")
            match = re.search(r'\((\d{4})\)', title)
            if match:
                year = int(match.group(1))
                movie_years[movie_id] = year

        logger.info(f"✓ Extracted years for {len(movie_years):,} movies")
        return movie_years

    def compute_genre_similarity(self):
        """Compute movie similarities based on genres"""
        logger.info("\nComputing genre-based similarities...")

        # Create genre feature matrix
        movie_ids = self.movies_df['movieId'].tolist()
        genre_features = []

        for _, row in self.movies_df.iterrows():
            genres = row['genres'].split('|')
            genre_features.append(' '.join(genres))

        # TF-IDF on genres
        vectorizer = TfidfVectorizer()
        genre_matrix = vectorizer.fit_transform(genre_features)

        # Compute cosine similarity
        similarity_matrix = cosine_similarity(genre_matrix)

        logger.info("✓ Computed genre similarities")
        return movie_ids, similarity_matrix

    def compute_collaborative_similarity(self, top_k=100):
        """Compute collaborative filtering based similarities"""
        logger.info("\nComputing collaborative filtering similarities...")

        from scipy.sparse import csr_matrix

        # Create user-item matrix
        user_ids = self.ratings_df['userId'].unique()
        movie_ids = self.ratings_df['movieId'].unique()

        user_to_idx = {u: i for i, u in enumerate(user_ids)}
        movie_to_idx = {m: i for i, m in enumerate(movie_ids)}

        rows = self.ratings_df['userId'].map(user_to_idx)
        cols = self.ratings_df['movieId'].map(movie_to_idx)
        data = self.ratings_df['rating'].values

        user_item_matrix = csr_matrix(
            (data, (rows, cols)),
            shape=(len(user_ids), len(movie_ids))
        )

        # Compute item-item similarity
        logger.info("  Computing item-item similarity (this may take a few minutes)...")
        item_similarity = cosine_similarity(user_item_matrix.T, dense_output=False)

        logger.info("✓ Computed collaborative similarities")
        return movie_ids, item_similarity, movie_to_idx

    def process_tags(self):
        """Process user tags if available"""
        if self.tags_df is None:
            return {}

        logger.info("\nProcessing tags...")

        movie_tags = defaultdict(list)

        # Filter out NaN tags first
        valid_tags_df = self.tags_df.dropna(subset=['tag'])

        for _, row in valid_tags_df.iterrows():
            movie_id = row['movieId']
            tag = str(row['tag']).lower().strip()

            # Skip empty or invalid tags
            if tag and tag != 'nan' and len(tag) > 1:
                movie_tags[movie_id].append(tag)

        # Get most common tags per movie
        movie_tag_summary = {}
        for movie_id, tags in movie_tags.items():
            if tags:  # Only include movies with valid tags
                from collections import Counter
                tag_counts = Counter(tags)
                top_tags = [tag for tag, _ in tag_counts.most_common(5)]
                movie_tag_summary[movie_id] = top_tags

        logger.info(f"✓ Processed tags for {len(movie_tag_summary):,} movies")
        return movie_tag_summary

    def build_graph(self, similarity_threshold=0.3, max_similar_movies=20):
        """Build the Knowledge Graph"""
        print("\n" + "=" * 70)
        print("Building Knowledge Graph")
        print("=" * 70)

        # Load data
        self.load_data()

        # Extract features
        movie_genres, all_genres = self.extract_genres()
        movie_years = self.extract_years()
        movie_tags = self.process_tags()

        # Compute similarities
        genre_movie_ids, genre_similarity = self.compute_genre_similarity()
        collab_movie_ids, collab_similarity, movie_to_idx = self.compute_collaborative_similarity()

        # Build graph
        logger.info("\nBuilding graph structure...")

        # 1. Add movie nodes
        for _, row in tqdm(self.movies_df.iterrows(), total=len(self.movies_df), desc="Adding movies"):
            movie_id = row['movieId']
            self.graph.add_node(
                f"movie_{movie_id}",
                type='movie',
                movie_id=movie_id,
                title=row['title'],
                genres=row['genres']
            )

        # 2. Add genre nodes and edges
        for genre in tqdm(all_genres, desc="Adding genres"):
            genre_node = f"genre_{genre}"
            self.graph.add_node(genre_node, type='genre', name=genre)

        for movie_id, genres in tqdm(movie_genres.items(), desc="Linking genres"):
            for genre in genres:
                if genre != "(no genres listed)":
                    self.graph.add_edge(
                        f"movie_{movie_id}",
                        f"genre_{genre}",
                        relation='HAS_GENRE'
                    )

        # 3. Add year nodes (by decade)
        decades = set()
        for movie_id, year in movie_years.items():
            decade = (year // 10) * 10
            decades.add(decade)

        for decade in tqdm(decades, desc="Adding decades"):
            decade_node = f"decade_{decade}s"
            self.graph.add_node(decade_node, type='decade', decade=decade)

        for movie_id, year in tqdm(movie_years.items(), desc="Linking decades"):
            decade = (year // 10) * 10
            self.graph.add_edge(
                f"movie_{movie_id}",
                f"decade_{decade}s",
                relation='RELEASED_IN'
            )

        # 4. Add tag nodes if available
        if movie_tags:
            all_tags = set()
            for tags in movie_tags.values():
                all_tags.update(tags)

            for tag in tqdm(all_tags, desc="Adding tags"):
                tag_node = f"tag_{tag}"
                self.graph.add_node(tag_node, type='tag', name=tag)

            for movie_id, tags in tqdm(movie_tags.items(), desc="Linking tags"):
                for tag in tags:
                    self.graph.add_edge(
                        f"movie_{movie_id}",
                        f"tag_{tag}",
                        relation='HAS_TAG'
                    )

        # 5. Add movie-movie similarity edges (genre-based only)
        logger.info("\nAdding movie similarity edges (genre-based)...")

        similarity_edges = []

        for i, movie_id in enumerate(tqdm(genre_movie_ids, desc="Computing genre similarity")):
            # Get genre similarities
            genre_sims = genre_similarity[i]

            # Get top-k similar movies above threshold
            similar_indices = np.argsort(genre_sims)[::-1][1:max_similar_movies + 1]

            for sim_idx in similar_indices:
                similarity = genre_sims[sim_idx]
                if similarity > similarity_threshold:
                    similar_movie_id = genre_movie_ids[sim_idx]

                    # Avoid duplicate edges
                    if movie_id < similar_movie_id:
                        similarity_edges.append((movie_id, similar_movie_id, similarity))

        logger.info(f"  Found {len(similarity_edges):,} similarity edges")

        # Add similarity edges to graph
        for movie_id1, movie_id2, similarity in tqdm(similarity_edges, desc="Adding similarity edges"):
            self.graph.add_edge(
                f"movie_{movie_id1}",
                f"movie_{movie_id2}",
                relation='SIMILAR_TO',
                weight=float(similarity)
            )
        # Graph statistics
        print("\n" + "=" * 70)
        print("Knowledge Graph Statistics")
        print("=" * 70)
        print(f"{'Total Nodes':<30} {self.graph.number_of_nodes():>20,}")
        print(f"{'Total Edges':<30} {self.graph.number_of_edges():>20,}")

        # Count by type
        node_types = defaultdict(int)
        for node, data in self.graph.nodes(data=True):
            node_types[data['type']] += 1

        print("\nNode Types:")
        for node_type, count in sorted(node_types.items()):
            print(f"  {node_type.capitalize():<28} {count:>20,}")

        # Edge types
        edge_types = defaultdict(int)
        for _, _, data in self.graph.edges(data=True):
            edge_types[data['relation']] += 1

        print("\nEdge Types:")
        for edge_type, count in sorted(edge_types.items()):
            print(f"  {edge_type:<28} {count:>20,}")
        print("=" * 70)

        return self.graph

    def save_graph(self, path=None):
        """Save the knowledge graph"""
        if path is None:
            path = KG_DIR / "movie_kg.gpickle"

        # Use pickle directly instead of nx.write_gpickle
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.graph, f, pickle.HIGHEST_PROTOCOL)

        logger.info(f"\n✓ Knowledge Graph saved to {path}")

        # Also save metadata
        metadata = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'node_types': dict(defaultdict(int)),
            'edge_types': dict(defaultdict(int))
        }

        for node, data in self.graph.nodes(data=True):
            metadata['node_types'][data['type']] = metadata['node_types'].get(data['type'], 0) + 1

        for _, _, data in self.graph.edges(data=True):
            metadata['edge_types'][data['relation']] = metadata['edge_types'].get(data['relation'], 0) + 1

        with open(KG_DIR / "kg_metadata.pkl", 'wb') as f:
            pickle.dump(metadata, f)

        # Save human-readable JSON metadata
        import json
        with open(KG_DIR / "kg_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✓ Metadata saved to {KG_DIR}")

        return path

    @staticmethod
    def load_graph(path=None):
        """Load saved knowledge graph"""
        if path is None:
            path = KG_DIR / "movie_kg.gpickle"

        # Use pickle directly instead of nx.read_gpickle
        import pickle
        with open(path, 'rb') as f:
            graph = pickle.load(f)

        logger.info(f"✓ Loaded Knowledge Graph from {path}")
        logger.info(f"  Nodes: {graph.number_of_nodes():,}")
        logger.info(f"  Edges: {graph.number_of_edges():,}")

        return graph

def main():
    """Main execution"""
    print("\n" + "=" * 70)
    print("Knowledge Graph Construction")
    print("=" * 70)

    builder = KnowledgeGraphBuilder()
    graph = builder.build_graph(
        similarity_threshold=0.3,
        max_similar_movies=20
    )
    builder.save_graph()

    print("\n✓ Knowledge Graph construction complete!")


if __name__ == "__main__":
    main()
