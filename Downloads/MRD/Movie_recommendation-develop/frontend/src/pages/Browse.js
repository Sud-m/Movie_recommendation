import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MovieRow from '../components/MovieRow';
import MovieDetailModal from '../components/MovieDetailModal';
import { moviesAPI, getImageUrl } from '../api';

const Browse = () => {
  const [featuredMovie, setFeaturedMovie] = useState(null);
  const [trending, setTrending] = useState([]);
  const [topRated, setTopRated] = useState([]);
  const [popular, setPopular] = useState([]);
  const [nowPlaying, setNowPlaying] = useState([]);
  const [upcoming, setUpcoming] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const [trendingRes, topRatedRes, popularRes, nowPlayingRes, upcomingRes] = 
          await Promise.all([
            moviesAPI.getTrending(),
            moviesAPI.getTopRated(),
            moviesAPI.getPopular(),
            moviesAPI.getNowPlaying(),
            moviesAPI.getUpcoming(),
          ]);

        const trendingData = trendingRes.data.results || [];
        setTrending(trendingData);
        setTopRated(topRatedRes.data.results || []);
        setPopular(popularRes.data.results || []);
        setNowPlaying(nowPlayingRes.data.results || []);
        setUpcoming(upcomingRes.data.results || []);

        // Set random featured movie from trending
        if (trendingData.length > 0) {
          const randomMovie = trendingData[Math.floor(Math.random() * trendingData.length)];
          setFeaturedMovie(randomMovie);
        }
      } catch (error) {
        console.error('Error fetching movies:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, []);

  const truncate = (str, n) => {
    return str?.length > n ? str.substr(0, n - 1) + '...' : str;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-netflix-black flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-neutral-800 border-t-netflix-red rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="pt-[70px]">
      <Navbar />

      {/* Hero Banner */}
      {featuredMovie && (
        <div
          className="h-[80vh] bg-cover bg-center relative flex items-center px-[4%]"
          style={{
            backgroundImage: `linear-gradient(to right, rgba(0,0,0,0.8) 0%, transparent 100%), url(${getImageUrl(featuredMovie.backdrop_path, 'original')})`,
          }}
        >
          <div className="relative z-10 max-w-[500px]">
            <h1 className="text-5xl font-bold mb-4 drop-shadow-[2px_2px_4px_rgba(0,0,0,0.8)]">
              {featuredMovie.title || featuredMovie.name}
            </h1>
            <p className="text-lg leading-normal mb-6 drop-shadow-[2px_2px_4px_rgba(0,0,0,0.8)]">
              {truncate(featuredMovie.overview, 150)}
            </p>
            <div className="flex gap-3">
              <button className="px-8 py-3 text-base font-semibold bg-white text-black rounded flex items-center gap-2 hover:bg-white/75 transition-all">
                ▶ Play
              </button>
              <button
                className="px-8 py-3 text-base font-semibold bg-neutral-600/70 text-white rounded flex items-center gap-2 hover:bg-neutral-600/40 transition-all"
                onClick={() => setSelectedMovie(featuredMovie.id)}
              >
                ℹ More Info
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Movie Rows */}
      <MovieRow
        title="Trending Now"
        movies={trending}
        isLarge={true}
        onMovieClick={(movie) => setSelectedMovie(movie.id)}
      />
      <MovieRow
        title="Top Rated"
        movies={topRated}
        isLarge={false}
        onMovieClick={(movie) => setSelectedMovie(movie.id)}
      />
      <MovieRow
        title="Popular"
        movies={popular}
        isLarge={false}
        onMovieClick={(movie) => setSelectedMovie(movie.id)}
      />
      <MovieRow
        title="Now Playing"
        movies={nowPlaying}
        isLarge={false}
        onMovieClick={(movie) => setSelectedMovie(movie.id)}
      />
      <MovieRow
        title="Upcoming"
        movies={upcoming}
        isLarge={false}
        onMovieClick={(movie) => setSelectedMovie(movie.id)}
      />

      {/* Movie Detail Modal */}
      {selectedMovie && (
        <MovieDetailModal
          movieId={selectedMovie}
          onClose={() => setSelectedMovie(null)}
        />
      )}
    </div>
  );
};

export default Browse;
