import { Link } from 'react-router-dom'
import {
  Scale, Upload, Brain, FileText, Shield, CheckCircle,
  ArrowRight, Zap, Lock, BarChart3, AlertTriangle
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Analysis',
    desc: 'GPT-4 reads your legal documents and explains them in plain English — no law degree required.',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    icon: Shield,
    title: 'Risk Detection',
    desc: 'Automatically identifies suspicious clauses, unfair conditions, and hidden risks before you sign.',
    color: 'bg-red-100 text-red-600',
  },
  {
    icon: AlertTriangle,
    title: 'Smart Warnings',
    desc: 'Get alerted to missing clauses, payment traps, expiry deadlines, and compliance issues.',
    color: 'bg-yellow-100 text-yellow-600',
  },
  {
    icon: FileText,
    title: 'PDF Reports',
    desc: 'Download a professional PDF report with the full analysis to share with your lawyer or team.',
    color: 'bg-green-100 text-green-600',
  },
  {
    icon: Lock,
    title: 'Secure & Private',
    desc: 'Your documents are protected with JWT authentication and never shared with third parties.',
    color: 'bg-purple-100 text-purple-600',
  },
  {
    icon: BarChart3,
    title: 'Report History',
    desc: 'Access all your previous analyses from your personal dashboard, searchable and filterable.',
    color: 'bg-indigo-100 text-indigo-600',
  },
]

const steps = [
  { num: '01', title: 'Create Account', desc: 'Sign up for free in seconds. No credit card required.' },
  { num: '02', title: 'Upload Document', desc: 'Drag and drop your PDF, DOCX, or image file.' },
  { num: '03', title: 'AI Analyzes', desc: 'Our AI reads and analyzes every clause in seconds.' },
  { num: '04', title: 'Get Your Report', desc: 'Review risks, warnings, and recommendations. Download PDF.' },
]

export default function Home() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="animate-fade-in">
      {/* Hero */}
      <section className="bg-gradient-to-br from-navy-950 via-navy-900 to-primary-900 text-white py-24 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-primary-600/20 border border-primary-500/30 rounded-full px-4 py-1.5 text-primary-300 text-sm font-medium mb-8">
            <Zap className="w-4 h-4" />
            AI-Powered Legal Analysis
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6">
            Understand Legal Documents
            <span className="block text-primary-400 mt-2">Before You Sign</span>
          </h1>
          <p className="text-lg sm:text-xl text-gray-300 max-w-2xl mx-auto mb-10 leading-relaxed">
            Upload any legal document and get an instant AI analysis — risks, warnings,
            suspicious clauses, and recommendations explained in simple English.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            {isAuthenticated ? (
              <Link to="/upload" className="btn-primary text-base px-8 py-4">
                <Upload className="w-5 h-5" />
                Analyze a Document
                <ArrowRight className="w-5 h-5" />
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn-primary text-base px-8 py-4">
                  Get Started Free
                  <ArrowRight className="w-5 h-5" />
                </Link>
                <Link to="/login" className="btn-secondary text-base px-8 py-4 bg-transparent border-white/30 text-white hover:bg-white/10">
                  Sign In
                </Link>
              </>
            )}
          </div>

          {/* Trust indicators */}
          <div className="flex flex-wrap items-center justify-center gap-6 mt-12 text-gray-400 text-sm">
            {['PDF, DOCX & Images', 'Instant Analysis', 'Downloadable Reports', 'Secure & Private'].map((item) => (
              <div key={item} className="flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4 text-green-400" />
                {item}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-navy-800 mb-4">
              Everything You Need to Stay Protected
            </h2>
            <p className="text-gray-500 text-lg max-w-xl mx-auto">
              Our AI does the heavy lifting so you can make informed decisions about your legal documents.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map(({ icon: Icon, title, desc, color }) => (
              <div key={title} className="card hover:shadow-md transition-shadow duration-200 group">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${color}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="font-bold text-gray-900 mb-2">{title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-navy-800 mb-4">How It Works</h2>
            <p className="text-gray-500 text-lg">Get your legal analysis in four simple steps.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map(({ num, title, desc }, i) => (
              <div key={num} className="relative">
                <div className="card text-center h-full">
                  <div className="text-4xl font-extrabold text-primary-100 mb-3">{num}</div>
                  <h3 className="font-bold text-gray-900 mb-2">{title}</h3>
                  <p className="text-gray-500 text-sm">{desc}</p>
                </div>
                {i < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                    <ArrowRight className="w-5 h-5 text-gray-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-gradient-to-r from-primary-700 to-navy-800 text-white">
        <div className="max-w-3xl mx-auto text-center">
          <Scale className="w-14 h-14 mx-auto mb-6 text-primary-300" />
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Don't Sign Without Understanding
          </h2>
          <p className="text-primary-200 text-lg mb-8 max-w-xl mx-auto">
            Join thousands of users who use LegalAI to protect themselves from unfair contracts and hidden risks.
          </p>
          {!isAuthenticated && (
            <Link to="/register" className="inline-flex items-center gap-2 bg-white text-primary-700 font-bold px-8 py-4 rounded-lg hover:bg-primary-50 transition-colors text-base">
              Start Analyzing for Free
              <ArrowRight className="w-5 h-5" />
            </Link>
          )}
          {isAuthenticated && (
            <Link to="/upload" className="inline-flex items-center gap-2 bg-white text-primary-700 font-bold px-8 py-4 rounded-lg hover:bg-primary-50 transition-colors text-base">
              <Upload className="w-5 h-5" />
              Upload a Document
            </Link>
          )}
        </div>
      </section>
    </div>
  )
}
