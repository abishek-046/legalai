import { Link } from 'react-router-dom'
import { Scale, Shield, Github } from 'lucide-react'

export default function Footer() {
  return (
    <footer style={{ background: '#040d18', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
                <Scale className="w-5 h-5 text-dark-600" />
              </div>
              <span className="text-white font-bold text-lg">Legal<span className="text-gold-gradient">AI</span></span>
            </div>
            <p className="text-slate-500 text-sm leading-relaxed max-w-xs">
              AI-powered legal document analysis. Understand complex legal language in plain English before you sign.
            </p>
            <div className="flex items-center gap-1.5 mt-4 text-xs text-slate-600">
              <Shield className="w-3 h-3" />
              <span>Not a substitute for professional legal advice</span>
            </div>
          </div>
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Platform</h4>
            <ul className="space-y-2.5 text-sm text-slate-500">
              {[['/', 'Home'], ['/upload', 'Upload Document'], ['/dashboard', 'Dashboard'], ['/about', 'About']].map(([to, label]) => (
                <li key={to}><Link to={to} className="hover:text-gold-400 transition-colors">{label}</Link></li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Account</h4>
            <ul className="space-y-2.5 text-sm text-slate-500">
              <li><Link to="/register" className="hover:text-gold-400 transition-colors">Create Account</Link></li>
              <li><Link to="/login" className="hover:text-gold-400 transition-colors">Sign In</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-10 pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-600">© {new Date().getFullYear()} LegalAI. All rights reserved.</p>
          <p className="text-xs text-slate-600">Powered by OpenAI GPT-4 · FastAPI · React · Supabase</p>
        </div>
      </div>
    </footer>
  )
}
