import React, { createContext, useContext, useState, useEffect } from 'react'

const LanguageContext = createContext()

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('nilaayam_lang') || 'en'
  })

  useEffect(() => {
    localStorage.setItem('nilaayam_lang', language)
    if (language === 'ta') {
      document.documentElement.lang = 'ta'
    } else {
      document.documentElement.lang = 'en'
    }
  }, [language])

  const toggleLanguage = () => {
    setLanguage(prev => (prev === 'en' ? 'ta' : 'en'))
  }

  // Helper for inline translations: t('English text', 'தமிழ் உரை')
  const t = (enText, taText) => {
    return language === 'ta' && taText ? taText : enText
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}
