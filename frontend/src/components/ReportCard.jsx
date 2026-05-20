import { Link } from 'react-router-dom'
import { FileText, Trash2, Eye, Calendar, CheckCircle, XCircle } from 'lucide-react'
import { format } from 'date-fns'
import RiskBadge from './RiskBadge'

export default function ReportCard({ report, onDelete }) {
  const date = report.createdAt ? format(new Date(report.createdAt), 'MMM d, yyyy') : 'Unknown'

  return (
    <div className="glass p-5 hover:border-gold-400/20 transition-all duration-300 group animate-fade-in"
      style={{ background: 'rgba(255,255,255,0.03)' }}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform"
            style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.2)' }}>
            <FileText className="w-5 h-5 text-gold-400" />
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-white truncate text-sm" title={report.filename}>{report.filename}</h3>
            <p className="text-xs text-slate-500 mt-0.5">{report.documentType}</p>
            <div className="flex items-center gap-1 mt-1 text-xs text-slate-600">
              <Calendar className="w-3 h-3" />{date}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1 flex-shrink-0">
          <Link to={`/report/${report.id}`}
            className="p-2 rounded-lg text-slate-500 hover:text-gold-400 hover:bg-gold-400/10 transition-all"
            title="View report"><Eye className="w-4 h-4" /></Link>
          <button onClick={() => onDelete(report.id)}
            className="p-2 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-400/10 transition-all"
            title="Delete"><Trash2 className="w-4 h-4" /></button>
        </div>
      </div>
      <div className="flex items-center justify-between mt-4 pt-3 border-t border-white/5">
        {report.riskLevel ? <RiskBadge level={report.riskLevel} /> : <span className="text-xs text-slate-600">No data</span>}
        {report.safeToSign
          ? <span className="flex items-center gap-1 text-xs font-medium" style={{ color: '#4ade80' }}><CheckCircle className="w-3.5 h-3.5" />Safe to sign</span>
          : <span className="flex items-center gap-1 text-xs font-medium" style={{ color: '#f87171' }}><XCircle className="w-3.5 h-3.5" />Review needed</span>}
      </div>
    </div>
  )
}
