# GRAFTER-Rec: Graph-Augmented Movie Recommendation System

A full-stack transparent movie recommendation system built with React and Flask, featuring knowledge graph-based semantic reasoning, collaborative filtering, and explainable AI-driven recommendations.

## Features

- 🎯 **Hybrid Recommendation Engine**: Two-stage pipeline combining ItemKNN collaborative filtering with knowledge graph semantic re-ranking
- 🧠 **Knowledge Graph Reasoning**: 31,788 nodes and 301,027 edges encoding movies, genres, tags, and temporal relationships
- 💡 **Explainable Recommendations**: Path-based explanations showing why each movie was recommended
- 🔍 **Advanced Search**: Search movies with multi-criteria filtering and semantic similarity
- 📊 **Performance Analytics**: Real-time visualization of recommendation metrics (NDCG, Recall, Precision, MRR)
- ❄️ **Cold-Start Resilience**: 15.3% improved accuracy for users with limited interaction history
- 🎨 **Interactive UI**: Beautiful, responsive interface with graph visualizations and explanation panels
- ⚡ **Production-Ready**: 68ms average latency per user, real-time inference pipeline

## Tech Stack

### Backend
- **Flask** - Python web framework
- **PostgreSQL** - Relational database for user data and interactions
- **Flask-SQLAlchemy** - ORM for database management
- **Flask-JWT-Extended** - JWT-based authentication
- **TMDB API** - Live movie metadata integration
- **NetworkX** - Knowledge graph construction and traversal
- **Surprise/Scikit-learn** - ItemKNN collaborative filtering implementation
- **NumPy/Pandas** - Data processing and numerical computation

### Frontend
- **React 18** - UI framework
- **React Router v6** - Client-side routing
- **Axios** - HTTP client for API communication
- **Tailwind CSS** - Utility-first styling framework
- **Recharts/D3.js** - Data visualization for metrics and graphs
- **Lucide React** - Icon library

## System Architecture

GRAFTER-Rec implements a **GraphRAG-inspired two-stage recommendation pipeline**:

### Stage 1: Collaborative Filtering (Retrieval)
- **ItemKNN** computes item-item similarity using cosine distance on user-item interaction matrix
- Retrieves top-100 candidate movies based on collaborative signals
- Fast, interpretable, and transparent retrieval (~30ms)

### Stage 2: Knowledge Graph Re-Ranking (Reasoning)
- Semantic traversal through heterogeneous knowledge graph
- Multi-hop reasoning across genres, tags, decades, and content similarity
- Generates semantic compatibility scores and faithful explanations
- Final hybrid scoring: `s_Hybrid(u,c) = α·s_CF(u,c) + (1-α)·s_Graph(u,c)`

**Result**: +6.6% NDCG@10, +12.7% Recall@10, +8.7% Precision@10 vs. strong baselines

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- TMDB API Key (get from https://www.themoviedb.org/settings/api)

## Setup Instructions

### 1. Database Setup

Create a PostgreSQL database:
```bash
# Start PostgreSQL (if not already running)
brew services start postgresql  # macOS
# or
sudo systemctl start postgresql  # Linux

# Create database
createdb grafter_rec

# Or using psql:
psql postgres
CREATE DATABASE grafter_rec;
\q
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd App/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your configuration:
# - DATABASE_URL=postgresql://localhost/grafter_rec
# - TMDB_API_KEY=your_tmdb_api_key_here
# - SECRET_KEY=your-secret-key
# - JWT_SECRET_KEY=your-jwt-secret-key

# Initialize knowledge graph and train models
python scripts/build_knowledge_graph.py
python scripts/train_itemknn.py

# Run the Flask app
python app.py
```

The backend will start on `http://localhost:5000`

### 3. Frontend Setup
```bash
# Open a new terminal
# Navigate to frontend directory
cd App/frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will start on `http://localhost:3000`

## Environment Variables

### Backend (.env)

Create a `.env` file in the `backend` directory:
```env
DATABASE_URL=postgresql://localhost/grafter_rec
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
TMDB_API_KEY=your-tmdb-api-key-here
KG_ALPHA=0.5
GENRE_WEIGHT=3.0
TAG_WEIGHT=1.0
DECADE_WEIGHT=0.5
```

### Get TMDB API Key

1. Go to https://www.themoviedb.org/
2. Create an account
3. Go to Settings > API
4. Request an API key (choose "Developer" option)
5. Copy the API key and add it to your `.env` file

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires auth)

