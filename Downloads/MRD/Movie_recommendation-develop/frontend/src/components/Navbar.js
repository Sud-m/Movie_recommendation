import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 100);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <nav className={`fixed top-0 w-full h-[70px] flex justify-between items-center px-[4%] z-50 transition-colors duration-300 ${
      scrolled ? 'bg-netflix-black' : 'bg-gradient-to-b from-black/70 to-transparent'
    }`}>
      <div className="flex items-center gap-8">
        <Link to="/" className="text-netflix-red text-3xl font-black tracking-wider">
          NETFLIX
        </Link>
        <div className="hidden md:flex gap-5">
          <Link to="/" className="text-gray-200 text-sm hover:text-gray-400 transition-colors">
            Home
          </Link>
          <Link to="/watchlist" className="text-gray-200 text-sm hover:text-gray-400 transition-colors">
            My List
          </Link>
        </div>
      </div>

      <div className="flex items-center gap-5">
        <form onSubmit={handleSearch} className="flex items-center">
          <input
            type="text"
            className="px-3 py-2 bg-black/75 border border-white text-white rounded outline-none"
            placeholder="Search movies..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-netflix-red flex items-center justify-center font-bold">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <button 
            onClick={logout} 
            className="px-4 py-2 bg-netflix-red text-white rounded text-sm hover:bg-netflix-red-dark transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
