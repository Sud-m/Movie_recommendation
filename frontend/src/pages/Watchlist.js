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
            <img
              key={item.id}
              className="w-full h-[300px] object-cover rounded cursor-pointer transition-transform hover:scale-105"
              src={getImageUrl(item.movie_poster, 'w500')}
              alt={item.movie_title}
              onClick={() => setSelectedMovie(item.movie_id)}
            />
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