### Recommendations (requires authentication)
- `GET /api/recommendations/personalized` - Get personalized Top-10 recommendations with explanations
- `GET /api/recommendations/cold-start` - Get recommendations for new users
- `POST /api/recommendations/feedback` - Submit recommendation feedback (implicit signals)

### Movies
- `GET /api/movies/trending` - Get trending movies
- `GET /api/movies/popular` - Get popular movies
- `GET /api/movies/search?q=query` - Search movies
- `GET /api/movies/:movieId` - Get movie details with KG context
- `GET /api/movies/:movieId/similar` - Get semantically similar movies via graph traversal

### Interactions (requires authentication)
- `POST /api/interactions` - Record user-movie interaction (view, rate, etc.)
- `GET /api/interactions/history` - Get user's interaction history
- `DELETE /api/interactions/:movieId` - Remove interaction

### Knowledge Graph
- `GET /api/kg/stats` - Get knowledge graph statistics (nodes, edges, degree distribution)
- `GET /api/kg/path/:movieId1/:movieId2` - Get semantic path between two movies
- `GET /api/kg/neighborhood/:movieId` - Get graph neighborhood for visualization

### Analytics
- `GET /api/analytics/metrics` - Get system performance metrics (NDCG, Recall, Precision)
- `GET /api/analytics/coverage` - Get catalog coverage and diversity stats
- `GET /api/analytics/cold-start` - Get cold-start performance breakdown

## Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique email address
- `username` - Unique username
- `password_hash` - Hashed password
- `created_at` - Account creation timestamp
- `interaction_count` - Number of movies rated/viewed

### Interactions Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `movie_id` - TMDB movie ID
- `interaction_type` - Type: 'view', 'rate', 'watchlist'
- `rating` - Optional rating value (1-5)
- `timestamp` - Interaction timestamp

### Knowledge Graph (In-Memory/Graph DB)
- **Movie Nodes**: ID, title, release_year, tmdb_id, popularity
- **Genre Nodes**: ID, name
- **Tag Nodes**: ID, tag_text, frequency
- **Decade Nodes**: ID, decade_range
- **Edges**: HAS_GENRE, HAS_TAG, RELEASED_IN, SIMILAR_TO (with Jaccard weights)

## Usage

### For End Users

1. **Register/Login**: Create an account to start receiving personalized recommendations
2. **Rate Movies**: Interact with movies you've watched to build your profile
3. **Get Recommendations**: View your Top-10 personalized recommendations on the home page
4. **Understand Why**: Click "Show Explanation" to see the knowledge graph reasoning path
5. **Explore Similar**: Click any movie to find semantically similar films via graph traversal
6. **Track Progress**: View your interaction history and recommendation accuracy over time

### For Researchers/Developers

1. **Analyze Performance**: Access `/analytics` to view NDCG, Recall, Precision metrics
2. **Visualize KG**: Explore the knowledge graph structure and node degree distributions
3. **Compare Baselines**: Run ablation studies by adjusting `KG_ALPHA` in `.env`
4. **Cold-Start Testing**: Create new test users with limited interactions to validate robustness
5. **Path Inspection**: Use `/api/kg/path/:id1/:id2` to examine semantic reasoning between movies

## Key Algorithms

### ItemKNN Collaborative Filtering
```python
# Cosine similarity between items i and j
sim(i, j) = (R_i · R_j) / (||R_i|| * ||R_j||)

# Predicted score for user u and candidate c
s_CF(u, c) = Σ(sim(i, c) * R_u,i) / Σ|sim(i, c)|
             for i in user_history
```

### Knowledge Graph Semantic Scoring
```python
# Feature-weighted user profile
F_type_u(v) = |{i ∈ H_u : v ∈ N_type(i)}|

# Semantic compatibility score
s_Graph(u, c) = Σ w_type · (Σ F_type_u(v) / Σ F_type_u(v))
                type       v∈N_type(c)   v∈P_type_u

# Hybrid fusion (α=0.5 optimal)
s_Hybrid(u, c) = α·s_CF(u, c) + (1-α)·s_Graph(u, c)
```

### Explanation Generation
```python
# Find shortest paths in knowledge graph
P_u,i = ∪ ShortestPath(h, i, G) for h in user_history

# Convert to natural language
"Because you enjoyed [Movie A] → shares [Genre] → [Movie B]"
"This matches your interest in [Tag] films from the [Decade] era"
```

