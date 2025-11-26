import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_ML_MODELS_PATH = BASE_DIR / "ml_models"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://localhost/netflix_clone"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "jwt-secret-key-change-in-production"
    )
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    RECOMMENDER_ASSETS_PATH = os.environ.get(
        "RECOMMENDER_ASSETS_PATH", str(DEFAULT_ML_MODELS_PATH)
    )
    RECOMMENDER_CACHE_TTL = int(os.environ.get("RECOMMENDER_CACHE_TTL", "3600"))
