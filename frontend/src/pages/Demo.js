import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PersonaCard from '../components/demo/PersonaCard';
import DemoRecommendation from '../components/demo/DemoRecommendation';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Debug log
console.log('Demo page loaded');
console.log('API_URL:', API_URL);

const Demo = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  // const [showIntro, setShowIntro] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all demo users on mount
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        console.log('Fetching demo users from:', `${API_URL}/api/demo/users`);
        const response = await axios.get(`${API_URL}/api/demo/users`);
        console.log('Demo users response:', response.data);
        setUsers(response.data.users);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching demo users:', error);
        console.error('Error details:', error.response || error.message);
        setError(`Failed to load demo users: ${error.message}`);
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  // Fetch user profile and recommendations when user is selected
  useEffect(() => {
    if (selectedUser) {
      fetchUserData(selectedUser);
    }
  }, [selectedUser]);

  const fetchUserData = async (userId) => {
    setRecommendationsLoading(true);
    try {
      const [profileRes, recsRes] = await Promise.all([
        axios.get(`${API_URL}/api/demo/user/${userId}`),
        axios.get(`${API_URL}/api/demo/recommendations/${userId}`)
      ]);

      setUserProfile(profileRes.data);
      setRecommendations(recsRes.data.recommendations);
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setRecommendationsLoading(false);
    }
  };

  const handleRateMovie = async (movieId, rating) => {
    if (!selectedUser) return;

    try {
      await axios.post(`${API_URL}/api/demo/rate-movie`, {
        user_id: selectedUser,
        movie_id: movieId,
        rating: rating
      });

      // Refresh recommendations after rating
      setTimeout(() => {
        fetchUserData(selectedUser);
      }, 500);
    } catch (error) {
      console.error('Error rating movie:', error);
    }
  };

  const handleResetUser = async (userId) => {
    try {
      await axios.post(`${API_URL}/api/demo/reset/${userId}`);
      fetchUserData(userId);
    } catch (error) {
      console.error('Error resetting user:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-netflix-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-neutral-800 border-t-netflix-red rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-neutral-400">Loading demo...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-netflix-black flex items-center justify-center p-6">
        <div className="text-center max-w-md">
          <svg className="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Demo</h2>
          <p className="text-neutral-400 mb-4">{error}</p>
          <p className="text-sm text-neutral-500 mb-4">
            Make sure the backend is running on {API_URL}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-netflix-red hover:bg-red-700 rounded-lg font-semibold transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-900 via-netflix-black to-neutral-900">
      {/* Header */}
      <header className="bg-netflix-black border-b border-neutral-800 sticky top-0 z-50 backdrop-blur-lg bg-opacity-90">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span className="text-netflix-red">GRAFTER-Rec</span>
                <span className="text-neutral-400">|</span>
                <span className="text-xl text-neutral-300">Live Demo</span>
              </h1>
              <p className="text-sm text-neutral-400 mt-1">
                Graph-Augmented Re-Ranking for Transparent Movie Recommendations
              </p>
            </div>
            <a
              href="/login"
              className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg transition-colors text-sm font-semibold"
            >
              ← Back to Login
            </a>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Introduction Banner */}
        {/* {showIntro && (
          <div className="mb-8 bg-gradient-to-r from-netflix-red to-red-700 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
            <button
              onClick={() => setShowIntro(false)}
              className="absolute top-4 right-4 w-8 h-8 rounded-full bg-black bg-opacity-30 hover:bg-opacity-50 flex items-center justify-center transition-colors"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
            <div className="pr-12">
              <h2 className="text-2xl font-bold mb-3">
                Welcome to GRAFTER-Rec Live Demonstration
              </h2>
              <p className="text-white text-opacity-95 mb-4 leading-relaxed">
                Today you'll see GRAFTER-Rec in action. We have three users with different tastes. 
                Watch how the system learns, adapts, and most importantly—<strong>EXPLAINS</strong> its reasoning.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="bg-black bg-opacity-20 rounded-lg p-3">
                  <div className="font-bold mb-1">📊 6.6% Better NDCG</div>
                  <div className="text-white text-opacity-80">vs. strong baselines</div>
                </div>
                <div className="bg-black bg-opacity-20 rounded-lg p-3">
                  <div className="font-bold mb-1">❄️ 15.3% Improvement</div>
                  <div className="text-white text-opacity-80">for cold-start users</div>
                </div>
                <div className="bg-black bg-opacity-20 rounded-lg p-3">
                  <div className="font-bold mb-1">⚡ 68ms Latency</div>
                  <div className="text-white text-opacity-80">per recommendation</div>
                </div>
              </div>
            </div>
          </div>
        )} */}

        {/* User Personas Section */}
        <div className="mb-10">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <svg className="w-8 h-8 text-netflix-red" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
            </svg>
            Choose a User Persona
          </h2>
          
          {/* Debug info */}
          {users.length === 0 && (
            <div className="mb-4 p-4 bg-yellow-900 bg-opacity-30 rounded-lg border border-yellow-800">
              <p className="text-yellow-400">⚠️ No users loaded. Check browser console for errors.</p>
              <p className="text-sm text-yellow-300 mt-2">API URL: {API_URL}/api/demo/users</p>
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {users.map((user) => (
              <PersonaCard
                key={user.id}
                user={user}
                isActive={selectedUser === user.id}
                onClick={() => setSelectedUser(user.id)}
              />
            ))}
          </div>
        </div>

        {/* User Profile & Recommendations */}
        {selectedUser && userProfile && (
          <div className="space-y-8">
            {/* User Profile Section */}
            <div className="bg-neutral-800 rounded-xl p-6 shadow-xl">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className={`w-16 h-16 rounded-full ${userProfile.avatar_color} flex items-center justify-center text-3xl font-bold`}>
                    {userProfile.name.charAt(0)}
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold">{userProfile.name}'s Profile</h3>
                    <p className="text-neutral-400">{userProfile.subtitle}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleResetUser(selectedUser)}
                  className="px-4 py-2 bg-neutral-700 hover:bg-neutral-600 rounded-lg transition-colors text-sm font-semibold flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Reset Demo
                </button>
              </div>

              {/* Watched Movies */}
              <div>
                <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5 text-netflix-red" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
                  </svg>
                  Top Rated Movies ({userProfile.total_movies} total)
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                  {userProfile.watched_movies.slice(0, 10).map((movie, idx) => (
                    <div key={idx} className="bg-neutral-900 rounded-lg overflow-hidden hover:scale-105 transition-transform cursor-pointer">
                      {movie.poster_path ? (
                        <img 
                          src={`https://image.tmdb.org/t/p/w300${movie.poster_path}`}
                          alt={movie.title}
                          className="w-full aspect-[2/3] object-cover"
                        />
                      ) : (
                        <div className="w-full aspect-[2/3] bg-neutral-800 flex items-center justify-center">
                          <svg className="w-12 h-12 text-neutral-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                          </svg>
                        </div>
                      )}
                      <div className="p-2">
                        <div className="font-semibold text-xs mb-1 line-clamp-1">
                          {movie.title}
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-neutral-400">{movie.year}</span>
                          <div className="flex items-center gap-0.5">
                            {[...Array(movie.rating)].map((_, i) => (
                              <svg key={i} className="w-3 h-3 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                              </svg>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recommendations Section */}
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold flex items-center gap-3">
                  <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Personalized Recommendations for {userProfile.name}
                </h3>
                {recommendationsLoading && (
                  <div className="flex items-center gap-2 text-neutral-400">
                    <div className="w-5 h-5 border-2 border-neutral-600 border-t-netflix-red rounded-full animate-spin"></div>
                    <span className="text-sm">Updating...</span>
                  </div>
                )}
              </div>

              {recommendations.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {recommendations.map((rec, idx) => (
                    <DemoRecommendation
                      key={rec.id}
                      recommendation={rec}
                      rank={idx + 1}
                      onRate={handleRateMovie}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-neutral-400">
                  <svg className="w-16 h-16 mx-auto mb-4 text-neutral-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p>No recommendations available</p>
                </div>
              )}
            </div>

            {/* Information Footer */}
            <div className="bg-gradient-to-r from-purple-900 to-blue-900 bg-opacity-30 rounded-xl p-6 border border-purple-800 border-opacity-30">
              <h4 className="text-lg font-bold mb-3 flex items-center gap-2">
                <svg className="w-6 h-6 text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                How It Works
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-neutral-200">
                <div>
                  <strong className="text-purple-300">Stage 1: Collaborative Filtering</strong>
                  <p className="mt-1 text-neutral-300">ItemKNN retrieves top-100 candidate movies based on user-item interactions (~30ms)</p>
                </div>
                <div>
                  <strong className="text-purple-300">Stage 2: Knowledge Graph Re-Ranking</strong>
                  <p className="mt-1 text-neutral-300">Semantic traversal through 31K+ nodes to generate explainable scores (~38ms)</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-purple-800 border-opacity-30">
                <p className="text-xs text-neutral-300">
                  <strong>Result:</strong> Every recommendation comes with clear reasoning paths showing exactly why it matches your preferences. 
                  This is transparent, fair, and built to be understood.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!selectedUser && (
          <div className="text-center py-20">
            <svg className="w-24 h-24 mx-auto mb-6 text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 className="text-2xl font-bold text-neutral-400 mb-2">
              Select a User Persona to Begin
            </h3>
            <p className="text-neutral-500">
              Choose Sarah, James, or Emma to see how GRAFTER-Rec adapts to different tastes
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Demo;

