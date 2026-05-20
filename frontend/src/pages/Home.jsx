import { Link } from 'react-router-dom'
import { Scale, Upload, Brain, FileText, Shield, CheckCircle, ArrowRight, Zap, Lock, BarChart3, AlertTriangle, Star } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const features = [
  { icon: Brain, title: 'AI-Powered Analysis', desc: 'GPT-4 reads your legal documents and explains them in plain English.', color: '#38bdf8' },
  { icon: Shield, title: 'Risk Detection', desc: 'Automatically identifies suspicious clauses and hidden risks.', color: '#f87171' },
  { icon: AlertTriangle, title: 'Smart Warnings', desc: 'Get alerted to missing clauses, payment traps, and expiry deadlines.', color: '#fbbf24' },
  { icon: FileText, title: 'PDF Reports', desc: 'Download a professional PDF report with the full analysis.', color: '#4ade80' },
  { icon: Lock, title: 'Secure & Private', desc: 'Your documents are protected with JWT authentication.', color: '#a78bfa' },
  { icon: BarChart3, title: 'Report History', desc: 'Access all your previous analyses from your personal dashboard.', color: '#fb923c' },
]

const steps = [
  { num: '01', title: 'Create Account', desc: 'Sign up for free in seconds.' },
  { num: '02', title: 'Upload Document', desc: 'Drag and drop your PDF or DOCX file.' },
  { num: '03', title: 'AI Analyzes', desc: 'Our AI reads every clause in seconds.' },
  { num: '04', title: 'Get Your Report', desc: 'Review risks and download PDF.' },
]

const stats = [
  { value: '99%', label: 'Accuracy Rate' },
  { value: '<30s', label: 'Analysis Time' },
  { value: '10+', label: 'Risk Categories' },
  { value: 'Free', label: 'To Get Started' },
]

export default function Home() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="animate-fade-in">
      {/* Hero */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16"
        style={{ background: 'linear-gradient(135deg, #040d18 0%, #071a2f 50%, #0a2540 100%)' }}>
        {/* Background elements */}
        <div className="absolute inset-0 hero-pattern opacity-30" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-10"
          style={{ background: 'radial-gradient(circle, #f59e0b, transparent)' }} />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-10"
          style={{ background: 'radial-gradient(circle, #0ea5e9, transparent)' }} />

        <div className="relative max-w-5xl mx-auto px-4 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium mb-8 animate-slide-up"
            style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.3)', color: '#fbbf24' }}>
            <Zap className="w-4 h-4" />
            AI-Powered Legal Analysis Platform
          </div>

          {/* Heading */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold leading-tight mb-6 animate-slide-up"
            style={{ animationDelay: '0.1s' }}>
            <span className="text-white">Understand Legal</span>
            <br />
            <span className="text-gold-gradient">Documents Instantly</span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed animate-slide-up"
            style={{ animationDelay: '0.2s' }}>
            Upload any legal document and get an instant AI analysis — risks, warnings,
            suspicious clauses, and recommendations in simple English.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16 animate-slide-up"
            style={{ animationDelay: '0.3s' }}>
            {isAuthenticated ? (
              <Link to="/upload" className="btn-gold text-base px-8 py-4">
                <Upload className="w-5 h-5" /> Analyze a Document <ArrowRight className="w-5 h-5" />
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn-gold text-base px-8 py-4">
                  Get Started Free <ArrowRight className="w-5 h-5" />
                </Link>
                <Link to="/login" className="btn-outline text-base px-8 py-4">Sign In</Link>
              </>
            )}
          </div>

          {/* Trust badges */}
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-slate-500 animate-slide-up"
            style={{ animationDelay: '0.4s' }}>
            {['PDF & DOCX Support', 'Instant Analysis', 'Downloadable Reports', 'Secure & Private'].map(item => (
              <div key={item} className="flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4 text-gold-400" />{item}
              </div>
            ))}
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-float">
          <div className="w-6 h-10 rounded-full border-2 border-white/20 flex items-start justify-center p-1.5">
            <div className="w-1 h-2 rounded-full bg-gold-400 animate-bounce" />
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-4" style={{ background: '#071a2f' }}>
        <div className="max-w-4xl mx-auto grid grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map(({ value, label }) => (
            <div key={label} className="text-center">
              <div className="text-3xl font-extrabold text-gold-gradient mb-1">{value}</div>
              <div className="text-sm text-slate-500">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-24 px-4" style={{ background: '#040d18' }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Everything You Need to <span className="text-gold-gradient">Stay Protected</span>
            </h2>
            <p className="text-slate-400 text-lg max-w-xl mx-auto">
              Our AI does the heavy lifting so you can make informed decisions.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map(({ icon: Icon, title, desc, color }) => (
              <div key={title} className="glass p-6 hover:border-white/15 transition-all duration-300 group">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"
                  style={{ background: `${color}15`, border: `1px solid ${color}30` }}>
                  <Icon className="w-6 h-6" style={{ color }} />
                </div>
                <h3 className="font-bold text-white mb-2">{title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-24 px-4" style={{ background: '#071a2f' }}>
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">How It <span className="text-gold-gradient">Works</span></h2>
            <p className="text-slate-400 text-lg">Get your legal analysis in four simple steps.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map(({ num, title, desc }, i) => (
              <div key={num} className="relative text-center">
                <div className="glass p-6 h-full">
                  <div className="text-5xl font-extrabold mb-3 text-gold-gradient opacity-40">{num}</div>
                  <h3 className="font-bold text-white mb-2">{title}</h3>
                  <p className="text-slate-400 text-sm">{desc}</p>
                </div>
                {i < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-3 z-10 text-gold-400 opacity-40">
                    <ArrowRight className="w-5 h-5" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-4 relative overflow-hidden" style={{ background: '#040d18' }}>
        <div className="absolute inset-0 opacity-5 hero-pattern" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full blur-3xl opacity-20"
          style={{ background: 'radial-gradient(circle, #f59e0b, transparent)' }} />
        <div className="relative max-w-3xl mx-auto text-center">
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 animate-glow"
            style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
            <Scale className="w-8 h-8 text-dark-600" />
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Don't Sign Without <span className="text-gold-gradient">Understanding</span>
          </h2>
          <p className="text-slate-400 text-lg mb-8 max-w-xl mx-auto">
            Join thousands of users who use LegalAI to protect themselves from unfair contracts.
          </p>
          {!isAuthenticated && (
            <Link to="/register" className="btn-gold text-base px-8 py-4 inline-flex">
              Start Analyzing for Free <ArrowRight className="w-5 h-5" />
            </Link>
          )}
          {isAuthenticated && (
            <Link to="/upload" className="btn-gold text-base px-8 py-4 inline-flex">
              <Upload className="w-5 h-5" /> Upload a Document
            </Link>
          )}
        </div>
      </section>
    </div>
  )
}
