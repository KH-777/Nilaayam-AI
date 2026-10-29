import React from 'react'
import { useLanguage } from '../context/LanguageContext'
import { Globe } from 'lucide-react'

export default function LanguageToggle({ className = '' }) {
  const { language, setLanguage } = useLanguage()

  return (
    <div className={`language-toggle ${className}`} title="Switch Language / மொழியை மாற்றுக">
      <Globe size={14} style={{ marginLeft: 6, marginRight: 2, color: '#94a3b8' }} />
      <button
        type="button"
        className={`lang-btn ${language === 'en' ? 'active' : ''}`}
        onClick={() => setLanguage('en')}
      >
        EN
      </button>
      <button
        type="button"
        className={`lang-btn ${language === 'ta' ? 'active text-tamil' : 'text-tamil'}`}
        onClick={() => setLanguage('ta')}
      >
        தமிழ்
      </button>
    </div>
  )
}
