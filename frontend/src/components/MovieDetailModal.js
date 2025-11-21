import React, { useState, useEffect } from 'react';
import { moviesAPI, getImageUrl } from '../api';

const MovieDetailModal = ({ movieId, onClose }) => {
  const [movie, setMovie] = useState(null);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMovie = async () => {
      try {
        const [detailsRes, watchlistRes] = await Promise.all([
          moviesAPI.getMovieDetails(movieId),
          moviesAPI.checkInWatchlist(movieId).catch(() => ({ data: { in_watchlist: false } }))
        ]);

        setMovie(detailsRes.data);
        setInWatchlist(watchlistRes.data.in_watchlist);
      } catch (error) {
        console.error('Error fetching movie:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMovie();
  }, [movieId]);

  const handleWatchlistToggle = async () => {
    try {
      if (inWatchlist) {
        await moviesAPI.removeFromWatchlist(movieId);
        setInWatchlist(false);
      } else {
        await moviesAPI.addToWatchlist(movie);
        setInWatchlist(true);
      }
    } catch (error) {
      console.error('Error updating watchlist:', error);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[2000] p-5" onClick={onClose}>
        <div className="flex justify-center items-center">
          <div className="w-12 h-12 border-4 border-neutral-800 border-t-netflix-red rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!movie) {
    return null;
  }

  const truncate = (str, n) => {
    return str?.length > n ? str.substr(0, n - 1) + '...' : str;
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[2000] p-5" onClick={onClose}>
      <div className="bg-netflix-gray-dark rounded-lg max-w-[850px] w-full max-h-[90vh] overflow-y-auto relative" onClick={(e) => e.stopPropagation()}>
        <button 
          className="absolute top-5 right-5 bg-netflix-gray-dark text-white text-3xl w-10 h-10 rounded-full flex items-center justify-center z-10 hover:bg-neutral-700"
          onClick={onClose}
        >
          ×
        </button>

        <img
          className="w-full h-[480px] object-cover rounded-t-lg"
          src={getImageUrl(movie.backdrop_path || movie.poster_path, 'original')}
          alt={movie.title}
        />

        <div className="p-10">
          <h1 className="text-4xl font-bold mb-4">{movie.title}</h1>

          <div className="flex gap-5 mb-4 text-base text-green-400">
            <span>{movie.vote_average?.toFixed(1)} ★</span>
            <span>{movie.release_date?.split('-')[0]}</span>
            <span>{movie.runtime} min</span>
          </div>

          <div className="flex gap-3 mb-6">
            <button className="px-6 py-3 bg-white text-black rounded text-base font-semibold flex items-center gap-2 hover:bg-white/75 transition-colors">
              ▶ Play
            </button>
            <button
              className="px-6 py-3 bg-neutral-600/70 text-white rounded text-base font-semibold flex items-center gap-2 hover:bg-neutral-600/40 transition-colors"
              onClick={handleWatchlistToggle}
            >
              {inWatchlist ? '✓ In My List' : '+ Add to List'}
            </button>
          </div>

          <p className="text-lg leading-relaxed mb-6">{movie.overview}</p>

          <div className="text-sm leading-relaxed text-neutral-300">
            {movie.genres && (
              <p className="mb-2">
                <span className="text-neutral-500">Genres: </span>
                {movie.genres.map(g => g.name).join(', ')}
              </p>
            )}
            {movie.credits?.cast && (
              <p className="mb-2">
                <span className="text-neutral-500">Cast: </span>
                {truncate(
                  movie.credits.cast.slice(0, 5).map(c => c.name).join(', '),
                  150
                )}
              </p>
            )}
            {movie.credits?.crew && (
              <p className="mb-2">
                <span className="text-neutral-500">Director: </span>
                {movie.credits.crew
                  .filter(c => c.job === 'Director')
                  .map(d => d.name)
                  .join(', ')}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MovieDetailModal;
