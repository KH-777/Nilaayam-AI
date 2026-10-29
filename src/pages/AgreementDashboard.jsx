import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  AlertOctagon, 
  AlertTriangle, 
  CheckCircle2, 
  Info, 
  Download, 
  HelpCircle, 
  FileText,
  Printer,
  ArrowLeft,
  Share2
} from 'lucide-react'
import toast from 'react-hot-toast'

import { useLanguage } from '../context/LanguageContext'
import DisclaimerBanner from '../components/DisclaimerBanner'
import ClauseCard from '../components/ClauseCard'
import LanguageToggle from '../components/LanguageToggle'
import { getAgreementReport, exportReport } from '../api/client'
import { demoAgreementAnalysis } from '../data/demoData'

export default function AgreementDashboard() {
  const { id } = useParams()
  const { language, t } = useLanguage()

  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [filterSeverity, setFilterSeverity] = useState('all')

  useEffect(() => {
    async function fetchReport() {
      setLoading(true)
      setLoadError('')
      try {
        if (id === 'demo') {
          setReport(demoAgreementAnalysis)
          return
        }

        // Check localStorage first for fresh upload result
        const cached = localStorage.getItem(`nilaayam_agr_${id}`)
        if (cached) {
          setReport(JSON.parse(cached))
          setLoading(false)
          return
        }

        const data = await getAgreementReport(id)
        setReport(data)
      } catch (err) {
        console.error('Failed to load agreement analysis:', err)
        setLoadError(err?.response?.data?.detail || t('Could not load this agreement analysis. Please upload the document again.', 'இந்த ஒப்பந்தப் பகுப்பாய்வை ஏற்ற முடியவில்லை. ஆவணத்தை மீண்டும் பதிவேற்றவும்.'))
      } finally {
        setLoading(false)
      }
    }
    fetchReport()
  }, [id, t])

  const handleExportPDF = async () => {
    try {
      toast.loading(t('Generating printable PDF...', 'PDF அறிக்கை தயாராகிறது...'), { id: 'pdf-toast' })
      await exportReport(id || 'demo', 'pdf', language)
      toast.success(t('Report ready for download / printing!', 'அறிக்கை தயார்!'), { id: 'pdf-toast' })
      window.print()
    } catch (e) {
      toast.error(t('Export error', 'பிழை ஏற்பட்டது'), { id: 'pdf-toast' })
      window.print()
    }
  }

  if (loading) {
    return (
      <div className="container" style={{ padding: '5rem 20px', textAlign: 'center' }}>
        <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚡</div>
        <h2>{t('Loading Agreement Risk Report...', 'வாடகை ஒப்பந்த அறிக்கை ஏற்றப்படுகிறது...')}</h2>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="container" style={{ padding: '5rem 20px', textAlign: 'center' }}>
        <h2>{loadError}</h2>
        <Link to="/upload" className="btn-primary" style={{ marginTop: '1.5rem' }}>
          {t('Upload a document', 'ஆவணத்தைப் பதிவேற்றவும்')}
        </Link>
      </div>
    )
  }

  const analysis = report || demoAgreementAnalysis
  const stats = analysis.stats || {
    red_count: analysis.red_count || 0,
    yellow_count: analysis.yellow_count || 0,
    green_count: analysis.green_count || 0,
    grey_count: analysis.grey_count || 0
  }

  // Sort findings: Red first, then Yellow, then Grey, then Green
  const severityWeight = { red: 1, yellow: 2, grey: 3, green: 4 }
  const sortedFindings = [...(analysis.findings || [])].sort((a, b) => {
    const wA = severityWeight[(a.severity || 'grey').toLowerCase()] || 9
    const wB = severityWeight[(b.severity || 'grey').toLowerCase()] || 9
    return wA - wB
  })

  // Filter findings if selected
  const filteredFindings = filterSeverity === 'all' 
    ? sortedFindings 
    : sortedFindings.filter(f => (f.severity || '').toLowerCase() === filterSeverity)

  const overallTitle = language === 'ta' && analysis.overall_status_ta
    ? analysis.overall_status_ta
    : analysis.risk_level || analysis.overall_status || 'Analysis Results'

  const overallDesc = language === 'ta' && analysis.summary?.risk_summary_ta
    ? analysis.summary.risk_summary_ta
    : analysis.summary?.risk_summary || (typeof analysis.summary === 'string' ? analysis.summary : '')
  const questionsToAsk = analysis.questions_to_ask || analysis.recommended_questions || analysis.questions || []

  return (
    <div className="container" style={{ padding: '2.5rem 20px 5rem' }}>
      {/* Top Breadcrumb & Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <Link to="/upload" style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-navy)', fontWeight: 600, fontSize: '0.9rem' }}>
          <ArrowLeft size={16} />
          {t('Back to Upload', 'மீண்டும் பதிவேற்ற பக்கத்திற்கு')}
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {(analysis.isDemoData || analysis.is_demo) && (
            <span className="demo-badge">
              ⚡ {t('Demo Data Mode', 'மாதிரி தரவு நிலை')}
            </span>
          )}
          <LanguageToggle />
          <Link to={`/report/${id || 'demo'}`} className="btn-outline-dark" style={{ padding: '0.45rem 0.9rem' }}>
            <Printer size={16} />
            {t('Full Printable Report', 'அச்சு அறிக்கை')}
          </Link>
          <button type="button" className="btn-primary" onClick={handleExportPDF} style={{ padding: '0.45rem 1rem' }}>
            <Download size={16} />
            {t('Export PDF', 'PDF பதிவிறக்கு')}
          </button>
        </div>
      </div>

      {/* Main Title */}
      <div className="page-header">
        <h1>{t('Rental Agreement Risk Analysis', 'வாடகை ஒப்பந்த இடர் பகுப்பாய்வு')}</h1>
        <p>
          {analysis.document_name || 'Uploaded Agreement'} • {t('Audited under TNRRRLT Act 2017 & Indian Contract Law', 'TNRRRLT சட்டம் 2017-ன் கீழ் ஆய்வு செய்யப்பட்டது')}
        </p>
      </div>

      {/* Mandatory Disclaimer Banner */}
      <DisclaimerBanner />

      {/* Overall Summary Card */}
      <div className="card" style={{ marginBottom: '2rem', borderLeft: '6px solid var(--color-red)' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
          <div style={{ background: 'var(--color-red-pale)', color: 'var(--color-red)', padding: 12, borderRadius: 10 }}>
            <AlertOctagon size={28} />
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--color-navy)', marginBottom: '0.4rem', fontWeight: 700 }}>
              {overallTitle}
            </h2>
            <p style={{ color: '#334155', fontSize: '1rem', lineHeight: 1.6 }}>
              {overallDesc}
            </p>
          </div>
        </div>
      </div>

      {/* Color-Coded Stat Badges */}
      <div className="summary-stats">
        <div
          className="stat-badge"
          style={{ cursor: 'pointer', border: filterSeverity === 'red' ? '2px solid var(--color-red)' : '1px solid var(--color-grey-border)' }}
          onClick={() => setFilterSeverity(filterSeverity === 'red' ? 'all' : 'red')}
        >
          <div className="stat-badge-icon red">
            <AlertOctagon size={22} />
          </div>
          <div>
            <div className="stat-count" style={{ color: 'var(--color-red)' }}>{stats.red_count || 0}</div>
            <div className="stat-label">{t('High Risk Clauses', 'அதிக ஆபத்தான பிரிவுகள்')}</div>
          </div>
        </div>

        <div
          className="stat-badge"
          style={{ cursor: 'pointer', border: filterSeverity === 'yellow' ? '2px solid #ca8a04' : '1px solid var(--color-grey-border)' }}
          onClick={() => setFilterSeverity(filterSeverity === 'yellow' ? 'all' : 'yellow')}
        >
          <div className="stat-badge-icon yellow">
            <AlertTriangle size={22} />
          </div>
          <div>
            <div className="stat-count" style={{ color: '#a06e00' }}>{stats.yellow_count || 0}</div>
            <div className="stat-label">{t('Caution Required', 'எச்சரிக்கை தேவை')}</div>
          </div>
        </div>

        <div
          className="stat-badge"
          style={{ cursor: 'pointer', border: filterSeverity === 'green' ? '2px solid var(--color-green)' : '1px solid var(--color-grey-border)' }}
          onClick={() => setFilterSeverity(filterSeverity === 'green' ? 'all' : 'green')}
        >
          <div className="stat-badge-icon green">
            <CheckCircle2 size={22} />
          </div>
          <div>
            <div className="stat-count" style={{ color: 'var(--color-green)' }}>{stats.green_count || 0}</div>
            <div className="stat-label">{t('Standard / Fair', 'நியாயமான பிரிவுகள்')}</div>
          </div>
        </div>

        <div
          className="stat-badge"
          style={{ cursor: 'pointer', border: filterSeverity === 'grey' ? '2px solid var(--color-grey)' : '1px solid var(--color-grey-border)' }}
          onClick={() => setFilterSeverity(filterSeverity === 'grey' ? 'all' : 'grey')}
        >
          <div className="stat-badge-icon grey">
            <Info size={22} />
          </div>
          <div>
            <div className="stat-count" style={{ color: 'var(--color-grey)' }}>{stats.grey_count || 0}</div>
            <div className="stat-label">{t('Informational', 'தகவல் குறிப்புகள்')}</div>
          </div>
        </div>
      </div>

      {/* Clause-by-Clause Analysis Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <h2 className="section-title" style={{ margin: 0 }}>
          <FileText size={22} style={{ color: 'var(--color-navy)' }} />
          <span>{t('Clause-by-Clause Findings', 'பிரிவு வாரியான கண்டுபிடிப்புகள்')}</span>
          <span style={{ fontSize: '0.9rem', color: '#64748b', fontWeight: 500, marginLeft: 6 }}>
            ({filteredFindings.length} {t('of', '/') } {sortedFindings.length})
          </span>
        </h2>
        {filterSeverity !== 'all' && (
          <button 
            type="button" 
            onClick={() => setFilterSeverity('all')}
            style={{ fontSize: '0.85rem', color: 'var(--color-navy)', textDecoration: 'underline' }}
          >
            {t('Show All Severities', 'அனைத்தையும் காட்டு')}
          </button>
        )}
      </div>

      {/* List of Clause Cards */}
      <div style={{ marginBottom: '3rem' }}>
        {filteredFindings.map((finding) => (
          <ClauseCard key={finding.id} finding={finding} language={language} />
        ))}
      </div>

      {/* Key Questions to Ask Before Signing */}
      {questionsToAsk.length > 0 && (
        <div className="card" style={{ background: '#fefce8', borderColor: '#fef08a', padding: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.25rem' }}>
            <div style={{ background: '#fef08a', color: '#854d0e', padding: 8, borderRadius: 8 }}>
              <HelpCircle size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.3rem', color: '#713f12', fontWeight: 700 }}>
                {t('Questions to Ask Before Signing', 'கையெழுத்திடும் முன் உரிமையாளரிடம் கேட்க வேண்டிய முக்கிய கேள்விகள்')}
              </h3>
              <p style={{ color: '#854d0e', fontSize: '0.9rem' }}>
                {t('Take these specific questions to your landlord to negotiate a fair and legally valid agreement.', 'இந்தக் கேள்விகளை முன்வைத்து நியாயமான முறையில் ஒப்பந்தத்தை திருத்திக் கொள்ளுங்கள்.')}
              </p>
            </div>
          </div>

          <ol style={{ paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {questionsToAsk.map((q, idx) => (
              <li key={idx} style={{ color: '#78350f', fontSize: '1rem', fontWeight: 500, lineHeight: 1.5 }}>
                {q}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  )
}
