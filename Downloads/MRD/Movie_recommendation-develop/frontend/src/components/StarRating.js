import React, { useState, useEffect } from 'react';

const StarRating = ({ rating, onRatingChange, readOnly = false, size = 'md' }) => {
  const [hoveredRating, setHoveredRating] = useState(0);
  const [displayRating, setDisplayRating] = useState(rating || 0);

  useEffect(() => {
    setDisplayRating(rating || 0);
  }, [rating]);

  const maxRating = 5;
  const starSize = size === 'lg' ? 'w-8 h-8' : size === 'sm' ? 'w-4 h-4' : 'w-6 h-6';
  const starGap = size === 'lg' ? 'gap-1' : 'gap-0.5';

  const handleStarClick = (value, isHalf = false) => {
    if (!readOnly && onRatingChange) {
      const ratingValue = isHalf ? value - 0.5 : value;
      onRatingChange(ratingValue);
      setDisplayRating(ratingValue);
    }
  };

  const handleStarHover = (value, isHalf = false) => {
    if (!readOnly) {
      const ratingValue = isHalf ? value - 0.5 : value;
      setHoveredRating(ratingValue);
    }
  };

  const handleMouseLeave = () => {
    if (!readOnly) {
      setHoveredRating(0);
    }
  };

  const getStarValue = (index) => {
    return index + 1;
  };

  const getStarFill = (index) => {
    const starValue = getStarValue(index);
    const currentRating = hoveredRating || displayRating;
    
    if (currentRating >= starValue) {
      return '100%';
    } else if (currentRating >= starValue - 0.5) {
      return '50%';
    } else {
      return '0%';
    }
  };

  return (
    <div 
      className={`flex items-center ${starGap} ${readOnly ? 'cursor-default' : 'cursor-pointer'}`}
      onMouseLeave={handleMouseLeave}
    >
      {Array.from({ length: maxRating }).map((_, index) => {
        const starValue = getStarValue(index);
        const fillPercentage = getStarFill(index);
        
        return (
          <div
            key={index}
            className={`${starSize} relative ${!readOnly ? 'hover:scale-110 transition-transform' : ''}`}
          >
            <div className="relative w-full h-full">
              {/* Left half for half-star rating */}
              {!readOnly && (
                <div
                  className="absolute left-0 top-0 w-1/2 h-full z-10"
                  onClick={() => handleStarClick(starValue, true)}
                  onMouseEnter={() => handleStarHover(starValue, true)}
                />
              )}
              {/* Right half for full star rating */}
              {!readOnly && (
                <div
                  className="absolute right-0 top-0 w-1/2 h-full z-10"
                  onClick={() => handleStarClick(starValue, false)}
                  onMouseEnter={() => handleStarHover(starValue, false)}
                />
              )}
              <svg
                className="w-full h-full"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <defs>
                  <clipPath id={`half-star-${index}`}>
                    <rect x="0" y="0" width="12" height="24" />
                  </clipPath>
                </defs>
                {/* Empty star background */}
                <path
                  d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                  fill="#4B5563"
                  stroke="#6B7280"
                  strokeWidth="1"
                />
                {/* Filled star foreground */}
                {fillPercentage === '100%' && (
                  <path
                    d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                    fill="#FBBF24"
                  />
                )}
                {fillPercentage === '50%' && (
                  <path
                    d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                    fill="#FBBF24"
                    clipPath={`url(#half-star-${index})`}
                  />
                )}
              </svg>
            </div>
          </div>
        );
      })}
      {displayRating > 0 && (
        <span className="ml-2 text-sm text-neutral-400">
          {displayRating.toFixed(1)}
        </span>
      )}
    </div>
  );
};

export default StarRating;

