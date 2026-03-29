import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MovieDetailModal from '../components/MovieDetailModal';
import { moviesAPI, getImageUrl } from '../api';
import { useAuth } from '../AuthContext';

// Default movies to show as suggestions when watchlist is empty
const DEFAULT_SUGGESTIONS = [
  { id: 1, movie_id: 278, movie_title: "The Shawshank Redemption", movie_poster: "/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg" },
  { id: 2, movie_id: 238, movie_title: "The Godfather", movie_poster: "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg" },
  { id: 3, movie_id: 155, movie_title: "The Dark Knight", movie_poster: "/qJ2tW6WMUDux911r6m7haRef0WH.jpg" },
  { id: 4, movie_id: 550, movie_title: "Fight Club", movie_poster: "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg" },
  { id: 5, movie_id: 680, movie_title: "Pulp Fiction", movie_poster: "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg" },
  { id: 6, movie_id: 13, movie_title: "Forrest Gump", movie_poster: "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg" },
  { id: 7, movie_id: 27205, movie_title: "Inception", movie_poster: "/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg" },
  { id: 8, movie_id: 603, movie_title: "The Matrix", movie_poster: "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg" },
  { id: 9, movie_id: 857, movie_title: "Saving Private Ryan", movie_poster: "/uqx37cS8cpHg8U35f9U5IBlrCV3.jpg" },
  { id: 10, movie_id: 122, movie_title: "The Lord of the Rings: The Return of the King", movie_poster: "/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg" },
];

const Watchlist = () => {
  const { user } = useAuth();
  const [watchlist, setWatchlist] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Only fetch if user is authenticated
    if (user) {
    fetchWatchlist();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchWatchlist = async () => {
    try {
      setError(null);
      const res = await moviesAPI.getWatchlist();
      setWatchlist(res.data.watchlist || []);
    } catch (error) {
      // Only log if it's not an auth error (401/422)
      if (error.response?.status !== 401 && error.response?.status !== 422) {
      console.error('Error fetching watchlist:', error);
        setError('Unable to load your watchlist. Please try again.');
      }
      setWatchlist([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-netflix-black flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-neutral-800 border-t-netflix-red rounded-full animate-spin"></div>
      </div>
    );
  }

  const displayItems = watchlist.length > 0 ? watchlist : [];
  const showSuggestions = watchlist.length === 0;

  return (
    <div className="min-h-screen pt-[100px] px-[4%]">
      <Navbar />
      
      <h1 className="text-4xl font-bold mb-8">My List</h1>

      {error && (
        <div className="bg-red-900/50 border border-red-700 text-red-200 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {displayItems.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-12">
          {displayItems.map((item) => (
            <div
              key={item.id}
              className="cursor-pointer group relative"
              onClick={() => setSelectedMovie(item.movie_id)}
            >
              <img
                className="w-full h-[300px] object-cover rounded transition-transform group-hover:scale-105"
                src={getImageUrl(item.movie_poster, 'w500')}
                alt={item.movie_title}
              />
              {/* Title overlay at bottom of card with hover highlight */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/70 to-transparent rounded-b px-3 py-2 transition-all group-hover:from-black group-hover:via-black/90">
                <p className="text-sm text-white font-medium text-center line-clamp-2 transition-all group-hover:text-base group-hover:font-semibold group-hover:text-white group-hover:drop-shadow-lg">
                  {item.movie_title}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {showSuggestions && (
        <>
          <div className="text-center py-8 text-neutral-400">
            <p className="text-lg mb-2">Your watchlist is empty.</p>
            <p className="text-sm">Click on any movie below to add it to your list!</p>
          </div>

          <h2 className="text-2xl font-semibold mb-6 text-neutral-200">Suggested Movies</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {DEFAULT_SUGGESTIONS.map((item) => (
              <div
                key={item.id}
                className="cursor-pointer group relative"
                onClick={() => setSelectedMovie(item.movie_id)}
              >
                <img
                  className="w-full h-[300px] object-cover rounded transition-transform group-hover:scale-105"
                  src={getImageUrl(item.movie_poster, 'w500')}
                  alt={item.movie_title}
                />
                {/* Title overlay at bottom of card with hover highlight */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/70 to-transparent rounded-b px-3 py-2 transition-all group-hover:from-black group-hover:via-black/90">
                  <p className="text-sm text-white font-medium text-center line-clamp-2 transition-all group-hover:text-base group-hover:font-semibold group-hover:text-white group-hover:drop-shadow-lg">
                    {item.movie_title}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {selectedMovie && (
        <MovieDetailModal
          movieId={selectedMovie}
          onClose={() => {
            setSelectedMovie(null);
            fetchWatchlist(); // Refresh watchlist after modal closes
          }}
          onAddedToList={(createdItem) => {
            // Optimistically add to local state so it appears instantly
            setWatchlist((prev) => {
              const exists = prev.some((i) => i.movie_id === createdItem.movie_id);
              if (exists) return prev;
              return [createdItem, ...prev];
            });
            // Then fetch authoritative list from backend to ensure consistency
            fetchWatchlist();
          }}
          onRemovedFromList={() => {
            fetchWatchlist();
          }}
          onMovieClick={(newMovieId) => setSelectedMovie(newMovieId)}
        />
      )}
    </div>
  );
};

export default Watchlist;
