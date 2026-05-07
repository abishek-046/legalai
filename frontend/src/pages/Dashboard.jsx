import { useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
  LayoutDashboard, Upload, Search, Calendar, RefreshCw,
  FileText, TrendingUp, AlertTriangle, CheckCircle, Filter
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useDocuments } from '../hooks/useDocuments'
import ReportCard from '../components/ReportCard'
import LoadingSpinner from '../components/LoadingSpinner'
import AlertBox from '../components/AlertBox'

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${color}`}>
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [appliedFilters, setAppliedFilters] = useState({})

  const { reports, loading, error, refetch, removeReport } = useDocuments(appliedFilters)

  const applyFilters = useCallback(() => {
    setAppliedFilters({
      ...(search ? { search } : {}),
      ...(dateFrom ? { date_from: dateFrom } : {}),
      ...(dateTo ? { date_to: dateTo } : {}),
    })
  }, [search, dateFrom, dateTo])

  const clearFilters = () => {
    setSearch('')
    setDateFrom('')
    setDateTo('')
    setAppliedFilters({})
  }

  // Stats
  const total = reports.length
  const highRisk = reports.filter((r) => r.riskLevel === 'High').length
  const safeToSign = reports.filter((r) => r.safeToSign).length
  const mediumRisk = reports.filter((r) => r.riskLevel === 'Medium').length

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-navy-800 flex items-center gap-2">
            <LayoutDashboard className="w-6 h-6 text-primary-600" />
            Dashboard
          </h1>
          <p className="text-gray-500 mt-1">Welcome back, {user?.name}</p>
        </div>
        <Link to="/upload" className="btn-primary">
          <Upload className="w-4 h-4" />
          Analyze New Document
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard icon={FileText} label="Total Reports" value={total} color="bg-blue-100 text-blue-600" />
        <StatCard icon={AlertTriangle} label="High Risk" value={highRisk} color="bg-red-100 text-red-600" />
        <StatCard icon={TrendingUp} label="Medium Risk" value={mediumRisk} color="bg-yellow-100 text-yellow-600" />
        <StatCard icon={CheckCircle} label="Safe to Sign" value={safeToSign} color="bg-green-100 text-green-600" />
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-4 h-4 text-gray-500" />
          <h2 className="font-semibold text-gray-700 text-sm">Search & Filter</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search by filename..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && applyFilters()}
              className="input-field pl-9 py-2 text-sm"
            />
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-gray-400 flex-shrink-0" />
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="input-field py-2 text-sm"
              aria-label="From date"
            />
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-gray-400 flex-shrink-0" />
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="input-field py-2 text-sm"
              aria-label="To date"
            />
          </div>
        </div>
        <div className="flex items-center gap-2 mt-3">
          <button onClick={applyFilters} className="btn-primary text-sm py-2 px-4">
            <Search className="w-3.5 h-3.5" />
            Apply Filters
          </button>
          {Object.keys(appliedFilters).length > 0 && (
            <button onClick={clearFilters} className="btn-secondary text-sm py-2 px-4">
              Clear
            </button>
          )}
          <button
            onClick={refetch}
            className="ml-auto p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Reports list */}
      {loading ? (
        <div className="flex justify-center py-16">
          <LoadingSpinner size="lg" text="Loading your reports..." />
        </div>
      ) : error ? (
        <AlertBox variant="error" title="Failed to load reports">{error}</AlertBox>
      ) : reports.length === 0 ? (
        <div className="text-center py-20 card">
          <FileText className="w-16 h-16 text-gray-200 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-500 mb-2">
            {Object.keys(appliedFilters).length > 0 ? 'No reports match your filters' : 'No reports yet'}
          </h3>
          <p className="text-gray-400 text-sm mb-6">
            {Object.keys(appliedFilters).length > 0
              ? 'Try adjusting your search or date filters.'
              : 'Upload your first legal document to get started.'}
          </p>
          {Object.keys(appliedFilters).length === 0 && (
            <Link to="/upload" className="btn-primary">
              <Upload className="w-4 h-4" />
              Upload Document
            </Link>
          )}
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-500">
              {reports.length} report{reports.length !== 1 ? 's' : ''} found
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {reports.map((report) => (
              <ReportCard key={report.id} report={report} onDelete={removeReport} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
