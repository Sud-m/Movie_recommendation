import React from 'react';

const PersonaCard = ({ user, isActive, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`relative p-6 rounded-xl transition-all duration-300 text-left w-full ${
        isActive
          ? 'bg-gradient-to-br from-netflix-red to-red-700 shadow-2xl scale-105 ring-4 ring-netflix-red ring-opacity-50'
          : 'bg-neutral-800 hover:bg-neutral-700 shadow-lg'
      }`}
    >
      <div className="flex items-start gap-4">
        {/* Avatar */}
        <div
          className={`w-16 h-16 rounded-full ${user.avatar_color} flex items-center justify-center text-2xl font-bold flex-shrink-0`}
        >
          {user.name.charAt(0)}
        </div>

        {/* User Info */}
        <div className="flex-1 min-w-0">
          <h3 className="text-xl font-bold mb-1 truncate">{user.name}</h3>
          <p className="text-sm text-neutral-300 mb-2 font-semibold">
            {user.subtitle}
          </p>
          <p className="text-xs text-neutral-400 mb-3">{user.description}</p>
          
          {/* Movie Count Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-black bg-opacity-40 rounded-full">
            <svg
              className="w-4 h-4"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
            </svg>
            <span className="text-xs font-semibold">
              {user.movies_watched} movies watched
            </span>
          </div>
        </div>

        {/* Active Indicator */}
        {isActive && (
          <div className="absolute top-4 right-4">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          </div>
        )}
      </div>
    </button>
  );
};

export default PersonaCard;

