import { Link } from 'react-router-dom'
import { Scale, Github, Mail, Shield } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-navy-900 text-gray-400 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <Scale className="w-4 h-4 text-white" />
              </div>
              <span className="text-white font-bold text-lg">
                Legal<span className="text-primary-400">AI</span>
              </span>
            </div>
            <p className="text-sm leading-relaxed max-w-xs">
              AI-powered legal document analysis that helps you understand complex legal language
              in plain English. Protect yourself before you sign.
            </p>
            <div className="flex items-center gap-1 mt-4 text-xs text-gray-500">
              <Shield className="w-3 h-3" />
              <span>Not a substitute for professional legal advice</span>
            </div>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Platform</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/" className="hover:text-white transition-colors">Home</Link></li>
              <li><Link to="/upload" className="hover:text-white transition-colors">Upload Document</Link></li>
              <li><Link to="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
              <li><Link to="/about" className="hover:text-white transition-colors">About</Link></li>
            </ul>
          </div>

          {/* Account */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Account</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/register" className="hover:text-white transition-colors">Create Account</Link></li>
              <li><Link to="/login" className="hover:text-white transition-colors">Sign In</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-navy-800 mt-10 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs">© {new Date().getFullYear()} LegalAI. All rights reserved.</p>
          <p className="text-xs">
            Powered by OpenAI GPT-4 · Built with FastAPI & React
          </p>
        </div>
      </div>
    </footer>
  )
}
