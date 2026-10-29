import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  ShieldAlert, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Download, 
  Printer, 
  ArrowLeft,
  FileCheck2,
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import toast from 'react-hot-toast'

import { useLanguage } from '../context/LanguageContext'
import DisclaimerBanner from '../components/DisclaimerBanner'
import ComparisonTable from '../components/ComparisonTable'
import LanguageToggle from '../components/LanguageToggle'
import { getPropertyComparison, exportReport } from '../api/client'
import { demoPropertyComparison } from '../data/demoData'

export default function PropertyVerification() {
  const { id } = useParams()
  const { language, t } = useLanguage()

  const [comparisonData, setComparisonData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [expandedFlags, setExpandedFlags] = useState({})

  useEffect(() => {
    async function fetchComparison() {
      setLoading(true)
      try {
        const cached = localStorage.getItem(`nilaayam_prop_${id}`)
        if (cached) {
          setComparisonData(JSON.parse(cached))
          setLoading(false)
          return
        }

        const data = await getPropertyComparison(id)
        setComparisonData(data || demoPropertyComparison)
      } catch (err) {
        console.warn('Using demo property comparison data:', err)
        setComparisonData(demoPropertyComparison)
      } finally {
        setLoading(false)
      }
    }
    fetchComparison()
  }, [id])

  const toggleFlag = (flagId) => {
    setExpandedFlags(prev => ({
      ...prev,
      [flagId]: !prev[flagId]
    }))
  }

  const handlePrintOrDownload = () => {
    toast.success(t('Printing Property Verification Report...', 'அறிக்கை அச்சிடப்படுகிறது...'))
    window.print()
  }

  if (loading) {
    return (
      <div className="container" style={{ padding: '5rem 20px', textAlign: 'center' }}>
        <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚡</div>
        <h2>{t('Comparing Property Documents...', 'சொத்து ஆவணங்கள் ஒப்பிடப்படுகின்றன...')}</h2>
      </div>
    )
  }

  const data = comparisonData || demoPropertyComparison
  const summary = data.summary || {
    match_count: 2,
    mismatch_count: 1,
    flags_count: 1,
    overall_verdict: 'Discrepancy Detected'
  }

  const verdictTitle = language === 'ta' && summary.overall_verdict_ta
    ? summary.overall_verdict_ta
    : summary.overall_verdict

  return (
    <div className="container" style={{ padding: '2.5rem 20px 5rem' }}>
      {/* Top Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <Link to="/upload?tab=property" style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-navy)', fontWeight: 600, fontSize: '0.9rem' }}>
          <ArrowLeft size={16} />
          {t('Back to Property Upload', 'மீண்டும் ஆவணப் பதிவேற்றத்திற்கு')}
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {data.isDemoData && (
            <span className="demo-badge">
              ⚡ {t('Demo Data Mode', 'மாதிரி தரவு நிலை')}
            </span>
          )}
          <LanguageToggle />
          <Link to={`/report/${id || 'demo'}`} className="btn-outline-dark" style={{ padding: '0.45rem 0.9rem' }}>
            <Printer size={16} />
            {t('Full Printable Report', 'அச்சு அறிக்கை')}
          </Link>
          <button type="button" className="btn-primary" onClick={handlePrintOrDownload} style={{ padding: '0.45rem 1rem' }}>
            <Download size={16} />
            {t('Download Report', 'அறிக்கையைப் பதிவிறக்கு')}
          </button>
        </div>
      </div>

      {/* Page Header */}
      <div className="page-header">
        <h1>{t('Property Document Verification & Cross-Checker', 'சொத்து ஆவணங்கள் ஒப்பீட்டு அறிக்கை')}</h1>
        <p>
          {t('Triangulating data points across Patta, Encumbrance Certificate, and Sale Deed', 'பட்டா, வில்லங்கச் சான்றிதழ் மற்றும் கிரயப் பத்திரங்களின் ஒப்பீட்டு ஆய்வு')}
        </p>
      </div>

      {/* Mandatory Disclaimer */}
      <DisclaimerBanner />

      {/* Verdict Banner */}
      <div 
        className="card" 
        style={{ 
          marginBottom: '2rem', 
          borderLeft: `6px solid ${summary.mismatch_count > 0 ? 'var(--color-red)' : 'var(--color-green)'}`,
          background: summary.mismatch_count > 0 ? '#fff5f5' : '#f0fdf4'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
          <div 
            style={{ 
              background: summary.mismatch_count > 0 ? 'var(--color-red-pale)' : 'var(--color-green-pale)', 
              color: summary.mismatch_count > 0 ? 'var(--color-red)' : 'var(--color-green)', 
              padding: 12, 
              borderRadius: 10 
            }}
          >
            {summary.mismatch_count > 0 ? <ShieldAlert size={28} /> : <CheckCircle size={28} />}
          </div>
          <div>
            <h2 style={{ fontSize: '1.35rem', color: 'var(--color-navy)', fontWeight: 700, marginBottom: '0.25rem' }}>
              {verdictTitle}
            </h2>
            <p style={{ color: '#334155', fontSize: '0.95rem' }}>
              {t(
                'Cross-document reconciliation complete. One or more critical survey identifier discrepancies were identified and require physical inspection of Taluk revenue maps.',
                'ஆவணங்களின் ஒப்பாய்வு நிறைவுற்றது. சர்வே எண் உட்பிரிவு முரண்பாடுகள் உள்ளதால் வட்டாட்சியர் அலுவலக வரைபடத்தை சரிபார்க்க வேண்டும்.'
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Verification Stat Counts */}
      <div className="summary-stats">
        <div className="stat-badge">
          <div className="stat-badge-icon green">
            <CheckCircle size={22} />
          </div>
          <div>
            <div className="stat-count" style={{ color: 'var(--color-green)' }}>{summary.match_count || 0}</div>
            <div className="stat-label">{t('Matching Fields', 'பொருந்தும் புலங்கள்')}</div>
          </div>
        </div>

        <div className="stat-badge">
          <div className="stat-badge-icon red">
            <XCircle size={22} />
          </div>
          <div>
            <div className="stat-count" style={{ color: 'var(--color-red)' }}>{summary.mismatch_count || 0}</div>
            <div className="stat-label">{t('Mismatches / Conflicts', 'முரண்பாடுகள்')}</div>
          </div>
        </div>

        <div className="stat-badge">
          <div className="stat-badge-icon yellow">
            <AlertTriangle size={22} />
          </div>
          <div>
            <div className="stat-count" style={{ color: '#a06e00' }}>{summary.flags_count || 0}</div>
            <div className="stat-label">{t('High Priority Flags', 'முக்கிய எச்சரிக்கைகள்')}</div>
          </div>
        </div>
      </div>

      {/* Main Comparison Table */}
      <div style={{ marginBottom: '3rem' }}>
        <h2 className="section-title">
          <FileCheck2 size={22} style={{ color: 'var(--color-navy)' }} />
          <span>{t('Side-by-Side Field Cross-Check', 'புலங்கள் வாரியான ஒப்பீடு')}</span>
        </h2>
        <ComparisonTable comparisons={data.comparisons || []} />
      </div>

      {/* Red Flags Section */}
      {data.red_flags && data.red_flags.length > 0 && (
        <div style={{ marginBottom: '3rem' }}>
          <h2 className="section-title" style={{ color: 'var(--color-red)' }}>
            <ShieldAlert size={22} />
            <span>{t('Discrepancy Red Flags & Required Actions', 'கடுமையான முரண்பாடுகள் & செய்ய வேண்டிய நடவடிக்கைகள்')}</span>
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {data.red_flags.map((flag) => {
              const isExpanded = expandedFlags[flag.id] ?? true
              const flagTitle = language === 'ta' && flag.title_ta ? flag.title_ta : flag.title
              const flagDesc = language === 'ta' && flag.description_ta ? flag.description_ta : flag.description
              const flagRec = language === 'ta' && flag.recommendation_ta ? flag.recommendation_ta : flag.recommendation

              return (
                <div 
                  key={flag.id} 
                  className="card" 
                  style={{ borderLeft: '5px solid var(--color-red)', padding: '1.5rem' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                      <span className="risk-badge-red" style={{ padding: '4px 10px', borderRadius: 999 }}>
                        {t('HIGH PRIORITY FLAG', 'அதிக முக்கியத்துவம்')}
                      </span>
                      <span 
                        style={{ 
                          background: '#fef3c7', 
                          color: '#92400e', 
                          border: '1px solid #fde68a',
                          padding: '3px 8px', 
                          borderRadius: 6, 
                          fontSize: '0.775rem', 
                          fontWeight: 700 
                        }}
                      >
                        ⚠️ {t('Requires official verification', 'அரசுத் துறை சரிபார்ப்பு அவசியம்')}
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={() => toggleFlag(flag.id)}
                      style={{ color: '#64748b', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 4 }}
                    >
                      {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </button>
                  </div>

                  <h3 style={{ fontSize: '1.2rem', color: 'var(--color-navy)', fontWeight: 700, margin: '0.75rem 0 0.5rem' }}>
                    {flagTitle}
                  </h3>

                  <p style={{ color: '#334155', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '1rem' }}>
                    {flagDesc}
                  </p>

                  {isExpanded && flagRec && (
                    <div style={{ background: '#f8fafc', borderLeft: '3px solid var(--color-navy)', padding: '0.9rem 1.15rem', borderRadius: '0 8px 8px 0' }}>
                      <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-navy)', textTransform: 'uppercase', marginBottom: 3 }}>
                        {t('Recommended Next Step:', 'பரிந்துரைக்கப்படும் அடுத்த நடவடிக்கை:')}
                      </div>
                      <p style={{ fontSize: '0.925rem', color: '#1e293b' }}>
                        {flagRec}
                      </p>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Direct Quick Link to Checklist */}
      <div className="card" style={{ background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', padding: '1.5rem 2rem' }}>
        <div>
          <h3 style={{ fontSize: '1.15rem', color: 'var(--color-navy)', fontWeight: 700 }}>
            {t('Planning to register this property in Tamil Nadu?', 'இந்தச் சொத்தை தமிழ்நாட்டில் பதிவு செய்ய திட்டமிடுகிறீர்களா?')}
          </h3>
          <p style={{ fontSize: '0.9rem', color: '#475569' }}>
            {t('Follow our official SRO pre-registration checklist to prevent document rejections.', 'சார்-பதிவாளர் அலுவலக ஆவண நிராகரிப்பை தவிர்க்க முழுமையான சரிபார்ப்பு பட்டியலை பாருங்கள்.')}
          </p>
        </div>
        <Link to="/checklist" className="btn-primary">
          <span>{t('Open Registration Checklist', 'சரிபார்ப்புப் பட்டியலைத் திற')}</span>
        </Link>
      </div>
    </div>
  )
}
