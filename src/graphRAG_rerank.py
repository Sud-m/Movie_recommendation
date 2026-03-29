import numpy as np
import pandas as pd
import networkx as nx
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from tqdm import tqdm
import logging

try:
    from config import *
except ImportError:
    from src.config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphRAGReranker:
    """GraphRAG-based recommendation re-ranker using Knowledge Graph"""

    def __init__(self, kg_path=None, embedding_model=None):
        # Load Knowledge Graph
        if kg_path is None:
            kg_path = KG_DIR / "movie_kg.gpickle"

        logger.info("Loading Knowledge Graph...")
        with open(kg_path, 'rb') as f:
            self.kg = pickle.load(f)
        logger.info(f"✓ Loaded KG: {self.kg.number_of_nodes():,} nodes, {self.kg.number_of_edges():,} edges")

        # Load sentence transformer for embeddings
        if embedding_model is None:
            embedding_model = SENTENCE_TRANSFORMER_MODEL

        logger.info(f"Loading embedding model: {embedding_model}")
        self.encoder = SentenceTransformer(embedding_model)
        logger.info("✓ Embedding model loaded")

        # Load movie metadata
        self.movies_df = pd.read_csv(PROCESSED_DATA_DIR / "movies.csv")
        self.movie_id_to_title = dict(zip(self.movies_df['movieId'], self.movies_df['title']))

        # Cache for embeddings
        self.context_cache = {}

    def retrieve_context(self, movie_id, hops=2, max_items=20):
        """Retrieve context from Knowledge Graph for a movie"""
        # Check cache
        cache_key = f"{movie_id}_{hops}"
        if cache_key in self.context_cache:
            return self.context_cache[cache_key]

        movie_node = f"movie_{movie_id}"

        if movie_node not in self.kg:
            return ""

        # Get movie title
        movie_data = self.kg.nodes.get(movie_node, {})
        title = movie_data.get('title', f'Movie {movie_id}')

        # Collect context from neighbors
        genres = []
        tags = []
        similar_movies = []
        decade = None

        for neighbor in self.kg.neighbors(movie_node):
            neighbor_data = self.kg.nodes[neighbor]
            neighbor_type = neighbor_data.get('type')

            if neighbor_type == 'genre':
                genres.append(neighbor_data.get('name', ''))
            elif neighbor_type == 'tag':
                tags.append(neighbor_data.get('name', ''))
            elif neighbor_type == 'decade':
                decade = f"{neighbor_data.get('decade', '')}s"
            elif neighbor_type == 'movie':
                similar_movies.append(neighbor_data.get('title', ''))

        # Build context string
        context_parts = [f"Movie: {title}"]

        if genres:
            context_parts.append(f"Genres: {', '.join(genres[:5])}")

        if decade:
            context_parts.append(f"Released: {decade}")

        if tags:
            context_parts.append(f"Tags: {', '.join(tags[:10])}")

        if similar_movies:
            context_parts.append(f"Similar to: {', '.join(similar_movies[:5])}")

        context = " | ".join(context_parts)

        # Cache it
        self.context_cache[cache_key] = context

        return context

    def create_user_profile(self, user_history, top_k=20):
        """Create user profile from interaction history"""
        # Get contexts for user's watched movies
        contexts = []
        for movie_id in user_history[:top_k]:
            context = self.retrieve_context(movie_id)
            if context:
                contexts.append(context)

        # Combine contexts
        if not contexts:
            return None

        user_profile_text = " ".join(contexts)
        return user_profile_text

    def compute_graphrag_score(self, user_profile_embedding, candidate_movie_id):
        """Compute GraphRAG relevance score"""
        # Get candidate context
        candidate_context = self.retrieve_context(candidate_movie_id)

        if not candidate_context or user_profile_embedding is None:
            return 0.0

        # Encode candidate
        candidate_embedding = self.encoder.encode([candidate_context])

        # Compute similarity
        similarity = cosine_similarity(user_profile_embedding, candidate_embedding)[0][0]

        return float(similarity)

    def rerank(self, user_id, user_history, candidates, top_k=10,
               alpha=None, apply_diversity=True):
        """
        Re-rank candidates using GraphRAG

        Args:
            user_id: User ID
            user_history: List of movie IDs user has interacted with
            candidates: List of candidate movie IDs to re-rank
            top_k: Number of recommendations to return
            alpha: Popularity penalty weight (default from config)
            apply_diversity: Whether to apply MMR diversity re-ranking
        """
        if alpha is None:
            alpha = ALPHA_POPULARITY_PENALTY

        # Create user profile
        user_profile_text = self.create_user_profile(user_history)

        if user_profile_text is None:
            # Fallback: return candidates as-is
            return candidates[:top_k], [0.0] * min(top_k, len(candidates))

        user_profile_embedding = self.encoder.encode([user_profile_text])

        # Score all candidates
        scored_candidates = []

        for movie_id in tqdm(candidates, desc="Scoring candidates", leave=False):
            # GraphRAG score
            graphrag_score = self.compute_graphrag_score(user_profile_embedding, movie_id)

            # Popularity penalty (optional)
            # For now, skip popularity penalty as we don't have interaction counts easily
            final_score = graphrag_score

            scored_candidates.append((movie_id, final_score))

        # Sort by score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Apply MMR diversity if requested
        if apply_diversity and len(scored_candidates) > top_k:
            recommendations = self._apply_mmr(scored_candidates, top_k,
                                              lambda_param=DIVERSITY_LAMBDA)
        else:
            recommendations = scored_candidates[:top_k]

        # Extract movie IDs and scores
        rec_ids = [movie_id for movie_id, _ in recommendations]
        rec_scores = [score for _, score in recommendations]

        return rec_ids, rec_scores

    def _apply_mmr(self, scored_candidates, top_k, lambda_param=0.5):
        """Apply Maximal Marginal Relevance for diversity"""
        selected = []
        remaining = scored_candidates.copy()

        # Pre-compute embeddings for efficiency
        candidate_embeddings = {}
        for movie_id, _ in scored_candidates[:top_k * 3]:  # Only compute for top candidates
            context = self.retrieve_context(movie_id)
            if context:
                candidate_embeddings[movie_id] = self.encoder.encode([context])[0]

        # Select first item (highest relevance)
        if remaining:
            selected.append(remaining.pop(0))

        # Iteratively select diverse items
        while len(selected) < top_k and remaining:
            best_mmr = -float('inf')
            best_idx = 0

            for idx, (movie_id, relevance) in enumerate(remaining):
                if movie_id not in candidate_embeddings:
                    continue

                # Compute max similarity to already selected
                max_sim = 0.0
                for selected_movie_id, _ in selected:
                    if selected_movie_id in candidate_embeddings:
                        sim = cosine_similarity(
                            [candidate_embeddings[movie_id]],
                            [candidate_embeddings[selected_movie_id]]
                        )[0][0]
                        max_sim = max(max_sim, sim)

                # MMR score
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim

                if mmr_score > best_mmr:
                    best_mmr = mmr_score
                    best_idx = idx

            selected.append(remaining.pop(best_idx))

        return selected


