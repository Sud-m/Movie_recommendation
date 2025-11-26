import React, { useState, useRef } from 'react';
import { getImageUrl } from '../api';

const SWIPE_THRESHOLD = 80; // px

const CinematchModal = ({ movies, onClose }) => {
  const [index, setIndex] = useState(0);
  const [swipeDirection, setSwipeDirection] = useState(null); // 'left' | 'right' | null
  const [dragX, setDragX] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const startXRef = useRef(null);

  const movie = movies[index];

  if (!movie) {
    return null;
  }

  const logSwipe = (direction, movieObj) => {
    if (direction === 'right') {
      console.log('RIGHT SWIPE:', movieObj);
    } else {
      console.log('LEFT SWIPE:', movieObj);
    }
  };

  const advanceCard = () => {
    if (index < movies.length - 1) {
      setIndex((prev) => prev + 1);
      setSwipeDirection(null);
      setDragX(0);
    } else {
      // No more cards
      setSwipeDirection(null);
      setDragX(0);
      onClose();
    }
  };

  const triggerSwipe = (direction) => {
    if (!movie) return;

    logSwipe(direction, movie);
    setSwipeDirection(direction);
    setIsDragging(false);
    setDragX(0);

    // Wait for animation to complete, then show next movie
    setTimeout(() => {
      advanceCard();
    }, 250);
  };

  // Pointer / touch handlers
  const handlePointerDown = (clientX) => {
    startXRef.current = clientX;
    setIsDragging(true);
  };

  const handlePointerMove = (clientX) => {
    if (!isDragging || startXRef.current == null) return;
    const deltaX = clientX - startXRef.current;
    setDragX(deltaX);
  };

  const handlePointerUp = (clientX) => {
    if (!isDragging || startXRef.current == null) {
      setIsDragging(false);
      setDragX(0);
      return;
    }

    const deltaX = clientX - startXRef.current;

    if (deltaX > SWIPE_THRESHOLD) {
      // Swipe right
      triggerSwipe('right');
    } else if (deltaX < -SWIPE_THRESHOLD) {
      // Swipe left
      triggerSwipe('left');
    } else {
      // Not enough swipe, snap back
      setIsDragging(false);
      setDragX(0);
    }

    startXRef.current = null;
  };

  const onMouseDown = (e) => handlePointerDown(e.clientX);
  const onMouseMove = (e) => {
    if (isDragging) {
      e.preventDefault();
      handlePointerMove(e.clientX);
    }
  };
  const onMouseUp = (e) => handlePointerUp(e.clientX);

  const onTouchStart = (e) => {
    const touch = e.touches[0];
    if (touch) handlePointerDown(touch.clientX);
  };

  const onTouchMove = (e) => {
    const touch = e.touches[0];
    if (touch) handlePointerMove(touch.clientX);
  };

  const onTouchEnd = (e) => {
    const touch = e.changedTouches[0];
    if (touch) handlePointerUp(touch.clientX);
  };

  // Card classes + inline transform for drag / animation
  const baseCardClasses = `
    relative w-full h-[400px]
    rounded-xl overflow-hidden shadow-xl bg-black
    transition-transform transition-opacity duration-300 ease-out
  `;

  const directionClasses =
    swipeDirection === 'right'
      ? ' translate-x-[400px] rotate-12 opacity-0'
      : swipeDirection === 'left'
      ? ' -translate-x-[400px] -rotate-12 opacity-0'
      : '';

  const cardStyle =
    !swipeDirection && dragX !== 0
      ? {
          transform: `translateX(${dragX}px) rotate(${dragX / 25}deg)`,
        }
      : undefined;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[3000] p-5">
      <div className="relative bg-netflix-gray-dark p-6 rounded-xl w-[90%] max-w-[500px]">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-white text-3xl hover:text-neutral-300"
        >
          ×
        </button>

        <h2 className="text-xl font-semibold mb-4 text-white">
          Cinematch – Swipe to Train Your Taste
        </h2>

        {/* Card Area */}
        <div
          className={`${baseCardClasses} ${directionClasses}`}
          style={cardStyle}
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
          onMouseLeave={isDragging ? onMouseUp : undefined}
          onTouchStart={onTouchStart}
          onTouchMove={onTouchMove}
          onTouchEnd={onTouchEnd}
        >
          <img
            src={getImageUrl(
              movie.poster_path || movie.backdrop_path,
              'w500'
            )}
            alt={movie.title || movie.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-x-0 bottom-0 p-4 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
            <h3 className="text-lg font-bold text-white">
              {movie.title || movie.name}
            </h3>
          </div>
        </div>

        <p className="mt-3 text-xs text-neutral-400 text-center">
          Swipe the card (or use the buttons) to rate. 
        </p>

        {/* Buttons – for quick desktop testing */}
        <div className="flex justify-between mt-3">
          <button
            onClick={() => triggerSwipe('left')}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            👎 Cut
          </button>
          <button
            onClick={() => triggerSwipe('right')}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            👍 Action
          </button>
        </div>

        
      </div>
    </div>
  );
};

export default CinematchModal;
