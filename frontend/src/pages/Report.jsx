import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Download, FileText, Calendar, CheckCircle, XCircle,
  AlertTriangle, Search, DollarSign, Clock, Scale, Lightbulb,
  ShieldAlert, Trash2
} from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import { getReport, downloadReportPdf, deleteReport } from '../services/documentService'
import RiskBadge from '../components/RiskBadge'
import AlertBox from '../components/AlertBox'
import LoadingSpinner from '../components/LoadingSpinner'

function Section({ icon: Icon, title, items, variant = 'default', emptyText }) {
  if (!items || items.length === 0) return null

  const variantStyles = {
    default: { container: 'bg-gray-50 border-gray-200', bullet: 'text-gray-400', text: 'text-gray-700' },
    warning: { container: 'bg-yellow-50 border-yellow-200', bullet: 'text-yellow-500', text: 'text-yellow-800' },
    danger: { container: 'bg-red-50 border-red-200', bullet: 'text-red-500', text: 'text-red-800' },
    success: { container: 'bg-green-50 border-green-200', bullet: 'text-green-500', text: 'text-green-800' },
    info: { container: 'bg-blue-50 border-blue-200', bullet: 'text-blue-500', text: 'text-blue-800' },
  }
  const s = variantStyles[variant]

  return (
    <div className={`rounded-xl border p-5 ${s.container}`}>
      <h3 className="section-title text-base">
        <Icon className={`w-5 h-5 ${s.bullet}`} />
        {title}
        <span className="ml-auto text-xs font-normal text-gray-400 bg-white px-2 py-0.5 rounded-full border">
          {items.length}
        </span>
      </h3>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className={`flex items-start gap-2 text-sm ${s.text}`}>
            <span className={`mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0 bg-current ${s.bullet}`} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function Report() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await getReport(id)
        setReport(data)
      } catch (err) {
        toast.error('Report not found')
        navigate('/dashboard')
      } finally {
        setLoading(false)
      }
    }
    fetchReport()
  }, [id, navigate])

  const handleDownload = async () => {
    setDownloading(true)
    try {
      await downloadReportPdf(id, report.filename)
      toast.success('PDF downloaded successfully')
    } catch {
      toast.error('Failed to download PDF')
    } finally {
      setDownloading(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this report? This action cannot be undone.')) return
    setDeleting(true)
    try {
      await deleteReport(id)
      toast.success('Report deleted')
      navigate('/dashboard')
    } catch {
      toast.error('Failed to delete report')
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading report..." />
      </div>
    )
  }

  if (!report) return null

  const date = report.createdAt
    ? format(new Date(report.createdAt), 'MMMM d, yyyy \'at\' HH:mm')
    : 'Unknown date'

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 animate-fade-in">
      {/* Back */}
      <Link to="/dashboard" className="inline-flex items-center gap-1.5 text-gray-500 hover:text-gray-700 text-sm mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </Link>

      {/* Header card */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
              <FileText className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-navy-800 break-all">{report.filename}</h1>
              <p className="text-gray-500 text-sm mt-0.5">{report.documentType}</p>
              <div className="flex items-center gap-1.5 text-xs text-gray-400 mt-1">
                <Calendar className="w-3.5 h-3.5" />
                {date}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="btn-secondary text-sm py-2 px-4"
            >
              <Download className="w-4 h-4" />
              {downloading ? 'Downloading...' : 'Download PDF'}
            </button>
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="btn-danger text-sm py-2 px-3"
              aria-label="Delete report"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Risk + Safe to sign */}
        <div className="flex flex-wrap items-center gap-4 mt-5 pt-5 border-t border-gray-100">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Risk Level:</span>
            <RiskBadge level={report.riskLevel} size="lg" />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Safe to Sign:</span>
            {report.safeToSign ? (
              <span className="flex items-center gap-1.5 text-green-700 font-semibold text-sm bg-green-100 px-3 py-1 rounded-full">
                <CheckCircle className="w-4 h-4" /> Yes
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-red-700 font-semibold text-sm bg-red-100 px-3 py-1 rounded-full">
                <XCircle className="w-4 h-4" /> Review Needed
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Summary */}
      {report.summary && (
        <div className="card mb-6">
          <h2 className="section-title">
            <Scale className="w-5 h-5 text-primary-600" />
            Document Summary
          </h2>
          <p className="text-gray-700 leading-relaxed">{report.summary}</p>
        </div>
      )}

      {/* Risk alert */}
      {report.riskLevel === 'High' && (
        <div className="mb-6">
          <AlertBox variant="error" title="High Risk Document">
            This document contains significant risks. We strongly recommend consulting a qualified
            legal professional before signing.
          </AlertBox>
        </div>
      )}
      {report.riskLevel === 'Medium' && (
        <div className="mb-6">
          <AlertBox variant="warning" title="Medium Risk Document">
            This document has some concerns that should be reviewed carefully before signing.
          </AlertBox>
        </div>
      )}
      {report.riskLevel === 'Low' && (
        <div className="mb-6">
          <AlertBox variant="success" title="Low Risk Document">
            This document appears to be relatively standard. Review the recommendations below before signing.
          </AlertBox>
        </div>
      )}

      {/* Analysis sections */}
      <div className="space-y-4">
        <Section icon={AlertTriangle} title="Warnings" items={report.warnings} variant="warning" />
        <Section icon={Search} title="Suspicious Clauses" items={report.suspiciousClauses} variant="danger" />
        <Section icon={ShieldAlert} title="Missing Clauses" items={report.missingClauses} variant="warning" />
        <Section icon={DollarSign} title="Financial & Payment Risks" items={report.financialRisks} variant="danger" />
        <Section icon={Clock} title="Expiry & Deadline Risks" items={report.expiryRisks} variant="warning" />
        <Section icon={Scale} title="Unfair Conditions" items={report.unfairConditions} variant="danger" />
        <Section icon={Lightbulb} title="Recommendations" items={report.recommendations} variant="success" />
      </div>

      {/* Disclaimer */}
      <div className="mt-8">
        <AlertBox variant="info" title="Disclaimer">
          This analysis is generated by AI and is for informational purposes only. It does not
          constitute legal advice. Always consult a qualified legal professional before signing
          any legal document.
        </AlertBox>
      </div>
    </div>
  )
}
