import React from 'react'
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function RiskBadge({ level = 'grey', label, size = 'normal', showIcon = true }) {
  const { t } = useLanguage()

  const normalized = (level || 'grey').toLowerCase()

  const config = {
    red: {
      className: 'risk-badge-red',
      icon: <AlertCircle size={size === 'small' ? 12 : 14} />,
      defaultLabel: t('High Risk', 'அதிக ஆபத்து')
    },
    yellow: {
      className: 'risk-badge-yellow',
      icon: <AlertTriangle size={size === 'small' ? 12 : 14} />,
      defaultLabel: t('Caution', 'எச்சரிக்கை தேவை')
    },
    green: {
      className: 'risk-badge-green',
      icon: <CheckCircle2 size={size === 'small' ? 12 : 14} />,
      defaultLabel: t('Fair / Standard', 'நியாயமானது')
    },
    grey: {
      className: 'risk-badge-grey',
      icon: <Info size={size === 'small' ? 12 : 14} />,
      defaultLabel: t('Informational', 'தகவல்')
    }
  }

  const current = config[normalized] || config.grey

  return (
    <span className={`risk-badge ${current.className}`}>
      {showIcon && current.icon}
      <span>{label || current.defaultLabel}</span>
    </span>
  )
}
