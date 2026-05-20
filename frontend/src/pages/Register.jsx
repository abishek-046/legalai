import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Scale, User, Mail, Lock, Eye, EyeOff, UserPlus } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'
import { registerUser } from '../services/authService'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Register() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', confirmPassword: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  if (isAuthenticated) { navigate('/dashboard', { replace: true }); return null }

  const validate = () => {
    const e = {}
    if (!form.name.trim()) e.name = 'Name is required'
    else if (form.name.trim().length < 2) e.name = 'Min 2 characters'
    if (!form.email) e.email = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Invalid email'
    if (!form.password) e.password = 'Password is required'
    else if (form.password.length < 6) e.password = 'Min 6 characters'
    if (form.password !== form.confirmPassword) e.confirmPassword = 'Passwords do not match'
    return e
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setLoading(true)
    try {
      const data = await registerUser(form.name.trim(), form.email, form.password)
      login(data.access_token, data.user)
      toast.success(`Welcome to LegalAI, ${data.user.name}!`)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally { setLoading(false) }
  }

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: '' })
  }

  const Field = ({ label, name, type = 'text', placeholder, autoComplete, icon: Icon, extra }) => (
    <div>
      <label className="block text-sm font-medium text-slate-300 mb-1.5">{label}</label>
      <div className="relative">
        <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input type={type} name={name} value={form[name]} onChange={handleChange}
          placeholder={placeholder} autoComplete={autoComplete}
          className={`input-dark pl-10 ${extra || ''} ${errors[name] ? 'ring-1 ring-red-500' : ''}`} />
      </div>
      {errors[name] && <p className="text-red-400 text-xs mt-1">{errors[name]}</p>}
    </div>
  )

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 pt-24"
      style={{ background: 'linear-gradient(135deg, #040d18 0%, #071a2f 100%)' }}>
      <div className="absolute top-1/3 right-1/3 w-96 h-96 rounded-full blur-3xl opacity-10 pointer-events-none"
        style={{ background: 'radial-gradient(circle, #f59e0b, transparent)' }} />

      <div className="w-full max-w-md animate-slide-up relative">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-glow"
            style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
            <Scale className="w-8 h-8 text-dark-600" />
          </div>
          <h1 className="text-2xl font-bold text-white">Create your account</h1>
          <p className="text-slate-400 mt-1 text-sm">Start analyzing legal documents for free</p>
        </div>

        <div className="glass p-8" style={{ background: 'rgba(255,255,255,0.04)' }}>
          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            <Field label="Full Name" name="name" placeholder="John Smith" autoComplete="name" icon={User} />
            <Field label="Email Address" name="email" type="email" placeholder="you@example.com" autoComplete="email" icon={Mail} />
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input type={showPassword ? 'text' : 'password'} name="password" value={form.password}
                  onChange={handleChange} placeholder="Min. 6 characters" autoComplete="new-password"
                  className={`input-dark pl-10 pr-10 ${errors.password ? 'ring-1 ring-red-500' : ''}`} />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password}</p>}
            </div>
            <Field label="Confirm Password" name="confirmPassword"
              type={showPassword ? 'text' : 'password'} placeholder="Repeat your password"
              autoComplete="new-password" icon={Lock} />

            <button type="submit" disabled={loading} className="btn-gold w-full justify-center py-3 mt-2">
              {loading ? <LoadingSpinner size="sm" /> : <><UserPlus className="w-4 h-4" />Create Account</>}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-gold-400 font-semibold hover:text-gold-300 transition-colors">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
