import React from 'react';
import { getImageUrl } from '../api';

const MovieRow = ({ title, movies, isLarge, onMovieClick }) => {
  return (
    <div className="mb-10 px-[4%]">
      <h2 className="text-2xl font-bold mb-4">{title}</h2>
      <div className="flex gap-2 overflow-x-scroll overflow-y-hidden py-5 scrollbar-hide">
        {movies.map((movie) => (
          <img
            key={movie.id}
            className={`object-cover rounded cursor-pointer transition-transform hover:scale-110 flex-shrink-0 ${
              isLarge ? 'w-[250px] h-[350px]' : 'w-[200px] h-[300px]'
            }`}
            src={getImageUrl(
              isLarge ? movie.poster_path : movie.backdrop_path || movie.poster_path,
              isLarge ? 'w500' : 'w300'
            )}
            alt={movie.title || movie.name}
            onClick={() => onMovieClick(movie)}
          />
        ))}
      </div>
    </div>
  );
};

export default MovieRow;
