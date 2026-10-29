import React from 'react'
import { AlertTriangle } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function DisclaimerBanner({ text, className = '' }) {
  const { t } = useLanguage()

  const defaultText = t(
    'This tool provides preliminary AI-assisted document review, not legal advice. Always consult a qualified legal professional.',
    'இந்தக் கருவி முதற்கட்ட AI-உதவி ஆவண மதிப்பாய்வை மட்டுமே வழங்குகிறது, சட்ட ஆலோசனையை அல்ல. எப்போதும் தகுதியான சட்ட வல்லுநரை அணுகவும்.'
  )

  return (
    <div className={`disclaimer-banner ${className}`} role="alert">
      <AlertTriangle size={20} />
      <span>{text || defaultText}</span>
    </div>
  )
}
