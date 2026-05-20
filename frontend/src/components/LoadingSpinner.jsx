export default function LoadingSpinner({ size = 'md', text = '' }) {
  const sizes = { sm: 'w-5 h-5 border-2', md: 'w-8 h-8 border-2', lg: 'w-12 h-12 border-2', xl: 'w-16 h-16 border-3' }
  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className={`${sizes[size]} rounded-full animate-spin`}
        style={{ borderColor: 'rgba(251,191,36,0.2)', borderTopColor: '#f59e0b' }}
        role="status" aria-label="Loading" />
      {text && <p className="text-slate-400 text-sm animate-pulse">{text}</p>}
    </div>
  )
}
