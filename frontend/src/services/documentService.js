import api from './api'

/**
 * Upload and analyze a document file.
 * Returns the full analysis report.
 */
export async function analyzeDocument(file, onUploadProgress) {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await api.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  })
  return data
}

/**
 * Get all reports for the current user.
 */
export async function getReports(params = {}) {
  const { data } = await api.get('/reports', { params })
  return data
}

/**
 * Get a single report by ID.
 */
export async function getReport(id) {
  const { data } = await api.get(`/report/${id}`)
  return data
}

/**
 * Delete a report by ID.
 */
export async function deleteReport(id) {
  await api.delete(`/report/${id}`)
}

/**
 * Get the PDF download URL for a report.
 */
export function getReportPdfUrl(id) {
  const token = localStorage.getItem('token')
  return `/api/report/${id}/download`
}

/**
 * Download a report PDF (triggers browser download).
 */
export async function downloadReportPdf(id, filename) {
  const { data } = await api.get(`/report/${id}/download`, {
    responseType: 'blob',
  })
  const url = window.URL.createObjectURL(new Blob([data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `legal_analysis_${filename || id}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
