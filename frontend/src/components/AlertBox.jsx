import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react'

const variants = {
  warning: {
    container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    icon: AlertTriangle,
    iconClass: 'text-yellow-500',
  },
  success: {
    container: 'bg-green-50 border-green-200 text-green-800',
    icon: CheckCircle,
    iconClass: 'text-green-500',
  },
  error: {
    container: 'bg-red-50 border-red-200 text-red-800',
    icon: XCircle,
    iconClass: 'text-red-500',
  },
  info: {
    container: 'bg-blue-50 border-blue-200 text-blue-800',
    icon: Info,
    iconClass: 'text-blue-500',
  },
}

export default function AlertBox({ variant = 'info', title, children }) {
  const { container, icon: Icon, iconClass } = variants[variant]

  return (
    <div className={`flex gap-3 p-4 rounded-lg border ${container}`} role="alert">
      <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${iconClass}`} />
      <div>
        {title && <p className="font-semibold mb-1">{title}</p>}
        <div className="text-sm">{children}</div>
      </div>
    </div>
  )
}
