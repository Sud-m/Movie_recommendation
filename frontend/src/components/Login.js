import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const Login = () => {
  // eslint-disable-next-line no-unused-vars
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        if (!username.trim()) {
          setError('Username is required');
          setLoading(false);
          return;
        }
        await register(email, username, password);
      } else {
        await login(email, password);
      }
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-cover bg-center"
      style={{
        backgroundImage: `linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://assets.nflxext.com/ffe/siteui/vlv3/9c5457b8-9ab0-4a04-9fc1-e608d5670f1a/710d74e0-7158-408e-8d9b-23c219dee5df/IN-en-20210719-popsignuptwoweeks-perspective_alpha_website_small.jpg')`
      }}
    >
      <div className="bg-black/85 rounded p-16 w-[450px] max-w-[90%]">
        <h1 className="text-3xl font-bold mb-7">
          {isRegister ? 'Sign Up' : 'Sign In'}
        </h1>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {error && (
            <div className="text-orange-600 text-sm mb-2">
              {error}
            </div>
          )}

          <input
            type="email"
            className="px-5 py-4 bg-neutral-700 rounded text-white text-base outline-none focus:bg-neutral-600"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          {isRegister && (
            <input
              type="text"
              className="px-5 py-4 bg-neutral-700 rounded text-white text-base outline-none focus:bg-neutral-600"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          )}

          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              className="px-5 py-4 pr-12 bg-neutral-700 rounded text-white text-base outline-none focus:bg-neutral-600 w-full"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength="6"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-400 hover:text-white transition-colors focus:outline-none"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.29 3.29m0 0A9.97 9.97 0 015.12 5.12m0 0L8.88 8.88M5.12 5.12L3 3m2.12 2.12L8.88 8.88" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          </div>

          <button
            type="submit"
            className="px-4 py-4 bg-netflix-red text-white rounded text-base font-bold mt-6 hover:bg-netflix-red-dark transition-colors disabled:bg-purple-900 disabled:cursor-not-allowed"
            disabled={loading}
          >
            {loading ? 'Loading...' : (isRegister ? 'Sign Up' : 'Sign In')}
          </button>

          <div className="text-neutral-500 mt-4 text-base">
            {/* {isRegister ? 'Already have an account?' : 'New to CSE573 Movie Platform?'} */}
            {/* <span
              className="text-white ml-2 cursor-pointer hover:underline"
              onClick={() => {
                setIsRegister(!isRegister);
                setError('');
              }}
            >
              {isRegister ? 'Sign in now' : 'Sign up now'}
            </span> */}
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
