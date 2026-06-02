import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import {
  Upload as UploadIcon, FileText, X, CheckCircle,
  Brain, Loader2, FileImage, FileType, AlertTriangle
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
  'image/webp': ['.webp'],
  'image/bmp': ['.bmp'],
  'image/tiff': ['.tiff', '.tif'],
}
const MAX_SIZE = 10 * 1024 * 1024 // 10MB

// Smart status messages based on file type
const getAnalysisSteps = (filename) => {
  const ext = filename?.split('.').pop()?.toLowerCase()
  const isPdf = ext === 'pdf'
  const isImage = ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'tif'].includes(ext)

  return [
    { label: 'Uploading file...', icon: UploadIcon },
    {
      label: isPdf
        ? 'Detecting PDF type (text or scanned)...'
        : isImage
        ? 'Preparing image for OCR...'
        : 'Reading document structure...',
      icon: FileType
    },
    {
      label: isPdf
        ? 'Extracting text from PDF...'
        : isImage
        ? 'Running OCR to extract text...'
        : 'Extracting text from document...',
      icon: FileText
    },
    { label: 'Identifying clauses and terms...', icon: Brain },
    { label: 'Running AI legal analysis...', icon: Brain },
    { label: 'Detecting risks and warnings...', icon: AlertTriangle },
    { label: 'Generating recommendations...', icon: CheckCircle },
    { label: 'Finalizing report...', icon: CheckCircle },
  ]
}

