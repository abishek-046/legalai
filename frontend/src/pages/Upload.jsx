import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import {
  Upload as UploadIcon, FileText, X, CheckCircle,
  AlertCircle, Brain, Loader2, File
} from 'lucide-react'
import toast from 'react-hot-toast'
import { analyzeDocument } from '../services/documentService'
import AlertBox from '../components/AlertBox'

const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/msword': ['.doc'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
}
const MAX_SIZE = 10 * 1024 * 1024 // 10MB

const analysisSteps = [
  'Extracting text from document...',
  'Reading document structure...',
  'Identifying clauses and terms...',
  'Running AI legal analysis...',
  'Detecting risks and warnings...',
  'Generating recommendations...',
  'Finalizing report...',
]

export default function Upload() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [analysisStep, setAnalysisStep] = useState(0)
  const [error, setError] = useState('')

  const onDrop = useCallback((accepted, rejected) => {
    setError('')
    if (rejected.length > 0) {
      const err = rejected[0].errors[0]
      if (err.code === 'file-too-large') setError('File is too large. Maximum size is 10MB.')
      else if (err.code === 'file-invalid-type') setError('Invalid file type. Please upload PDF, DOCX, PNG, or JPG.')
      else setError(err.message)
      return
    }
    if (accepted.length > 0) setFile(accepted[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: MAX_SIZE,
    multiple: false,
  })

  const handleAnalyze = async () => {
    if (!file) return
    setUploading(true)
    setError('')
    setAnalysisStep(0)

    // Simulate step progression during analysis
    const stepInterval = setInterval(() => {
      setAnalysisStep((prev) => (prev < analysisSteps.length - 1 ? prev + 1 : prev))
    }, 3000)

    try {
      const result = await analyzeDocument(file, (progressEvent) => {
        const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        setUploadProgress(pct)
      })

      clearInterval(stepInterval)
      toast.success('Analysis complete!')
      navigate(`/report/${result.id}`)
    } catch (err) {
      clearInterval(stepInterval)
      const msg = err.response?.data?.detail || 'Analysis failed. Please try again.'
      setError(msg)
      toast.error(msg)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const removeFile = () => {
    setFile(null)
    setError('')
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12 animate-fade-in">
      {/* Header */}
      <div className="text-center mb-10">
        <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Brain className="w-8 h-8 text-primary-600" />
        </div>
        <h1 className="text-3xl font-bold text-navy-800 mb-2">Analyze Your Document</h1>
        <p className="text-gray-500">
          Upload a legal document and get an instant AI-powered analysis with risk assessment.
        </p>
      </div>

      {/* Dropzone */}
      {!uploading && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-200 ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : file
              ? 'border-green-400 bg-green-50'
              : 'border-gray-300 bg-white hover:border-primary-400 hover:bg-primary-50/30'
          }`}
          role="button"
          aria-label="Upload document"
        >
          <input {...getInputProps()} />
          {file ? (
            <div className="flex flex-col items-center gap-3">
              <CheckCircle className="w-12 h-12 text-green-500" />
              <p className="font-semibold text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-500">{formatSize(file.size)}</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <UploadIcon className={`w-12 h-12 ${isDragActive ? 'text-primary-500' : 'text-gray-400'}`} />
              <div>
                <p className="font-semibold text-gray-700 text-lg">
                  {isDragActive ? 'Drop your file here' : 'Drag & drop your document'}
                </p>
                <p className="text-gray-400 text-sm mt-1">or click to browse files</p>
              </div>
              <div className="flex flex-wrap justify-center gap-2 mt-2">
                {['PDF', 'DOCX', 'PNG', 'JPG'].map((type) => (
                  <span key={type} className="px-2.5 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded-full">
                    {type}
                  </span>
                ))}
              </div>
              <p className="text-xs text-gray-400">Maximum file size: 10MB</p>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-4">
          <AlertBox variant="error" title="Upload Error">{error}</AlertBox>
        </div>
      )}

      {/* File selected - actions */}
      {file && !uploading && (
        <div className="mt-6 flex items-center justify-between gap-4 p-4 bg-white rounded-xl border border-gray-200">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <FileText className="w-5 h-5 text-primary-600" />
            </div>
            <div className="min-w-0">
              <p className="font-medium text-gray-900 truncate text-sm">{file.name}</p>
              <p className="text-xs text-gray-400">{formatSize(file.size)}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={removeFile}
              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              aria-label="Remove file"
            >
              <X className="w-4 h-4" />
            </button>
            <button onClick={handleAnalyze} className="btn-primary py-2 px-5 text-sm">
              <Brain className="w-4 h-4" />
              Analyze Now
            </button>
          </div>
        </div>
      )}

      {/* Analysis in progress */}
      {uploading && (
        <div className="mt-6 card text-center animate-fade-in">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="w-20 h-20 rounded-full border-4 border-primary-100 border-t-primary-600 animate-spin" />
              <Brain className="w-8 h-8 text-primary-600 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
            </div>
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">AI is Analyzing Your Document</h3>
          <p className="text-primary-600 font-medium text-sm mb-6 animate-pulse">
            {analysisSteps[analysisStep]}
          </p>

          {/* Progress bar */}
          {uploadProgress > 0 && uploadProgress < 100 && (
            <div className="mb-4">
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Uploading...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Steps */}
          <div className="space-y-2 text-left max-w-xs mx-auto">
            {analysisSteps.map((step, i) => (
              <div key={step} className={`flex items-center gap-2 text-xs transition-all duration-300 ${
                i < analysisStep ? 'text-green-600' : i === analysisStep ? 'text-primary-600 font-medium' : 'text-gray-300'
              }`}>
                {i < analysisStep ? (
                  <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />
                ) : i === analysisStep ? (
                  <Loader2 className="w-3.5 h-3.5 flex-shrink-0 animate-spin" />
                ) : (
                  <div className="w-3.5 h-3.5 rounded-full border border-gray-200 flex-shrink-0" />
                )}
                {step}
              </div>
            ))}
          </div>

          <p className="text-xs text-gray-400 mt-6">This may take 15-30 seconds. Please don't close this page.</p>
        </div>
      )}

      {/* Info box */}
      {!uploading && (
        <div className="mt-8">
          <AlertBox variant="info" title="What happens after upload?">
            <ul className="space-y-1 mt-1">
              <li>• Text is extracted from your document using OCR</li>
              <li>• AI analyzes every clause for risks and issues</li>
              <li>• You receive a detailed report with recommendations</li>
              <li>• Download a professional PDF report anytime</li>
            </ul>
          </AlertBox>
        </div>
      )}
    </div>
  )
}
