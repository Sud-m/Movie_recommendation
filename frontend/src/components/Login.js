import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const Login = () => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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

          <input
            type="password"
            className="px-5 py-4 bg-neutral-700 rounded text-white text-base outline-none focus:bg-neutral-600"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength="6"
          />

          <button
            type="submit"
            className="px-4 py-4 bg-netflix-red text-white rounded text-base font-bold mt-6 hover:bg-netflix-red-dark transition-colors disabled:bg-red-900 disabled:cursor-not-allowed"
            disabled={loading}
          >
            {loading ? 'Loading...' : (isRegister ? 'Sign Up' : 'Sign In')}
          </button>

          <div className="text-neutral-500 mt-4 text-base">
            {isRegister ? 'Already have an account?' : 'New to Netflix?'}
            <span
              className="text-white ml-2 cursor-pointer hover:underline"
              onClick={() => {
                setIsRegister(!isRegister);
                setError('');
              }}
            >
              {isRegister ? 'Sign in now' : 'Sign up now'}
            </span>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
