import { Link } from 'react-router-dom'
import {
  Scale, Brain, Shield, Users, Target, CheckCircle,
  ArrowRight, BookOpen, AlertTriangle, Lightbulb
} from 'lucide-react'

const values = [
  {
    icon: Brain,
    title: 'AI-Powered Intelligence',
    desc: 'We use state-of-the-art GPT-4 to analyze legal documents with the depth of an experienced legal analyst.',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    icon: Shield,
    title: 'Protecting Everyday People',
    desc: 'Legal documents are complex by design. We level the playing field so everyone can understand what they\'re signing.',
    color: 'bg-green-100 text-green-600',
  },
  {
    icon: BookOpen,
    title: 'Legal Awareness',
    desc: 'We believe legal literacy is a right, not a privilege. Our mission is to make legal knowledge accessible to all.',
    color: 'bg-purple-100 text-purple-600',
  },
  {
    icon: Target,
    title: 'Accuracy & Reliability',
    desc: 'Our AI is trained to identify specific legal risks, not just summarize. Every analysis is structured and actionable.',
    color: 'bg-orange-100 text-orange-600',
  },
]

const capabilities = [
  'Summarize complex legal language in plain English',
  'Identify suspicious and potentially harmful clauses',
  'Detect missing standard protections',
  'Flag financial and payment risks',
  'Highlight expiry and deadline traps',
  'Spot unfair or one-sided conditions',
  'Assess overall document risk level',
  'Provide actionable recommendations',
  'Generate professional PDF reports',
]

export default function About() {
  return (
    <div className="animate-fade-in">
      {/* Hero */}
      <section className="bg-gradient-to-br from-navy-950 to-navy-900 text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Scale className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold mb-6">
            About <span className="text-primary-400">LegalAI</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
            We're on a mission to democratize legal understanding — making it possible for
            anyone to know exactly what they're agreeing to before they sign.
          </p>
        </div>
      </section>

      {/* Mission */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-navy-800 mb-6">The Problem We're Solving</h2>
              <div className="space-y-4 text-gray-600 leading-relaxed">
                <p>
                  Every day, millions of people sign legal documents they don't fully understand —
                  employment contracts, rental agreements, service terms, NDAs, and more.
                </p>
                <p>
                  Legal language is intentionally complex. Hiring a lawyer for every document
                  is expensive and impractical. The result? People sign away rights they didn't
                  know they had, or agree to terms that could hurt them later.
                </p>
                <p>
                  <strong className="text-navy-800">LegalAI changes that.</strong> We use advanced
                  AI to read your documents and explain them in plain English — identifying risks,
                  flagging suspicious clauses, and giving you the knowledge to make informed decisions.
                </p>
              </div>
            </div>
            <div className="space-y-4">
              {[
                { icon: AlertTriangle, text: 'Hidden clauses that limit your rights', color: 'text-red-500 bg-red-50' },
                { icon: Scale, text: 'One-sided terms that favor the other party', color: 'text-yellow-600 bg-yellow-50' },
                { icon: Lightbulb, text: 'Missing protections you should have', color: 'text-blue-600 bg-blue-50' },
                { icon: CheckCircle, text: 'Clear recommendations before you sign', color: 'text-green-600 bg-green-50' },
              ].map(({ icon: Icon, text, color }) => (
                <div key={text} className={`flex items-center gap-3 p-4 rounded-xl ${color.split(' ')[1]}`}>
                  <Icon className={`w-5 h-5 flex-shrink-0 ${color.split(' ')[0]}`} />
                  <span className="text-gray-700 font-medium">{text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-navy-800 mb-4">Our Core Values</h2>
            <p className="text-gray-500 text-lg">What drives everything we build.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {values.map(({ icon: Icon, title, desc, color }) => (
              <div key={title} className="card">
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

      {/* AI Capabilities */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-navy-800 mb-4">What Our AI Can Do</h2>
            <p className="text-gray-500 text-lg">
              Powered by GPT-4, our AI performs a comprehensive legal analysis on every document.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {capabilities.map((cap) => (
              <div key={cap} className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                <span className="text-gray-700 text-sm">{cap}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="py-16 px-4 bg-navy-900 text-white">
        <div className="max-w-3xl mx-auto text-center">
          <Scale className="w-10 h-10 text-primary-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-4">Important Disclaimer</h2>
          <p className="text-gray-300 leading-relaxed mb-6">
            LegalAI is an AI-powered tool designed to help you understand legal documents.
            It is <strong className="text-white">not a substitute for professional legal advice</strong>.
            Always consult a qualified attorney for important legal matters. Our analysis is
            meant to inform and educate, not to replace expert legal counsel.
          </p>
          <Link to="/register" className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white font-semibold px-6 py-3 rounded-lg transition-colors">
            Start Analyzing Documents
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  )
}
