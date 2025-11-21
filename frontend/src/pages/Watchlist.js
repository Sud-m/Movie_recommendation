import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MovieDetailModal from '../components/MovieDetailModal';
import { moviesAPI, getImageUrl } from '../api';

const Watchlist = () => {
  const [watchlist, setWatchlist] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      const res = await moviesAPI.getWatchlist();
      setWatchlist(res.data.watchlist || []);
    } catch (error) {
      console.error('Error fetching watchlist:', error);
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

  return (
    <div className="min-h-screen pt-[100px] px-[4%]">
      <Navbar />
      
      <h1 className="text-4xl font-bold mb-8">My List</h1>

      {watchlist.length === 0 ? (
        <div className="text-center py-16 text-neutral-500 text-lg">
          <p>Your watchlist is empty.</p>
          <p>Add movies to your list to watch them later!</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {watchlist.map((item) => (
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

      {selectedMovie && (
        <MovieDetailModal
          movieId={selectedMovie}
          onClose={() => {
            setSelectedMovie(null);
            fetchWatchlist(); // Refresh watchlist after modal closes
          }}
        />
      )}
    </div>
  );
};

export default Watchlist;
