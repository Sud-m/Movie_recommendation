import React, { useState } from 'react';
import ExplanationPanel from './ExplanationPanel';

const DemoRecommendation = ({ recommendation, onRate, rank }) => {
  const [showExplanation, setShowExplanation] = useState(false);
  const [selectedRating, setSelectedRating] = useState(null);
  const [imageError, setImageError] = useState(false);

  const handleRate = (rating) => {
    setSelectedRating(rating);
    onRate(recommendation.id, rating);
  };

  const imageUrl = recommendation.poster_path 
    ? `https://image.tmdb.org/t/p/w500${recommendation.poster_path}` 
    : null;

  console.log('Recommendation:', recommendation.title, 'Image URL:', imageUrl);

  return (
    <div className="bg-neutral-800 rounded-xl overflow-hidden shadow-xl transition-all duration-300 hover:shadow-2xl hover:scale-[1.02]">
      {/* Rank Badge */}
      <div className="absolute top-4 left-4 z-10 w-10 h-10 bg-netflix-red rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
        #{rank}
      </div>

      {/* Movie Poster */}
      <div className="relative h-64 bg-neutral-900">
        {imageUrl && !imageError ? (
          <img
            src={imageUrl}
            alt={recommendation.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              console.error('Image failed to load:', imageUrl);
              setImageError(true);
            }}
            onLoad={() => {
              console.log('Image loaded successfully:', imageUrl);
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center flex-col gap-2">
            <svg
              className="w-20 h-20 text-neutral-700"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
            </svg>
            <p className="text-xs text-neutral-600">{recommendation.title}</p>
          </div>
        )}
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-neutral-900 via-transparent to-transparent"></div>
      </div>

      {/* Content */}
      <div className="p-5">
        {/* Title and Year */}
        <div className="mb-3">
          <h3 className="text-xl font-bold mb-1 line-clamp-2">
            {recommendation.title}
          </h3>
          <p className="text-sm text-neutral-400">({recommendation.year})</p>
        </div>

        {/* Match Score */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-neutral-300">
              Match Score
            </span>
            <span className="text-2xl font-bold text-green-400">
              {recommendation.match_score}%
            </span>
          </div>
          <div className="w-full bg-neutral-700 rounded-full h-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-green-500 to-green-400 h-full rounded-full transition-all duration-1000"
              style={{ width: `${recommendation.match_score}%` }}
            ></div>
          </div>
        </div>

        {/* Confidence Badge (if present) */}
        {recommendation.confidence && (
          <div className="mb-3">
            <span className="inline-block px-3 py-1 bg-yellow-600 bg-opacity-20 text-yellow-400 rounded-full text-xs font-bold">
              Confidence: {recommendation.confidence}
            </span>
          </div>
        )}

        {/* Quick Explanations */}
        <div className="mb-4 space-y-2">
          {recommendation.explanations.slice(0, 2).map((explanation, idx) => (
            <div key={idx} className="flex items-start gap-2 text-sm text-neutral-300">
              <svg
                className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="line-clamp-2">{explanation}</span>
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="w-full px-4 py-2.5 bg-neutral-700 hover:bg-neutral-600 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
          >
            <svg
              className={`w-5 h-5 transition-transform ${
                showExplanation ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
            {showExplanation ? 'Hide' : 'Show'} Full Explanation
          </button>

          {/* Rating Buttons */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-neutral-400 font-semibold">Rate:</span>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  onClick={() => handleRate(rating)}
                  className={`w-8 h-8 rounded transition-all ${
                    selectedRating && rating <= selectedRating
                      ? 'text-yellow-400 scale-110'
                      : 'text-neutral-600 hover:text-yellow-400 hover:scale-110'
                  }`}
                >
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Explanation Panel */}
      {showExplanation && (
        <ExplanationPanel
          explanations={recommendation.explanations}
          graphPaths={recommendation.graph_paths}
        />
      )}
    </div>
  );
};

export default DemoRecommendation;

