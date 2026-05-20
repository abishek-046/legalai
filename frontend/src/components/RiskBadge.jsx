import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react'

const config = {
  Low:    { className: 'badge-low',    Icon: ShieldCheck, label: 'Low Risk' },
  Medium: { className: 'badge-medium', Icon: ShieldAlert, label: 'Medium Risk' },
  High:   { className: 'badge-high',   Icon: ShieldX,     label: 'High Risk' },
}

export default function RiskBadge({ level, showLabel = true, size = 'md' }) {
  const { className, Icon, label } = config[level] || config.Medium
  const iconSize = size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'
  const textSize = size === 'lg' ? 'text-base px-4 py-1.5' : ''
  return (
    <span className={`${className} ${textSize}`}>
      <Icon className={iconSize} />
      {showLabel && label}
    </span>
  )
}