const FILE_TYPE_INFO = [
  { ext: 'PDF', label: 'Text PDF', desc: 'Contracts, agreements', color: '#f87171' },
  { ext: 'PDF', label: 'Scanned PDF', desc: 'Photocopied documents', color: '#fb923c' },
  { ext: 'DOCX', label: 'Word Document', desc: 'Microsoft Word files', color: '#38bdf8' },
  { ext: 'IMG', label: 'Images', desc: 'PNG, JPG, WEBP, BMP, TIFF', color: '#a78bfa' },
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
      else if (err.code === 'file-invalid-type') setError('Invalid file type. Please upload PDF, DOCX, or an image file.')
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

    const steps = getAnalysisSteps(file.name)

    // Progress through steps with realistic timing
    let stepIdx = 0
    const stepInterval = setInterval(() => {
      stepIdx++
      if (stepIdx < steps.length - 1) {
        setAnalysisStep(stepIdx)
      }
    }, 4000)

    try {
      const result = await analyzeDocument(file, (progressEvent) => {
        if (progressEvent.total) {
          const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          setUploadProgress(pct)
          if (pct === 100) setAnalysisStep(1) // move to extraction step
        }
      })

      clearInterval(stepInterval)
      setAnalysisStep(steps.length - 1)
      toast.success('Analysis complete!')
      setTimeout(() => navigate(`/report/${result.id}`), 500)
    } catch (err) {
      clearInterval(stepInterval)
      const msg = err.response?.data?.detail || 'Analysis failed. Please try again.'
      setError(msg)
      toast.error('Analysis failed')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const removeFile = () => { setFile(null); setError('') }

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const getFileIcon = (filename) => {
    const ext = filename?.split('.').pop()?.toLowerCase()
    if (ext === 'pdf') return <FileText className="w-5 h-5 text-red-400" />
    if (['docx', 'doc'].includes(ext)) return <FileText className="w-5 h-5 text-blue-400" />
    return <FileImage className="w-5 h-5 text-purple-400" />
  }

  const steps = file ? getAnalysisSteps(file.name) : getAnalysisSteps('')

  return (
    <div className="min-h-screen pt-20 pb-12" style={{ background: '#040d18' }}>
      <div className="max-w-3xl mx-auto px-4 py-10 animate-fade-in">

        {/* Header */}
        <div className="text-center mb-10">
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-glow"
            style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
            <Brain className="w-8 h-8 text-dark-600" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Analyze Your Document</h1>
          <p className="text-slate-400">
            Upload any legal document — text PDF, scanned PDF, Word file, or image.
            Our AI extracts the text and analyzes every clause.
          </p>
        </div>

        {/* Supported formats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          {FILE_TYPE_INFO.map((f, i) => (
            <div key={i} className="glass p-3 text-center">
              <div className="text-xs font-bold mb-1" style={{ color: f.color }}>{f.ext}</div>
              <div className="text-xs font-semibold text-white">{f.label}</div>
              <div className="text-xs text-slate-500 mt-0.5">{f.desc}</div>
            </div>
          ))}
        </div>

        {/* Dropzone */}
        {!uploading && (
          <div
            {...getRootProps()}
            className="rounded-2xl p-12 text-center cursor-pointer transition-all duration-300"
            style={{
              border: `2px dashed ${isDragActive ? '#f59e0b' : file ? '#4ade80' : 'rgba(255,255,255,0.1)'}`,
              background: isDragActive
                ? 'rgba(251,191,36,0.05)'
                : file
                ? 'rgba(74,222,128,0.05)'
                : 'rgba(255,255,255,0.02)',
            }}
            role="button"
            aria-label="Upload document"
          >
            <input {...getInputProps()} />
            {file ? (
              <div className="flex flex-col items-center gap-3">
                <CheckCircle className="w-12 h-12 text-green-400" />
                <p className="font-semibold text-white">{file.name}</p>
                <p className="text-sm text-slate-400">{formatSize(file.size)}</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <UploadIcon className={`w-12 h-12 ${isDragActive ? 'text-gold-400' : 'text-slate-600'}`} />
                <div>
                  <p className="font-semibold text-white text-lg">
                    {isDragActive ? 'Drop your file here' : 'Drag & drop your document'}
                  </p>
                  <p className="text-slate-500 text-sm mt-1">or click to browse files</p>
                </div>
                <div className="flex flex-wrap justify-center gap-2 mt-2">
                  {['PDF', 'DOCX', 'PNG', 'JPG', 'WEBP', 'BMP', 'TIFF'].map(type => (
                    <span key={type} className="px-2.5 py-1 text-xs font-medium rounded-full"
                      style={{ background: 'rgba(255,255,255,0.06)', color: '#94a3b8', border: '1px solid rgba(255,255,255,0.08)' }}>
                      {type}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-slate-600">Maximum file size: 10MB</p>
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-4">
            <AlertBox variant="error" title="Processing Error">{error}</AlertBox>
          </div>
        )}

        {/* File selected bar */}
        {file && !uploading && (
          <div className="mt-5 flex items-center justify-between gap-4 p-4 rounded-xl"
            style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.2)' }}>
                {getFileIcon(file.name)}
              </div>
              <div className="min-w-0">
                <p className="font-medium text-white truncate text-sm">{file.name}</p>
                <p className="text-xs text-slate-500">{formatSize(file.size)}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <button onClick={removeFile}
                className="p-2 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-400/10 transition-all"
                aria-label="Remove file">
                <X className="w-4 h-4" />
              </button>
              <button onClick={handleAnalyze} className="btn-gold py-2 px-5 text-sm">
                <Brain className="w-4 h-4" /> Analyze Now
              </button>
            </div>
          </div>
        )}

        {/* Analysis in progress */}
        {uploading && (
          <div className="mt-6 glass p-8 text-center animate-fade-in">
            {/* Spinner */}
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="w-20 h-20 rounded-full animate-spin"
                  style={{ border: '3px solid rgba(251,191,36,0.15)', borderTopColor: '#f59e0b' }} />
                <Brain className="w-8 h-8 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-gold-400" />
              </div>
            </div>

            <h3 className="text-lg font-bold text-white mb-2">Processing Your Document</h3>
            <p className="text-gold-400 font-medium text-sm mb-6 animate-pulse">
              {steps[analysisStep]?.label || 'Processing...'}
            </p>

            {/* Upload progress bar */}
            {uploadProgress > 0 && uploadProgress < 100 && (
              <div className="mb-5">
                <div className="flex justify-between text-xs text-slate-500 mb-1.5">
                  <span>Uploading...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="w-full rounded-full h-1.5" style={{ background: 'rgba(255,255,255,0.08)' }}>
                  <div className="h-1.5 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%`, background: 'linear-gradient(90deg, #f59e0b, #d97706)' }} />
                </div>
              </div>
            )}

            {/* Step list */}
            <div className="space-y-2 text-left max-w-xs mx-auto">
              {steps.map((step, i) => {
                const StepIcon = step.icon
                const isDone = i < analysisStep
                const isCurrent = i === analysisStep
                return (
                  <div key={i} className={`flex items-center gap-2.5 text-xs transition-all duration-300 ${
                    isDone ? 'text-green-400' : isCurrent ? 'text-gold-400 font-medium' : 'text-slate-700'
                  }`}>
                    {isDone ? (
                      <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="w-3.5 h-3.5 flex-shrink-0 animate-spin" />
                    ) : (
                      <div className="w-3.5 h-3.5 rounded-full border flex-shrink-0"
                        style={{ borderColor: 'rgba(255,255,255,0.1)' }} />
                    )}
                    {step.label}
                  </div>
                )
              })}
            </div>

            <p className="text-xs text-slate-600 mt-6">
              This may take 15–45 seconds depending on document size. Please don't close this page.
            </p>
          </div>
        )}

        {/* Info box */}
        {!uploading && (
          <div className="mt-8">
            <AlertBox variant="info" title="How document processing works">
              <ul className="space-y-1 mt-1">
                <li>• Text PDFs → text extracted directly (fastest)</li>
                <li>• Scanned PDFs → automatically detected and OCR applied</li>
                <li>• Images → OCR runs to read text from the image</li>
                <li>• AI analyzes every clause for risks and issues</li>
                <li>• Download a professional PDF report anytime</li>
              </ul>
            </AlertBox>
          </div>
        )}
      </div>
    </div>
  )
}