def main():
    """Test GraphRAG reranker"""
    logger.info("\n" + "=" * 70)
    logger.info("GraphRAG Reranker Test")
    logger.info("=" * 70)

    # Initialize
    reranker = GraphRAGReranker()

    # Load user history
    with open(PROCESSED_DATA_DIR / "user_history.pkl", 'rb') as f:
        user_history = pickle.load(f)

    # Find a user with good training history
    logger.info("\nFinding test user with sufficient history...")
    test_user = None
    for user_id, history in user_history['train'].items():
        if len(history) >= 20:  # At least 20 movies
            test_user = user_id
            break

    if test_user is None:
        logger.error("No suitable test user found!")
        return

    user_train_history = user_history['train'][test_user]

    logger.info(f"✓ Test User: {user_id}")
    logger.info(f"  Training history: {len(user_train_history)} movies")

    # Show some movies from history
    movies_df = pd.read_csv(PROCESSED_DATA_DIR / "movies.csv")
    movie_id_to_title = dict(zip(movies_df['movieId'], movies_df['title']))

    logger.info("\n  User's watched movies (sample):")
    for movie_id in user_train_history[:5]:
        title = movie_id_to_title.get(movie_id, f"Movie {movie_id}")
        logger.info(f"    - {title}")

    # Get candidate movies
    all_movies = movies_df['movieId'].tolist()
    candidates = [m for m in all_movies if m not in user_train_history][:100]

    logger.info(f"\n  Candidate pool: {len(candidates)} movies")

    # Rerank
    logger.info(f"\nRe-ranking with GraphRAG...")
    recommendations, scores = reranker.rerank(
        test_user,
        user_train_history,
        candidates,
        top_k=10
    )

    # Display results
    logger.info("\n" + "=" * 70)
    logger.info("Top 10 GraphRAG Recommendations:")
    logger.info("=" * 70)

    for i, (movie_id, score) in enumerate(zip(recommendations, scores), 1):
        title = movie_id_to_title.get(movie_id, f"Movie {movie_id}")
        genres = movies_df[movies_df['movieId'] == movie_id]['genres'].values
        genre_str = genres[0] if len(genres) > 0 else "Unknown"
        logger.info(f"{i:2d}. {title[:45]:<45} [{genre_str[:20]:<20}] (score: {score:.4f})")

    logger.info("=" * 70)
    logger.info("✓ GraphRAG test complete")


if __name__ == "__main__":
    main()
