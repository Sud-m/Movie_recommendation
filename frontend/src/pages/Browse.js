// src/pages/Browse.js
import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MovieRow from '../components/MovieRow';
import MovieDetailModal from '../components/MovieDetailModal';
import CinematchModal from '../components/CinematchModal'; // 👈 NEW
import { moviesAPI, getImageUrl } from '../api';

// Hardcoded Hidden Gems - Critically acclaimed but lesser-known films
const HIDDEN_GEMS = [
  { id: 769, title: "GoodFellas", poster_path: "/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg", backdrop_path: "/sw7mordbZxgITU877yTpZCud90M.jpg", vote_average: 8.5 },
  { id: 11216, title: "Cinema Paradiso", poster_path: "/8SRUfRUi6x4O68n0VCbDNRa6iGL.jpg", backdrop_path: "/gCI2AeMV4IHSewhJkzsur5MEp6R.jpg", vote_average: 8.4 },
  { id: 194, title: "Amélie", poster_path: "/wnUAcUrMRGPPZUDroLeZhSjLkuu.jpg", backdrop_path: "/1IlPZkVD4zcLU8ZxJOHl0DzdZIa.jpg", vote_average: 8.3 },
  { id: 641, title: "Requiem for a Dream", poster_path: "/nOd6vjEmzCT0k4VYqsA2hwyi87C.jpg", backdrop_path: "/dE0SJBnR0XJNA8HhL3hlTIrZ85x.jpg", vote_average: 8.0 },
  { id: 62, title: "2001: A Space Odyssey", poster_path: "/ve72VxNqjGM69Uky4WTo2bK6rfq.jpg", backdrop_path: "/zmmYdPa8Lxx999Af9vnVP4NfqTd.jpg", vote_average: 8.1 },
  { id: 1422, title: "The Departed", poster_path: "/nT97ifVT2J1yMQmeq20Qblg61T.jpg", backdrop_path: "/4dOmT1IcNLaWUOEqkCTmNxqNpkb.jpg", vote_average: 8.2 },
  { id: 1124, title: "The Prestige", poster_path: "/bdN3gXuIZYaJP7ftKK2sU0nPtEA.jpg", backdrop_path: "/c6FfUxzYMEPxJmFVNrjzRAy0Rh1.jpg", vote_average: 8.2 },
  { id: 4935, title: "Howl's Moving Castle", poster_path: "/TkTPELv4kC3u1lkloush8skOjE.jpg", backdrop_path: "/lsdj4S4fetqTXH1gXb3F7QVQZSE.jpg", vote_average: 8.4 },
  { id: 129, title: "Spirited Away", poster_path: "/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg", backdrop_path: "/mSDsSDwaP3E7dEfUPWy4J0djt4O.jpg", vote_average: 8.5 },
  { id: 372058, title: "Your Name", poster_path: "/q719jXXEzOoYaps6babgKnONONX.jpg", backdrop_path: "/dIWwZW7dJJtqC6CgWzYkNVKIUm8.jpg", vote_average: 8.5 },
  { id: 4638, title: "Hot Fuzz", poster_path: "/zPib4ukTSdXvHP9pxGkFCe34oz3.jpg", backdrop_path: "/xHEqM7fTuQJokNzGvIGJNOyL7WU.jpg", vote_average: 7.8 },
  { id: 862, title: "Toy Story", poster_path: "/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg", backdrop_path: "/43PnQR5jjbXNj8Y8R1Fy0Cj5avZ.jpg", vote_average: 8.0 },
];

const Browse = () => {
  const [featuredMovie, setFeaturedMovie] = useState(null);
  const [trending, setTrending] = useState([]);
  const [topRated, setTopRated] = useState([]);
  const [popular, setPopular] = useState([]);
  const [nowPlaying, setNowPlaying] = useState([]);
  const [upcoming, setUpcoming] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [loading, setLoading] = useState(true);

  // 👇 NEW: cinematch modal state
  const [showCinematch, setShowCinematch] = useState(false);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const [
          trendingRes,
          topRatedRes,
          popularRes,
          nowPlayingRes,
          upcomingRes,
        ] = await Promise.all([
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
          const randomMovie =
            trendingData[Math.floor(Math.random() * trendingData.length)];
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

  // All movies we’ll feed into cinematch
  const cinematchMovies = [
    ...trending,
    ...popular,
    ...topRated,
    ...nowPlaying,
    ...upcoming,
  ].filter((m) => m && (m.poster_path || m.backdrop_path));

  return (
    <div className="pt-[70px]">
      <Navbar />

      {/* Hero Banner */}
      {featuredMovie && (
        <div
          className="h-[80vh] bg-cover bg-center relative flex items-center px-[4%]"
          style={{
            backgroundImage: `linear-gradient(to right, rgba(0,0,0,0.8) 0%, transparent 100%), url(${getImageUrl(
              featuredMovie.backdrop_path,
              'original'
            )})`,
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
      
      {/* Hidden Gems Section - Above Trending (Hardcoded curated list) */}
      <div className="mt-5 relative z-20">
        <MovieRow
          title="Hidden Gems 💎"
          subtitle="Critically acclaimed classics & under-the-radar masterpieces"
          movies={HIDDEN_GEMS}
          isLarge={true}
          onMovieClick={(movie) => setSelectedMovie(movie.id)}
        />
      </div>
    

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

      {/* Cinematch - Swipe Game - Future Feature */}
      <div className="my-10 px-[4%]">
        <button
          onClick={() => setShowCinematch(true)}
          className="bg-netflix-red mx-auto italic text-black font-bold px-6 py-3 rounded-lg shadow-md hover:opacity-90 active:scale-95 transition-all flex items-center gap-2"
        >
          Cinematch 🎥
        </button>
      </div>

      {/* Cinematch Modal */}
      {showCinematch && cinematchMovies.length > 0 && (
        <CinematchModal movies={cinematchMovies} onClose={() => setShowCinematch(false)} />
      )}

      {/* Movie Detail Modal */}
      {selectedMovie && (
        <MovieDetailModal
          movieId={selectedMovie}
          onClose={() => setSelectedMovie(null)}
          onMovieClick={(newMovieId) => setSelectedMovie(newMovieId)}
        />
      )}
    </div>
  );
};

export default Browse;
