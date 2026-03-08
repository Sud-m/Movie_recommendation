import React from 'react';
import { getImageUrl } from '../api';

const MovieRow = ({ title, subtitle, movies, isLarge, onMovieClick }) => {
  return (
    <div className="my-10 px-[4%]">
      <h2 className="text-3xl font-bold mb-1">{title}</h2>
      {subtitle && (
        <p className="text-sm text-neutral-400 mb-4">{subtitle}</p>
      )}
      {!subtitle && <div className="mb-3"></div>}
      <div className="flex gap-2 overflow-x-scroll overflow-y-hidden py-5 scrollbar-hide">
        {movies.map((movie) => (
          <div
            key={movie.id}
            className="flex-shrink-0 cursor-pointer group"
            onClick={() => onMovieClick(movie)}
          >
            {/* Card container scales on hover */}
            <div
              className={`
                relative rounded-lg overflow-hidden
                transition-transform duration-300
                group-hover:scale-110
                shadow-lg
                ${isLarge ? 'w-[250px] h-[350px]' : 'w-[200px] h-[300px]'}
              `}
            >
              <img
                className="object-cover w-full h-full"
                src={getImageUrl(
                  isLarge
                    ? movie.poster_path
                    : movie.backdrop_path || movie.poster_path,
                  isLarge ? 'w500' : 'w300'
                )}
                alt={movie.title || movie.name}
              />

              {/* Title overlay at bottom of card with hover highlight */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/70 to-transparent px-3 py-2 transition-all group-hover:from-black group-hover:via-black/90">
                <p className="text-lg text-white font-medium text-center line-clamp-2 transition-all group-hover:text-base group-hover:font-semibold group-hover:text-white group-hover:drop-shadow-lg">
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
