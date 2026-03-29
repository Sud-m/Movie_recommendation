import React from 'react';

const ExplanationPanel = ({ explanations, graphPaths }) => {
  return (
    <div className="border-t border-neutral-700 bg-neutral-900 p-5 animate-slideDown">
      {/* Full Explanations */}
      <div className="mb-5">
        <h4 className="text-sm font-bold text-neutral-300 mb-3 flex items-center gap-2">
          <svg
            className="w-5 h-5 text-blue-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
          Why This Movie Was Recommended
        </h4>
        <div className="space-y-2.5">
          {explanations.map((explanation, idx) => (
            <div
              key={idx}
              className="flex items-start gap-3 p-3 bg-neutral-800 bg-opacity-50 rounded-lg"
            >
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-600 bg-opacity-20 flex items-center justify-center">
                <svg
                  className="w-4 h-4 text-green-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <p className="text-sm text-neutral-200 flex-1">{explanation}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Knowledge Graph Paths */}
      {graphPaths && graphPaths.length > 0 && (
        <div>
          <h4 className="text-sm font-bold text-neutral-300 mb-3 flex items-center gap-2">
            <svg
              className="w-5 h-5 text-purple-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
            Knowledge Graph Reasoning Paths
          </h4>
          <div className="space-y-2">
            {graphPaths.map((path, idx) => (
              <div
                key={idx}
                className="p-3 bg-purple-900 bg-opacity-20 rounded-lg border border-purple-800 border-opacity-30"
              >
                <div className="flex items-center gap-2 text-sm font-mono">
                  {path.split(' → ').map((node, nodeIdx, array) => (
                    <React.Fragment key={nodeIdx}>
                      <span className="px-2 py-1 bg-purple-600 bg-opacity-30 rounded text-purple-200 font-semibold">
                        {node}
                      </span>
                      {nodeIdx < array.length - 1 && (
                        <svg
                          className="w-4 h-4 text-purple-400 flex-shrink-0"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Footer */}
      <div className="mt-4 p-3 bg-blue-900 bg-opacity-20 rounded-lg border border-blue-800 border-opacity-30">
        <p className="text-xs text-blue-200">
          <strong>Transparent AI:</strong> Every recommendation is backed by
          clear reasoning paths through our knowledge graph, showing exactly why
          this movie matches your preferences.
        </p>
      </div>
    </div>
  );
};

export default ExplanationPanel;

