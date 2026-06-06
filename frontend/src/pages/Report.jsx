import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Download, FileText, Calendar, CheckCircle, XCircle,
  AlertTriangle, Search, DollarSign, Clock, Scale, Lightbulb,
  ShieldAlert, Trash2, Shield, Eye, Lock, Zap, Target,
  AlertCircle, Star, TrendingUp, FileWarning
} from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import { getReport, downloadReportPdf, deleteReport } from '../services/documentService'
import LoadingSpinner from '../components/LoadingSpinner'

// ── Status Badge ────────────────────────────────────────────────────────────
function StatusBadge({ status }) {
  const cfg = {
    Legal:         { bg: 'rgba(74,222,128,0.12)', border: 'rgba(74,222,128,0.3)',  text: '#4ade80', icon: CheckCircle,  label: 'LEGAL' },
    Illegal:       { bg: 'rgba(239,68,68,0.12)',  border: 'rgba(239,68,68,0.3)',   text: '#f87171', icon: XCircle,      label: 'ILLEGAL' },
    'Needs Review':{ bg: 'rgba(251,191,36,0.12)', border: 'rgba(251,191,36,0.3)',  text: '#fbbf24', icon: AlertTriangle, label: 'NEEDS REVIEW' },
  }
  const c = cfg[status] || cfg['Needs Review']
  const Icon = c.icon
  return (
    <div className="flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-sm"
      style={{ background: c.bg, border: `1px solid ${c.border}`, color: c.text }}>
      <Icon className="w-4 h-4" />
      {c.label}
    </div>
  )
}

// ── Risk Badge ───────────────────────────────────────────────────────────────
function RiskBadge({ level }) {
  const cfg = {
    Low:    { bg: 'rgba(74,222,128,0.12)',  border: 'rgba(74,222,128,0.3)',  text: '#4ade80' },
    Medium: { bg: 'rgba(251,191,36,0.12)',  border: 'rgba(251,191,36,0.3)',  text: '#fbbf24' },
    High:   { bg: 'rgba(239,68,68,0.12)',   border: 'rgba(239,68,68,0.3)',   text: '#f87171' },
  }
  const c = cfg[level] || cfg.Medium
  return (
    <span className="px-3 py-1 rounded-full text-sm font-bold"
      style={{ background: c.bg, border: `1px solid ${c.border}`, color: c.text }}>
      {level} Risk
    </span>
  )
}

// ── Confidence Meter ─────────────────────────────────────────────────────────
function ConfidenceMeter({ score }) {
  const color = score >= 75 ? '#4ade80' : score >= 50 ? '#fbbf24' : '#f87171'
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
        <div className="h-2 rounded-full transition-all duration-700"
          style={{ width: `${score}%`, background: `linear-gradient(90deg, ${color}, ${color}aa)` }} />
      </div>
      <span className="text-sm font-bold" style={{ color }}>{score}%</span>
    </div>
  )
}

// ── Section ──────────────────────────────────────────────────────────────────
function Section({ icon: Icon, title, items, accentColor = '#94a3b8', numbered = false }) {
  if (!items || items.length === 0) return null
  return (
    <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="flex items-center gap-2 font-bold text-white text-sm">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: `${accentColor}18`, border: `1px solid ${accentColor}30` }}>
            <Icon className="w-4 h-4" style={{ color: accentColor }} />
          </div>
          {title}
        </h3>
        <span className="text-xs px-2 py-0.5 rounded-full font-medium"
          style={{ background: `${accentColor}15`, color: accentColor, border: `1px solid ${accentColor}25` }}>
          {items.length}
        </span>
      </div>
      <ul className="space-y-2.5">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2.5 text-sm text-slate-300">
            <span className="mt-1.5 text-xs font-bold flex-shrink-0 w-4" style={{ color: accentColor }}>
              {numbered ? `${i + 1}.` : '•'}
            </span>
            <span className="leading-relaxed">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

// ── Divider Header ────────────────────────────────────────────────────────────
function DividerHeader({ title }) {
  return (
    <div className="flex items-center gap-3 my-6">
      <div className="flex-1 h-px" style={{ background: 'rgba(251,191,36,0.2)' }} />
      <span className="text-xs font-bold tracking-widest text-gold-400 px-2">{title}</span>
      <div className="flex-1 h-px" style={{ background: 'rgba(251,191,36,0.2)' }} />
    </div>
  )
}

