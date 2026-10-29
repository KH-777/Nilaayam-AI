import React from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { FileText, ShieldCheck, CheckSquare, Upload, Home, Info } from 'lucide-react'

import { LanguageProvider, useLanguage } from './context/LanguageContext'
import LanguageToggle from './components/LanguageToggle'

// Pages
import Landing from './pages/Landing'
import UploadPage from './pages/Upload'
import AgreementDashboard from './pages/AgreementDashboard'
import PropertyVerification from './pages/PropertyVerification'
import RegistrationChecklist from './pages/RegistrationChecklist'
import ReportPage from './pages/ReportPage'

function Navbar() {
  const { pathname } = useLocation()
  const { t } = useLanguage()

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="navbar-brand">
          <span className="navbar-logo-icon">🏘️</span>
          <div>
            <span style={{ letterSpacing: '-0.02em' }}>Nilaayam</span>
            <span style={{ color: '#6ee7b7', marginLeft: 4, fontWeight: 800 }}>AI</span>
          </div>
        </Link>

        <ul className="navbar-nav">
          <li>
            <Link to="/" className={`nav-link ${pathname === '/' ? 'active' : ''}`}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Home size={16} />
                {t('Home', 'முகப்பு')}
              </span>
            </Link>
          </li>
          <li>
            <Link to="/upload" className={`nav-link ${pathname === '/upload' ? 'active' : ''}`}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Upload size={16} />
                {t('Upload & Scan', 'பதிவேற்றம்')}
              </span>
            </Link>
          </li>
          <li>
            <Link to="/checklist" className={`nav-link ${pathname === '/checklist' ? 'active' : ''}`}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <CheckSquare size={16} />
                {t('Checklist', 'சரிபார்ப்புப் பட்டியல்')}
              </span>
            </Link>
          </li>
          <li>
            <Link to="/analysis/demo" className={`nav-link ${pathname.startsWith('/analysis') ? 'active' : ''}`}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <FileText size={16} />
                {t('Demo Analysis', 'மாதிரி பகுப்பாய்வு')}
              </span>
            </Link>
          </li>
          <li>
            <Link to="/property/demo" className={`nav-link ${pathname.startsWith('/property') ? 'active' : ''}`}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <ShieldCheck size={16} />
                {t('Demo Property', 'மாதிரி சொத்து')}
              </span>
            </Link>
          </li>
          <li>
            <LanguageToggle />
          </li>
        </ul>
      </div>
    </nav>
  )
}

function AppContent() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/analysis/:id" element={<AgreementDashboard />} />
          <Route path="/property/:id" element={<PropertyVerification />} />
          <Route path="/checklist" element={<RegistrationChecklist />} />
          <Route path="/report/:id" element={<ReportPage />} />
        </Routes>
      </main>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            fontFamily: 'var(--font-primary)',
            fontSize: '0.9rem',
            borderRadius: 'var(--radius-sm)',
            boxShadow: 'var(--shadow-md)'
          }
        }} 
      />
    </div>
  )
}

export default function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  )
}
