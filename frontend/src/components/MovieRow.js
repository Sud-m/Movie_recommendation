import React from 'react';
import { getImageUrl } from '../api';

const MovieRow = ({ title, movies, isLarge, onMovieClick }) => {
  return (
    <div className="mb-10 px-[4%]">
      <h2 className="text-2xl font-bold mb-4">{title}</h2>
      <div className="flex gap-2 overflow-x-scroll overflow-y-hidden py-5 scrollbar-hide">
        {movies.map((movie) => (
          <div
            key={movie.id}
            className="flex-shrink-0 cursor-pointer group"
            onClick={() => onMovieClick(movie)}
          >
            <div className="relative">
              <img
                className={`object-cover rounded transition-transform group-hover:scale-110 ${
                  isLarge ? 'w-[250px] h-[350px]' : 'w-[200px] h-[300px]'
                }`}
                src={getImageUrl(
                  isLarge ? movie.poster_path : movie.backdrop_path || movie.poster_path,
                  isLarge ? 'w500' : 'w300'
                )}
                alt={movie.title || movie.name}
              />
              {/* Title overlay at bottom of card with hover highlight */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/70 to-transparent rounded-b px-3 py-2 transition-all group-hover:from-black group-hover:via-black/90">
                <p className="text-sm text-white font-medium text-center line-clamp-2 transition-all group-hover:text-base group-hover:font-semibold group-hover:text-white group-hover:drop-shadow-lg">
                  {movie.title || movie.name}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MovieRow;