// ── Main Report ───────────────────────────────────────────────────────────────
export default function Report() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    getReport(id)
      .then(setReport)
      .catch(() => { toast.error('Report not found'); navigate('/dashboard') })
      .finally(() => setLoading(false))
  }, [id, navigate])

  const handleDownload = async () => {
    setDownloading(true)
    try { await downloadReportPdf(id, report.filename); toast.success('PDF downloaded') }
    catch { toast.error('Download failed') }
    finally { setDownloading(false) }
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this report? This cannot be undone.')) return
    setDeleting(true)
    try { await deleteReport(id); toast.success('Report deleted'); navigate('/dashboard') }
    catch { toast.error('Delete failed'); setDeleting(false) }
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#040d18' }}>
      <LoadingSpinner size="lg" text="Loading report..." />
    </div>
  )
  if (!report) return null

  const date = report.createdAt
    ? format(new Date(report.createdAt), "MMMM d, yyyy 'at' HH:mm")
    : 'Unknown date'

  const status = report.documentStatus || 'Needs Review'
  const confidence = report.confidenceScore ?? 0

  return (
    <div className="min-h-screen pt-20 pb-16" style={{ background: '#040d18' }}>
      <div className="max-w-4xl mx-auto px-4">

        {/* Back */}
        <Link to="/dashboard"
          className="inline-flex items-center gap-1.5 text-slate-500 hover:text-gold-400 text-sm mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>

        {/* ── DOCUMENT STATUS ── */}
        <DividerHeader title="DOCUMENT STATUS" />

        <div className="glass p-6 mb-4" style={{ background: 'rgba(255,255,255,0.03)' }}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
            <div className="flex items-start gap-3">
              <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
                style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.2)' }}>
                <FileText className="w-6 h-6 text-gold-400" />
              </div>
              <div>
                <h1 className="font-bold text-white text-lg break-all">{report.filename}</h1>
                <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                  <span>{report.documentType}</span>
                  <span>•</span>
                  <Calendar className="w-3 h-3" />
                  <span>{date}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={handleDownload} disabled={downloading}
                className="btn-outline text-sm py-2 px-4">
                <Download className="w-4 h-4" />
                {downloading ? 'Downloading...' : 'PDF Report'}
              </button>
              <button onClick={handleDelete} disabled={deleting}
                className="p-2 rounded-xl text-slate-500 hover:text-red-400 hover:bg-red-400/10 transition-all"
                aria-label="Delete">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Status row */}
          <div className="flex flex-wrap items-center gap-4 pt-4 border-t border-white/5">
            <StatusBadge status={status} />
            <RiskBadge level={report.riskLevel || 'Medium'} />
            {report.safeToSign ? (
              <span className="flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-xl"
                style={{ background: 'rgba(74,222,128,0.1)', border: '1px solid rgba(74,222,128,0.3)', color: '#4ade80' }}>
                <CheckCircle className="w-3.5 h-3.5" /> Safe to Sign
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-xl"
                style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}>
                <XCircle className="w-3.5 h-3.5" /> Do Not Sign Yet
              </span>
            )}
          </div>

          {/* Confidence */}
          <div className="mt-4 pt-4 border-t border-white/5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-slate-500 font-medium">Analysis Confidence Score</span>
              <span className="text-xs text-slate-500">{confidence}%</span>
            </div>
            <ConfidenceMeter score={confidence} />
          </div>
        </div>

        {/* ── SIMPLE SUMMARY ── */}
        <DividerHeader title="SIMPLE SUMMARY" />
        {report.summary && (
          <div className="glass p-5 mb-4" style={{ background: 'rgba(255,255,255,0.03)' }}>
            <p className="text-slate-300 leading-relaxed text-sm">{report.summary}</p>
          </div>
        )}

        {/* ── RISK LEVEL ── */}
        <DividerHeader title="RISK LEVEL" />
        <div className="glass p-5 mb-4" style={{ background: 'rgba(255,255,255,0.03)' }}>
          <div className="flex items-center gap-3 mb-3">
            <RiskBadge level={report.riskLevel || 'Medium'} />
          </div>
          {report.riskReason && (
            <div>
              <p className="text-xs font-semibold text-slate-500 mb-1">Reason:</p>
              <p className="text-slate-300 text-sm leading-relaxed">{report.riskReason}</p>
            </div>
          )}
        </div>

        {/* ── DOCUMENT ISSUES ── */}
        {report.documentIssues?.length > 0 && (
          <>
            <DividerHeader title="DOCUMENT ISSUES FOUND" />
            <Section icon={FileWarning} title="Document Issues & Mistakes"
              items={report.documentIssues} accentColor="#fb923c" numbered />
          </>
        )}

        {/* ── ANALYSIS SECTIONS ── */}
        <DividerHeader title="DETAILED ANALYSIS" />
        <div className="space-y-3">
          <Section icon={Search}      title="Suspicious Clauses"        items={report.suspiciousClauses}  accentColor="#f87171" numbered />
          <Section icon={ShieldAlert} title="Missing Clauses"           items={report.missingClauses}     accentColor="#fb923c" numbered />
          <Section icon={DollarSign}  title="Financial & Payment Risks" items={report.financialRisks}     accentColor="#fbbf24" numbered />
          <Section icon={Clock}       title="Expiry & Deadline Risks"   items={report.expiryRisks}        accentColor="#a78bfa" numbered />
          <Section icon={Scale}       title="Unfair Conditions"         items={report.unfairConditions}   accentColor="#f87171" numbered />
          <Section icon={Shield}      title="Compliance Issues"         items={report.complianceIssues}   accentColor="#38bdf8" numbered />
          <Section icon={Lock}        title="Privacy Risks"             items={report.privacyRisks}       accentColor="#c084fc" numbered />
          <Section icon={Eye}         title="Legal Loopholes"           items={report.legalLoopholes}     accentColor="#fb923c" numbered />
          <Section icon={AlertTriangle} title="Important Warnings"      items={report.warnings}           accentColor="#fbbf24" numbered />
        </div>

        {/* ── RECOMMENDATIONS ── */}
        {report.recommendations?.length > 0 && (
          <>
            <DividerHeader title="RECOMMENDATIONS" />
            <div className="rounded-2xl p-5" style={{ background: 'rgba(74,222,128,0.05)', border: '1px solid rgba(74,222,128,0.15)' }}>
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-5 h-5 text-green-400" />
                <h3 className="font-bold text-white text-sm">Practical Legal Recommendations</h3>
              </div>
              <ul className="space-y-2.5">
                {report.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-sm text-slate-300">
                    <span className="mt-0.5 text-green-400 font-bold flex-shrink-0">→</span>
                    <span className="leading-relaxed">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}

        {/* ── FINAL VERDICT ── */}
        <DividerHeader title="FINAL VERDICT" />
        <div className="rounded-2xl p-6 mb-8"
          style={{
            background: report.safeToSign
              ? 'rgba(74,222,128,0.06)'
              : 'rgba(239,68,68,0.06)',
            border: `1px solid ${report.safeToSign ? 'rgba(74,222,128,0.2)' : 'rgba(239,68,68,0.2)'}`,
          }}>
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
              style={{
                background: report.safeToSign ? 'rgba(74,222,128,0.15)' : 'rgba(239,68,68,0.15)',
              }}>
              {report.safeToSign
                ? <CheckCircle className="w-5 h-5 text-green-400" />
                : <AlertCircle className="w-5 h-5 text-red-400" />}
            </div>
            <div>
              <p className="font-bold mb-2" style={{ color: report.safeToSign ? '#4ade80' : '#f87171' }}>
                {report.safeToSign ? 'You may proceed with caution' : 'Review required before proceeding'}
              </p>
              <p className="text-slate-300 text-sm leading-relaxed">
                {report.finalVerdict || 'Please review all sections above before making a decision.'}
              </p>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="rounded-xl p-4 text-center"
          style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)' }}>
          <p className="text-xs text-slate-600">
            This report is AI-generated and for informational purposes only. It does not constitute legal advice.
            Always consult a qualified legal professional before signing any document.
          </p>
        </div>

      </div>
    </div>
  )
}
