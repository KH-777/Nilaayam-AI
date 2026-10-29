import React, { useState, useEffect } from 'react'
import { 
  CheckSquare, 
  Square, 
  AlertCircle, 
  HelpCircle, 
  ExternalLink, 
  Clock, 
  RotateCcw, 
  Printer, 
  ChevronDown, 
  ChevronUp,
  Info
} from 'lucide-react'
import toast from 'react-hot-toast'

import { useLanguage } from '../context/LanguageContext'
import DisclaimerBanner from '../components/DisclaimerBanner'
import LanguageToggle from '../components/LanguageToggle'
import { generateChecklist } from '../api/client'
import { demoChecklist } from '../data/demoData'

export default function RegistrationChecklist() {
  const { language, t } = useLanguage()

  const [transactionType, setTransactionType] = useState('sale') // 'sale' | 'lease'
  const [propertyType, setPropertyType] = useState('residential') // 'residential' | 'agricultural' | 'commercial'
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandedInfo, setExpandedInfo] = useState({})

  // Storage key for local persistence
  const storageKey = `nilaayam_chk_${transactionType}_${propertyType}`

  useEffect(() => {
    async function loadChecklist() {
      setLoading(true)
      try {
        const saved = localStorage.getItem(storageKey)
        if (saved) {
          setItems(JSON.parse(saved))
          setLoading(false)
          return
        }

        const data = await generateChecklist(propertyType, transactionType, language)
        const initialItems = (data?.items && data.items.length > 0) ? data.items : demoChecklist
        setItems(initialItems)
        localStorage.setItem(storageKey, JSON.stringify(initialItems))
      } catch (err) {
        console.warn('Failed loading checklist from API, using demo fallback:', err)
        setItems(demoChecklist)
      } finally {
        setLoading(false)
      }
    }
    loadChecklist()
  }, [transactionType, propertyType, language, storageKey])

  const handleStatusChange = (id, newStatus) => {
    const updated = items.map(item => {
      if (item.id === id) {
        return { ...item, status: newStatus }
      }
      return item
    })
    setItems(updated)
    localStorage.setItem(storageKey, JSON.stringify(updated))
  }

  const handleResetChecklist = () => {
    const reset = items.map(i => ({ ...i, status: 'Pending' }))
    setItems(reset)
    localStorage.setItem(storageKey, JSON.stringify(reset))
    toast.success(t('Checklist reset to default.', 'சரிபார்ப்புப் பட்டியல் மீட்டமைக்கப்பட்டது.'))
  }

  const toggleWhyNeeded = (id) => {
    setExpandedInfo(prev => ({
      ...prev,
      [id]: !prev[id]
    }))
  }

  // Calculate Progress
  const totalItems = items.length
  const obtainedCount = items.filter(i => i.status === 'Obtained').length
  const progressPercent = totalItems > 0 ? Math.round((obtainedCount / totalItems) * 100) : 0

  return (
    <div className="container" style={{ padding: '2.5rem 20px 5rem' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div className="page-header" style={{ margin: 0 }}>
          <h1>{t('Sub-Registrar Registration Checklist', 'சார்-பதிவாளர் அலுவலக பதிவு சரிபார்ப்புப் பட்டியல்')}</h1>
          <p>
            {t('Tamil Nadu Registration Department compliance checklist for property conveyance', 'தமிழ்நாடு பதிவுத் துறை வழிகாட்டுதலின்படியான ஆவண சரிபார்ப்பு பட்டியல்')}
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <LanguageToggle />
          <button type="button" className="btn-outline-dark" onClick={() => window.print()}>
            <Printer size={16} />
            {t('Print Checklist', 'அச்சிடுக')}
          </button>
          <button type="button" className="btn-outline-dark" onClick={handleResetChecklist} title="Reset Statuses">
            <RotateCcw size={16} />
            {t('Reset', 'மீட்டமை')}
          </button>
        </div>
      </div>

      <DisclaimerBanner />

      {/* Selectors for Transaction & Property Type */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.5rem' }}>
          {/* Transaction Type */}
          <div>
            <label style={{ display: 'block', fontWeight: 600, color: 'var(--color-navy)', marginBottom: 8, fontSize: '0.95rem' }}>
              {t('Transaction Type', 'பரிவர்த்தனை வகை')}
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                type="button"
                className={`tab-button ${transactionType === 'sale' ? 'active' : ''}`}
                style={{ padding: '0.65rem 1rem', border: '1px solid #cbd5e1' }}
                onClick={() => setTransactionType('sale')}
              >
                {t('Sale Deed (கிரயம்)', 'கிரயப் பத்திரம்')}
              </button>
              <button
                type="button"
                className={`tab-button ${transactionType === 'lease' ? 'active' : ''}`}
                style={{ padding: '0.65rem 1rem', border: '1px solid #cbd5e1' }}
                onClick={() => setTransactionType('lease')}
              >
                {t('Long Lease / Rental (குத்தகை)', 'குத்தகை / வாடகை')}
              </button>
            </div>
          </div>

          {/* Property Type */}
          <div>
            <label style={{ display: 'block', fontWeight: 600, color: 'var(--color-navy)', marginBottom: 8, fontSize: '0.95rem' }}>
              {t('Property Category', 'சொத்து வகை')}
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <button
                type="button"
                className={`tab-button ${propertyType === 'residential' ? 'active' : ''}`}
                style={{ padding: '0.65rem 1rem', border: '1px solid #cbd5e1' }}
                onClick={() => setPropertyType('residential')}
              >
                {t('Residential', 'குடியிருப்பு')}
              </button>
              <button
                type="button"
                className={`tab-button ${propertyType === 'agricultural' ? 'active' : ''}`}
                style={{ padding: '0.65rem 1rem', border: '1px solid #cbd5e1' }}
                onClick={() => setPropertyType('agricultural')}
              >
                {t('Agricultural', 'விவசாய நிலம்')}
              </button>
              <button
                type="button"
                className={`tab-button ${propertyType === 'commercial' ? 'active' : ''}`}
                style={{ padding: '0.65rem 1rem', border: '1px solid #cbd5e1' }}
                onClick={() => setPropertyType('commercial')}
              >
                {t('Commercial', 'வணிக வளாகம்')}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar Card */}
      <div className="card" style={{ marginBottom: '2rem', background: '#f8fafc' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <strong style={{ color: 'var(--color-navy)', fontSize: '1rem' }}>
            {t('Readiness Progress:', 'தயார் நிலை முன்னேற்றம்:')} {obtainedCount} / {totalItems} {t('Documents Ready', 'ஆவணங்கள் தயார்')}
          </strong>
          <span style={{ fontWeight: 700, color: progressPercent === 100 ? 'var(--color-green)' : 'var(--color-navy)' }}>
            {progressPercent}%
          </span>
        </div>
        <div className="progress-container" style={{ height: 10 }}>
          <div 
            className="progress-bar" 
            style={{ 
              width: `${progressPercent}%`,
              backgroundColor: progressPercent === 100 ? 'var(--color-green)' : '#2563eb' 
            }}
          ></div>
        </div>
      </div>

      {/* Warning Notice Box */}
      <div style={{ background: '#fffbeb', border: '1px solid #fef3c7', padding: '0.9rem 1.25rem', borderRadius: 8, marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: 10, fontSize: '0.9rem', color: '#92400e' }}>
        <Info size={18} style={{ flexShrink: 0 }} />
        <span>
          <strong>{t('Important Notice: ', 'முக்கிய அறிவிப்பு: ')}</strong>
          {t(
            'Requirements may vary. Always verify specific local office circulars with your jurisdictional Sub-Registrar Office (SRO).',
            'சார்-பதிவாளர் அலுவலக நடைமுறைகள் வட்டத்திற்கு ஏற்ப மாறுபடலாம். உங்கள் எல்லைக்குட்பட்ட அலுவலகத்தில் உறுதிப்படுத்தவும்.'
          )}
        </span>
      </div>

      {/* Checklist Items List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {items.map((item) => {
          const isObtained = item.status === 'Obtained'
          const isNeedsVerification = item.status === 'Needs Verification'
          const isExpanded = expandedInfo[item.id] || false

          const title = language === 'ta' && item.name_ta ? item.name_ta : item.name
          const whyNeeded = language === 'ta' && item.why_needed_ta ? item.why_needed_ta : item.why_needed

          return (
            <div 
              key={item.id} 
              className="card" 
              style={{ 
                padding: '1.25rem 1.5rem',
                borderLeft: isObtained 
                  ? '5px solid var(--color-green)' 
                  : (isNeedsVerification ? '5px solid #ca8a04' : '5px solid #cbd5e1'),
                backgroundColor: isObtained ? '#fcfdfd' : 'var(--color-white)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem', flex: 1, minWidth: 260 }}>
                  <button
                    type="button"
                    onClick={() => handleStatusChange(item.id, isObtained ? 'Pending' : 'Obtained')}
                    style={{ marginTop: 2, color: isObtained ? 'var(--color-green)' : '#94a3b8' }}
                    title={isObtained ? 'Mark Pending' : 'Mark Obtained'}
                  >
                    {isObtained ? <CheckSquare size={22} /> : <Square size={22} />}
                  </button>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
                      <span style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-navy)', textDecoration: isObtained ? 'line-through' : 'none' }}>
                        {title}
                      </span>
                      {item.is_mandatory && (
                        <span style={{ background: '#fee2e2', color: '#991b1b', fontSize: '0.7rem', fontWeight: 800, padding: '2px 7px', borderRadius: 4 }}>
                          MANDATORY
                        </span>
                      )}
                    </div>

                    {/* Status Pill Selector */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 6 }}>
                      <span style={{ fontSize: '0.8rem', color: '#64748b' }}>{t('Status:', 'நிலை:')}</span>
                      <select
                        value={item.status}
                        onChange={(e) => handleStatusChange(item.id, e.target.value)}
                        style={{
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          padding: '3px 8px',
                          borderRadius: 6,
                          border: '1px solid #cbd5e1',
                          backgroundColor: item.status === 'Obtained' ? '#dcfce7' : (item.status === 'Needs Verification' ? '#fef9c3' : '#f1f5f9'),
                          color: item.status === 'Obtained' ? '#15803d' : (item.status === 'Needs Verification' ? '#854d0e' : '#475569')
                        }}
                      >
                        <option value="Obtained">{t('Obtained', 'பெறப்பட்டது')}</option>
                        <option value="Pending">{t('Pending', 'நிலுவையில் உள்ளது')}</option>
                        <option value="Needs Verification">{t('Needs Verification', 'சரிபார்ப்பு தேவை')}</option>
                      </select>

                      {item.last_verified && (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: '0.75rem', color: '#94a3b8', marginLeft: 10 }}>
                          <Clock size={12} />
                          {t('Verified:', 'சரிபார்க்கப்பட்டது:')} {item.last_verified}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Expand / Details Toggle */}
                <button
                  type="button"
                  onClick={() => toggleWhyNeeded(item.id)}
                  style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.825rem', color: '#475569', fontWeight: 600 }}
                >
                  {isExpanded ? (
                    <>
                      {t('Less info', 'குறைவாக')} <ChevronUp size={16} />
                    </>
                  ) : (
                    <>
                      {t('Why needed?', 'ஏன் தேவை?')} <ChevronDown size={16} />
                    </>
                  )}
                </button>
              </div>

              {/* Expandable Explanation & Notes */}
              {isExpanded && (
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px dashed #e2e8f0' }}>
                  <p style={{ fontSize: '0.925rem', color: '#334155', marginBottom: 8, lineHeight: 1.5 }}>
                    <strong>{t('Legal Purpose: ', 'சட்ட நோக்கம்: ')}</strong>
                    {whyNeeded}
                  </p>

                  {item.notes && (
                    <div style={{ fontSize: '0.85rem', color: '#b45309', background: '#fffbeb', padding: '6px 10px', borderRadius: 6, marginBottom: 8 }}>
                      ⚠️ {item.notes}
                    </div>
                  )}

                  {item.official_source && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', color: '#2563eb' }}>
                      <span>{t('Statutory Authority: ', 'சட்ட ஆதாரம்: ')} {item.official_source}</span>
                      {item.official_source_url && (
                        <a href={item.official_source_url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink size={12} />
                        </a>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
