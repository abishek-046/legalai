import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { Scale, Menu, X, LogOut, LayoutDashboard, Upload, User } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
    setMenuOpen(false)
  }

  const navLinkClass = ({ isActive }) =>
    `text-sm font-medium transition-colors duration-200 ${
      isActive ? 'text-primary-400' : 'text-gray-300 hover:text-white'
    }`

  return (
    <nav className="bg-navy-900 border-b border-navy-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 bg-primary-600 rounded-lg flex items-center justify-center group-hover:bg-primary-500 transition-colors">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-white font-bold text-lg">
              Legal<span className="text-primary-400">AI</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6">
            <NavLink to="/" className={navLinkClass} end>Home</NavLink>
            <NavLink to="/about" className={navLinkClass}>About</NavLink>
            {isAuthenticated && (
              <>
                <NavLink to="/upload" className={navLinkClass}>Upload</NavLink>
                <NavLink to="/dashboard" className={navLinkClass}>Dashboard</NavLink>
              </>
            )}
          </div>

          {/* Desktop auth */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-gray-300 text-sm">
                  <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-bold">
                      {user?.name?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <span className="hidden lg:block">{user?.name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-red-400 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </div>
            ) : (
              <>
                <Link to="/login" className="text-sm text-gray-300 hover:text-white transition-colors font-medium">
                  Sign In
                </Link>
                <Link to="/register" className="btn-primary text-sm py-2 px-4">
                  Get Started
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden text-gray-300 hover:text-white"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden bg-navy-900 border-t border-navy-800 px-4 py-4 space-y-3 animate-fade-in">
          <NavLink to="/" className="block text-gray-300 hover:text-white py-2" onClick={() => setMenuOpen(false)} end>Home</NavLink>
          <NavLink to="/about" className="block text-gray-300 hover:text-white py-2" onClick={() => setMenuOpen(false)}>About</NavLink>
          {isAuthenticated ? (
            <>
              <NavLink to="/upload" className="block text-gray-300 hover:text-white py-2" onClick={() => setMenuOpen(false)}>Upload Document</NavLink>
              <NavLink to="/dashboard" className="block text-gray-300 hover:text-white py-2" onClick={() => setMenuOpen(false)}>Dashboard</NavLink>
              <div className="pt-2 border-t border-navy-800">
                <p className="text-gray-400 text-sm mb-2">Signed in as {user?.name}</p>
                <button onClick={handleLogout} className="flex items-center gap-2 text-red-400 hover:text-red-300 text-sm">
                  <LogOut className="w-4 h-4" /> Logout
                </button>
              </div>
            </>
          ) : (
            <div className="pt-2 border-t border-navy-800 flex flex-col gap-2">
              <Link to="/login" className="text-gray-300 hover:text-white py-2" onClick={() => setMenuOpen(false)}>Sign In</Link>
              <Link to="/register" className="btn-primary text-sm py-2 text-center" onClick={() => setMenuOpen(false)}>Get Started</Link>
            </div>
          )}
        </div>
      )}
    </nav>
  )
}
