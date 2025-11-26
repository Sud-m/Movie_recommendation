from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Watchlist
from recommender_service import (
    get_recommendation_engine,
    RecommendationError,
    RecommendationDataMissing
)

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")


@recommendations_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_recommendations():
    limit = request.args.get("limit", 10, type=int)
    mode = request.args.get("mode", "hybrid")
    demo_user_id = request.args.get("demo_user_id", type=int)
    movie_context = request.args.get("movie_id", type=int)

    watchlist_items = []
    user_id = get_jwt_identity()
    if user_id:
        watchlist_items = (
            Watchlist.query
            .filter_by(user_id=user_id)
            .order_by(Watchlist.added_at.desc())
            .all()
        )

    try:
        engine = get_recommendation_engine(
            current_app.config["RECOMMENDER_ASSETS_PATH"],
            current_app.config["RECOMMENDER_CACHE_TTL"]
        )
        result = engine.recommend(
            limit=limit,
            mode=mode,
            ml_user_id=demo_user_id,
            watchlist_items=watchlist_items,
            movie_context_tmdb=movie_context
        )
        return jsonify(result), 200
    except RecommendationDataMissing as exc:
        return jsonify({"error": str(exc)}), 503
    except RecommendationError as exc:
        current_app.logger.exception("Recommendation engine error")
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        current_app.logger.exception("Unhandled recommendation failure: %s", exc)
        return jsonify({"error": "Failed to generate recommendations"}), 500
