import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import MovieDetailModal from '../components/MovieDetailModal';
import { moviesAPI, getImageUrl } from '../api';

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q');
  const [results, setResults] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      if (!query) return;

      setLoading(true);
      try {
        const res = await moviesAPI.searchMovies(query);
        setResults(res.data.results || []);
      } catch (error) {
        console.error('Error searching movies:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [query]);

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
      
      <h1 className="text-4xl font-bold mb-8">
        Search Results for "{query}"
      </h1>

      {results.length === 0 ? (
        <div className="text-center py-16 text-neutral-500 text-lg">
          <p>No results found for "{query}"</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {results.map((movie) => (
            <img
              key={movie.id}
              className="w-full h-[300px] object-cover rounded cursor-pointer transition-transform hover:scale-105"
              src={getImageUrl(movie.poster_path, 'w500')}
              alt={movie.title}
              onClick={() => setSelectedMovie(movie.id)}
            />
          ))}
        </div>
      )}

      {selectedMovie && (
        <MovieDetailModal
          movieId={selectedMovie}
          onClose={() => setSelectedMovie(null)}
        />
      )}
    </div>
  );
};

export default SearchResults;
