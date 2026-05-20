import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react'

const variants = {
  warning: { bg: 'rgba(251,191,36,0.08)', border: 'rgba(251,191,36,0.25)', text: '#fbbf24', Icon: AlertTriangle },
  success: { bg: 'rgba(34,197,94,0.08)',  border: 'rgba(34,197,94,0.25)',  text: '#4ade80', Icon: CheckCircle },
  error:   { bg: 'rgba(239,68,68,0.08)',  border: 'rgba(239,68,68,0.25)',  text: '#f87171', Icon: XCircle },
  info:    { bg: 'rgba(56,189,248,0.08)', border: 'rgba(56,189,248,0.25)', text: '#38bdf8', Icon: Info },
}

export default function AlertBox({ variant = 'info', title, children }) {
  const { bg, border, text, Icon } = variants[variant]
  return (
    <div className="flex gap-3 p-4 rounded-xl" style={{ background: bg, border: `1px solid ${border}` }} role="alert">
      <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" style={{ color: text }} />
      <div>
        {title && <p className="font-semibold mb-1 text-sm" style={{ color: text }}>{title}</p>}
        <div className="text-sm text-slate-400">{children}</div>
      </div>
    </div>
  )
}