## Performance Benchmarks

### Accuracy Metrics (MovieLens-32M, 1000-user sample)

| Model | NDCG@10 | Recall@10 | Precision@10 | MRR |
|-------|---------|-----------|--------------|-----|
| MostPopular | 0.0300 | 0.0030 | 0.0300 | 0.0800 |
| Matrix Factorization | 0.0452 | 0.0055 | 0.0420 | 0.1050 |
| ItemKNN | 0.0484 | 0.0062 | 0.0461 | 0.1117 |
| LightGCN | 0.0501 | 0.0066 | 0.0479 | 0.1165 |
| **GRAFTER-Rec (α=0.5)** | **0.0516** | **0.0070** | **0.0501** | **0.1193** |

**Improvements over ItemKNN**: +6.6% NDCG, +12.7% Recall, +8.7% Precision (p<0.01)

### Cold-Start Performance

| User History Size | NDCG@10 Gain vs. ItemKNN |
|-------------------|---------------------------|
| 10-20 interactions | **+15.3%** |
| 21-50 interactions | +11.8% |
| 51-100 interactions | +8.4% |
| 100+ interactions | +5.9% |

### System Efficiency

- **Latency**: 68ms per user (Stage 1: ~30ms, Stage 2: ~38ms)
- **Memory**: 1.82 GB (KG + models in RAM)
- **Throughput**: ~14 recommendations/second (single thread)
- **Scalability**: Horizontally scalable via candidate pool decoupling

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
pg_isready

# Verify database exists
psql -l | grep grafter_rec

# Test connection
psql grafter_rec
```

### Knowledge Graph Not Loading
```bash
# Rebuild knowledge graph
cd backend
python scripts/build_knowledge_graph.py

# Verify graph file exists
ls -lh data/movie_kg.pkl

# Check graph statistics
python scripts/validate_kg.py
```

### ItemKNN Model Errors
```bash
# Retrain ItemKNN model
cd backend
python scripts/train_itemknn.py

# Verify model file
ls -lh models/itemknn_model.pkl
```

### TMDB API Issues

1. Verify your TMDB API key is correct in `.env`
2. Check rate limits (TMDB: 40 requests/10 seconds)
3. Monitor Flask console for 401/429 error codes

### Port Conflicts

**Frontend:**
```bash
PORT=3001 npm start
```

**Backend:**
Edit `app.py`:
```python
app.run(debug=True, port=5001)
```
## Development Notes

- Knowledge graph is built once and loaded into memory for fast traversal
- ItemKNN similarity matrix is precomputed and cached
- JWT tokens expire after 24 hours (configurable)
- All recommendation scores are normalized to [0,1] before fusion
- Explanation templates are dynamically generated from graph paths
- CORS is enabled for local development

## Future Enhancements

- [ ] Real-time graph updates from streaming user interactions
- [ ] Multi-modal reasoning (posters, trailers, reviews)
- [ ] Federated learning for privacy-preserving personalization
- [ ] A/B testing framework for α parameter optimization
- [ ] Graph Neural Network integration (GCN/GAT) for learned embeddings
- [ ] Cross-domain transfer (books, music, products)
- [ ] Conversational recommendation with LLM integration
- [ ] Advanced fairness metrics (demographic parity, equal opportunity)

## Research & Citations

This project implements the GRAFTER-Rec system described in:

**"GRAFTER-Rec: Graph-Augmented Re-Ranking for Transparent Movie Recommendations"**  
Arya, R., Bhatt, S., Masti, S., Malik, D., & Chinthalapani, S.L.R. (2025)

Key contributions:
1. Hybrid GraphRAG-based architecture for transparent recommendation
2. Large-scale movie knowledge graph with dynamic TMDb integration
3. State-of-the-art performance with path-faithful explanations

## License

This is an academic research project for educational purposes.

## Credits

- **Movie Data**: [The Movie Database (TMDB)](https://www.themoviedb.org/)
- **Dataset**: [MovieLens-32M](https://grouplens.org/datasets/movielens/) by GroupLens Research
- **Research Team**: Arizona State University, School of Computing and Augmented Intelligence

## Contact

For questions, issues, or collaboration inquiries:
- **Project Lead**: Rhythm Arya (rarya124@asu.edu)
- **GitHub Issues**: [Create an issue](https://github.com/your-repo/grafter-rec/issues)

---

**Built with ❤️ for transparent and trustworthy AI**
