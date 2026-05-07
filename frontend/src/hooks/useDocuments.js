import { useState, useEffect, useCallback } from 'react'
import { getReports, deleteReport } from '../services/documentService'
import toast from 'react-hot-toast'

export function useDocuments(filters = {}) {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchReports = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getReports(filters)
      setReports(data.reports || [])
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to load reports'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [JSON.stringify(filters)])

  useEffect(() => {
    fetchReports()
  }, [fetchReports])

  const removeReport = useCallback(async (id) => {
    try {
      await deleteReport(id)
      setReports((prev) => prev.filter((r) => r.id !== id))
      toast.success('Report deleted successfully')
    } catch {
      toast.error('Failed to delete report')
    }
  }, [])

  return { reports, loading, error, refetch: fetchReports, removeReport }
}
