import { useState, useEffect } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { Scale, Menu, X, LogOut, ChevronDown } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleLogout = () => { logout(); navigate('/'); setMenuOpen(false) }

  const navLink = ({ isActive }) =>
    `text-sm font-medium transition-all duration-200 px-3 py-1.5 rounded-lg ${
      isActive
        ? 'text-gold-400 bg-gold-400/10'
        : 'text-slate-400 hover:text-white hover:bg-white/5'
    }`

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled ? 'bg-dark-600/95 backdrop-blur-xl border-b border-white/5 shadow-2xl' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110"
              style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)', boxShadow: '0 4px 15px rgba(245,158,11,0.4)' }}>
              <Scale className="w-5 h-5 text-dark-600" />
            </div>
            <div>
              <span className="text-white font-bold text-lg leading-none">
                Legal<span className="text-gold-gradient">AI</span>
              </span>
            </div>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            <NavLink to="/" className={navLink} end>Home</NavLink>
            <NavLink to="/about" className={navLink}>About</NavLink>
            {isAuthenticated && (
              <>
                <NavLink to="/upload" className={navLink}>Upload</NavLink>
                <NavLink to="/dashboard" className={navLink}>Dashboard</NavLink>
              </>
            )}
          </div>

          {/* Desktop auth */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl"
                  style={{ background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.2)' }}>
                  <div className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-dark-600"
                    style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
                    {user?.name?.charAt(0).toUpperCase()}
                  </div>
                  <span className="text-gold-400 text-sm font-medium hidden lg:block">{user?.name}</span>
                </div>
                <button onClick={handleLogout}
                  className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-red-400 transition-colors px-2 py-1.5 rounded-lg hover:bg-red-400/10">
                  <LogOut className="w-4 h-4" /> Logout
                </button>
              </div>
            ) : (
              <>
                <Link to="/login" className="text-sm text-slate-400 hover:text-white transition-colors font-medium px-3 py-1.5">
                  Sign In
                </Link>
                <Link to="/register" className="btn-gold text-sm py-2 px-5">
                  Get Started
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button className="md:hidden text-slate-400 hover:text-white p-2 rounded-lg hover:bg-white/5"
            onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden border-t border-white/5 px-4 py-4 space-y-1 animate-fade-in"
          style={{ background: 'rgba(4,13,24,0.98)', backdropFilter: 'blur(20px)' }}>
          {[['/', 'Home', true], ['/about', 'About', false]].map(([to, label, end]) => (
            <NavLink key={to} to={to} end={end}
              className="block px-3 py-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-all"
              onClick={() => setMenuOpen(false)}>{label}</NavLink>
          ))}
          {isAuthenticated && (
            <>
              <NavLink to="/upload" className="block px-3 py-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/5" onClick={() => setMenuOpen(false)}>Upload</NavLink>
              <NavLink to="/dashboard" className="block px-3 py-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/5" onClick={() => setMenuOpen(false)}>Dashboard</NavLink>
              <div className="pt-3 mt-3 border-t border-white/5">
                <p className="text-gold-400 text-sm px-3 mb-2">{user?.name}</p>
                <button onClick={handleLogout} className="flex items-center gap-2 text-red-400 text-sm px-3 py-2 rounded-xl hover:bg-red-400/10 w-full">
                  <LogOut className="w-4 h-4" /> Logout
                </button>
              </div>
            </>
          )}
          {!isAuthenticated && (
            <div className="pt-3 mt-3 border-t border-white/5 flex flex-col gap-2">
              <Link to="/login" className="px-3 py-2.5 text-slate-400 hover:text-white" onClick={() => setMenuOpen(false)}>Sign In</Link>
              <Link to="/register" className="btn-gold text-sm py-2.5 text-center" onClick={() => setMenuOpen(false)}>Get Started</Link>
            </div>
          )}
        </div>
      )}
    </nav>
  )
}
