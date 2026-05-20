import { useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { LayoutDashboard, Upload, Search, Calendar, RefreshCw, FileText, TrendingUp, AlertTriangle, CheckCircle, Filter } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useDocuments } from '../hooks/useDocuments'
import ReportCard from '../components/ReportCard'
import LoadingSpinner from '../components/LoadingSpinner'
import AlertBox from '../components/AlertBox'

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="glass p-5 flex items-center gap-4">
      <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{ background: `${color}15`, border: `1px solid ${color}30` }}>
        <Icon className="w-6 h-6" style={{ color }} />
      </div>
      <div>
        <p className="text-2xl font-bold text-white">{value}</p>
        <p className="text-sm text-slate-500">{label}</p>
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

  const clearFilters = () => { setSearch(''); setDateFrom(''); setDateTo(''); setAppliedFilters({}) }

  const total = reports.length
  const highRisk = reports.filter(r => r.riskLevel === 'High').length
  const safeToSign = reports.filter(r => r.safeToSign).length
  const mediumRisk = reports.filter(r => r.riskLevel === 'Medium').length

  return (
    <div className="min-h-screen pt-20 pb-12" style={{ background: '#040d18' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 animate-fade-in">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <LayoutDashboard className="w-6 h-6 text-gold-400" /> Dashboard
            </h1>
            <p className="text-slate-400 mt-1 text-sm">Welcome back, <span className="text-gold-400">{user?.name}</span></p>
          </div>
          <Link to="/upload" className="btn-gold">
            <Upload className="w-4 h-4" /> Analyze New Document
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-slide-up">
          <StatCard icon={FileText} label="Total Reports" value={total} color="#38bdf8" />
          <StatCard icon={AlertTriangle} label="High Risk" value={highRisk} color="#f87171" />
          <StatCard icon={TrendingUp} label="Medium Risk" value={mediumRisk} color="#fbbf24" />
          <StatCard icon={CheckCircle} label="Safe to Sign" value={safeToSign} color="#4ade80" />
        </div>

        {/* Filters */}
        <div className="glass p-5 mb-6 animate-slide-up">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-4 h-4 text-gold-400" />
            <h2 className="font-semibold text-slate-300 text-sm">Search & Filter</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input type="text" placeholder="Search by filename..." value={search}
                onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && applyFilters()}
                className="input-dark pl-9 py-2 text-sm" />
            </div>
            <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)}
              className="input-dark py-2 text-sm" aria-label="From date" />
            <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)}
              className="input-dark py-2 text-sm" aria-label="To date" />
          </div>
          <div className="flex items-center gap-2 mt-3">
            <button onClick={applyFilters} className="btn-gold text-sm py-2 px-4">
              <Search className="w-3.5 h-3.5" /> Apply
            </button>
            {Object.keys(appliedFilters).length > 0 && (
              <button onClick={clearFilters} className="btn-outline text-sm py-2 px-4">Clear</button>
            )}
            <button onClick={refetch} className="ml-auto p-2 text-slate-500 hover:text-gold-400 hover:bg-gold-400/10 rounded-lg transition-all" aria-label="Refresh">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Reports */}
        {loading ? (
          <div className="flex justify-center py-20"><LoadingSpinner size="lg" text="Loading your reports..." /></div>
        ) : error ? (
          <AlertBox variant="error" title="Failed to load reports">{error}</AlertBox>
        ) : reports.length === 0 ? (
          <div className="glass text-center py-20 animate-fade-in">
            <FileText className="w-16 h-16 mx-auto mb-4 opacity-20 text-slate-400" />
            <h3 className="text-lg font-semibold text-slate-400 mb-2">
              {Object.keys(appliedFilters).length > 0 ? 'No reports match your filters' : 'No reports yet'}
            </h3>
            <p className="text-slate-600 text-sm mb-6">
              {Object.keys(appliedFilters).length > 0 ? 'Try adjusting your filters.' : 'Upload your first legal document to get started.'}
            </p>
            {Object.keys(appliedFilters).length === 0 && (
              <Link to="/upload" className="btn-gold"><Upload className="w-4 h-4" />Upload Document</Link>
            )}
          </div>
        ) : (
          <>
            <p className="text-sm text-slate-500 mb-4">{reports.length} report{reports.length !== 1 ? 's' : ''} found</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {reports.map(report => <ReportCard key={report.id} report={report} onDelete={removeReport} />)}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
