import { Link } from 'react-router-dom'
import { FileText, Trash2, Eye, Calendar, CheckCircle, XCircle } from 'lucide-react'
import { format } from 'date-fns'
import RiskBadge from './RiskBadge'

export default function ReportCard({ report, onDelete }) {
  const date = report.createdAt
    ? format(new Date(report.createdAt), 'MMM d, yyyy')
    : 'Unknown date'

  return (
    <div className="card hover:shadow-md transition-shadow duration-200 animate-fade-in">
      <div className="flex items-start justify-between gap-4">
        {/* Icon + info */}
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <FileText className="w-5 h-5 text-primary-600" />
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-gray-900 truncate text-sm" title={report.filename}>
              {report.filename}
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">{report.documentType}</p>
            <div className="flex items-center gap-1.5 mt-1 text-xs text-gray-400">
              <Calendar className="w-3 h-3" />
              {date}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <Link
            to={`/report/${report.id}`}
            className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
            title="View report"
          >
            <Eye className="w-4 h-4" />
          </Link>
          <button
            onClick={() => onDelete(report.id)}
            className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
            title="Delete report"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
        {report.riskLevel ? (
          <RiskBadge level={report.riskLevel} />
        ) : (
          <span className="text-xs text-gray-400">No risk data</span>
        )}
        <div className="flex items-center gap-1 text-xs">
          {report.safeToSign ? (
            <span className="flex items-center gap-1 text-green-600 font-medium">
              <CheckCircle className="w-3.5 h-3.5" /> Safe to sign
            </span>
          ) : (
            <span className="flex items-center gap-1 text-red-500 font-medium">
              <XCircle className="w-3.5 h-3.5" /> Review needed
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
