import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  Printer, 
  Download, 
  ArrowLeft, 
  ShieldAlert, 
  BookOpen, 
  HelpCircle, 
  CheckCircle2, 
  FileText,
  AlertCircle
} from 'lucide-react'
import toast from 'react-hot-toast'

import { useLanguage } from '../context/LanguageContext'
import LanguageToggle from '../components/LanguageToggle'
import RiskBadge from '../components/RiskBadge'
import ComparisonTable from '../components/ComparisonTable'
import { 
  getAgreementReport, 
  getPropertyComparison, 
  exportReport, 
  getLegalReferences 
} from '../api/client'
import { 
  demoAgreementAnalysis, 
  demoPropertyComparison, 
  demoChecklist 
} from '../data/demoData'

export default function ReportPage() {
  const { id } = useParams()
  const { language, t } = useLanguage()

  const [agreementData, setAgreementData] = useState(null)
  const [propertyData, setPropertyData] = useState(null)
  const [legalRefs, setLegalRefs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadAllData() {
      setLoading(true)
      try {
        // Load agreement report
        const cachedAgr = localStorage.getItem(`nilaayam_agr_${id}`)
        if (cachedAgr) {
          setAgreementData(JSON.parse(cachedAgr))
        } else {
          const agr = await getAgreementReport(id)
          setAgreementData(agr || demoAgreementAnalysis)
        }

        // Load property report
        const cachedProp = localStorage.getItem(`nilaayam_prop_${id}`)
        if (cachedProp) {
          setPropertyData(JSON.parse(cachedProp))
        } else {
          const prop = await getPropertyComparison(id)
          setPropertyData(prop || demoPropertyComparison)
        }

        // Load legal references
        const refs = await getLegalReferences()
        setLegalRefs(refs || [])
      } catch (e) {
        console.warn('Using demo data fallback in report:', e)
        setAgreementData(demoAgreementAnalysis)
        setPropertyData(demoPropertyComparison)
      } finally {
        setLoading(false)
      }
    }
    loadAllData()
  }, [id])

  const handlePrint = () => {
    window.print()
  }

  const handleDownloadPDF = async () => {
    toast.loading(t('Exporting PDF...', 'PDF பதிவிறக்கப்படுகிறது...'), { id: 'pdf-toast' })
    try {
      await exportReport(id || 'demo', 'pdf', language)
      toast.success(t('PDF Generated!', 'PDF தயார்!'), { id: 'pdf-toast' })
      window.print()
    } catch (err) {
      toast.error(t('Export failed', 'பதிவிறக்கம் தோல்வியடைந்தது'), { id: 'pdf-toast' })
      window.print()
    }
  }

  const agr = agreementData || demoAgreementAnalysis
  const prop = propertyData || demoPropertyComparison

  return (
    <div style={{ backgroundColor: '#ffffff', minHeight: '100vh', padding: '2rem 0 5rem' }}>
      <div className="container" style={{ maxWidth: 960 }}>
        {/* Navigation & Action Bar (Hidden during print) */}
        <div 
          className="no-print" 
          style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: '2rem', 
            paddingBottom: '1rem',
            borderBottom: '1px solid #e2e8f0',
            flexWrap: 'wrap',
            gap: '1rem'
          }}
        >
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-navy)', fontWeight: 600 }}>
            <ArrowLeft size={16} />
            {t('Back to Dashboard', 'முகப்புக்குத் திரும்பு')}
          </Link>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <LanguageToggle />
            <button type="button" className="btn-outline-dark" onClick={handlePrint}>
              <Printer size={16} />
              {t('Print Document', 'அச்சிடுக')}
            </button>
            <button type="button" className="btn-primary" onClick={handleDownloadPDF}>
              <Download size={16} />
              {t('Download PDF', 'PDF பதிவிறக்கம்')}
            </button>
          </div>
        </div>

        {/* Printable Document Sheet */}
        <div style={{ border: '1px solid #e2e8f0', padding: '3rem', borderRadius: 12, boxShadow: 'var(--shadow-sm)' }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid var(--color-navy)', paddingBottom: '1.5rem', marginBottom: '2rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '1.6rem', fontWeight: 800, color: 'var(--color-navy)' }}>
                <span>🏘️ Nilaayam AI</span>
              </div>
              <p style={{ color: '#64748b', fontSize: '0.9rem', marginTop: 4 }}>
                {t('Comprehensive Legal Risk & Property Verification Dossier', 'முழுமையான சட்ட இடர் & சொத்து சரிபார்ப்பு அறிக்கை')}
              </p>
            </div>
            <div style={{ textAlign: 'right', fontSize: '0.85rem', color: '#475569' }}>
              <div><strong>{t('Dossier Ref:', 'அறிக்கை எண்:')}</strong> NIL-{id || 'DEMO-2024'}</div>
              <div><strong>{t('Date:', 'தேதி:')}</strong> {new Date().toLocaleDateString()}</div>
              <div><strong>{t('Jurisdiction:', 'ஆளுகை:')}</strong> Tamil Nadu, India</div>
            </div>
          </div>

          {/* Share with Lawyer Notice Callout */}
          <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 8, padding: '1rem 1.25rem', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: 12 }}>
            <FileText size={24} style={{ color: '#1d4ed8', flexShrink: 0 }} />
            <div>
              <strong style={{ color: '#1e40af', fontSize: '0.95rem', display: 'block' }}>
                {t('Advice for Document Reviewer: Share with your Advocate', 'பயனர் குறிப்பு: வழக்கறிஞரிடம் பகிரவும்')}
              </strong>
              <span style={{ fontSize: '0.875rem', color: '#1e3a8a' }}>
                {t(
                  'Use this document to lead a targeted discussion with your licensed legal advocate. All findings include statutory citations to facilitate instant verification.',
                  'இந்த அறிக்கையை உங்கள் வழக்கறிஞருடன் கலந்தாலோசிக்கப் பயன்படுத்தவும். அனைத்து கண்டுபிடிப்புகளும் தொடர்புடைய சட்ட ஆதாரங்களுடன் தரப்பட்டுள்ளன.'
                )}
              </span>
            </div>
          </div>

          {/* SECTION 1: OVERALL EXECUTIVE SUMMARY */}
          <section style={{ marginBottom: '2.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', color: 'var(--color-navy)', borderBottom: '1px solid #cbd5e1', paddingBottom: 6, marginBottom: '1rem', fontWeight: 700 }}>
              1. {t('Executive Risk Assessment', '1. முதன்மை இடர் மதிப்பீடு')}
            </h2>
            <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: 8, borderLeft: '4px solid var(--color-red)' }}>
              <h3 style={{ fontSize: '1.05rem', color: 'var(--color-navy)', marginBottom: 6 }}>
                {language === 'ta' && agr.overall_status_ta ? agr.overall_status_ta : agr.overall_status}
              </h3>
              <p style={{ color: '#334155', fontSize: '0.95rem', lineHeight: 1.6 }}>
                {language === 'ta' && agr.summary?.risk_summary_ta ? agr.summary.risk_summary_ta : agr.summary?.risk_summary}
              </p>
            </div>
          </section>

          {/* SECTION 2: CLAUSE-BY-CLAUSE RISK FINDINGS */}
          <section style={{ marginBottom: '2.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', color: 'var(--color-navy)', borderBottom: '1px solid #cbd5e1', paddingBottom: 6, marginBottom: '1rem', fontWeight: 700 }}>
              2. {t('Statutory Findings & Clause Review', '2. சட்ட விதிகள் & பிரிவு வாரியான முடிவுகள்')}
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {(agr.findings || []).map((finding, idx) => {
                const exp = language === 'ta' && finding.explanation_ta ? finding.explanation_ta : finding.explanation
                const rsn = language === 'ta' && finding.reason_ta ? finding.reason_ta : finding.reason
                const q = language === 'ta' && finding.suggested_question_ta ? finding.suggested_question_ta : finding.suggested_question

                return (
                  <div key={idx} style={{ border: '1px solid #e2e8f0', borderRadius: 8, padding: '1.25rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <RiskBadge level={finding.severity} />
                        <span style={{ fontWeight: 700, color: 'var(--color-navy)', fontSize: '0.95rem' }}>
                          {finding.category}
                        </span>
                      </div>
                      {finding.clause_number && (
                        <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Clause #{finding.clause_number}</span>
                      )}
                    </div>

                    <p style={{ fontStyle: 'italic', background: '#f8fafc', padding: '8px 12px', borderRadius: 4, fontSize: '0.875rem', color: '#475569', marginBottom: 8 }}>
                      "{finding.original_text}"
                    </p>

                    <p style={{ fontSize: '0.925rem', color: '#1e293b', marginBottom: 6 }}>
                      <strong>{t('Plain Meaning: ', 'விளக்கம்: ')}</strong>{exp}
                    </p>

                    {rsn && (
                      <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: 6 }}>
                        <strong>{t('Legal Rationale: ', 'சட்ட காரணம்: ')}</strong>{rsn}
                      </p>
                    )}

                    <div style={{ fontSize: '0.825rem', color: '#1d4ed8', fontWeight: 600 }}>
                      {t('Statute Ref: ', 'சட்டப்பிரிவு: ')} {finding.legal_source}
                    </div>

                    {q && (
                      <div style={{ marginTop: 8, fontSize: '0.875rem', color: '#854d0e', background: '#fefce8', padding: '6px 10px', borderRadius: 4 }}>
                        💬 <strong>{t('Proposed Revision Question: ', 'திருத்தக் கேள்வி: ')}</strong>"{q}"
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </section>

          {/* SECTION 3: QUESTIONS TO ASK */}
          {agr.questions_to_ask && agr.questions_to_ask.length > 0 && (
            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ fontSize: '1.25rem', color: 'var(--color-navy)', borderBottom: '1px solid #cbd5e1', paddingBottom: 6, marginBottom: '1rem', fontWeight: 700 }}>
                3. {t('Mandatory Questions to Ask Before Signing', '3. கையெழுத்திடும் முன் கேட்க வேண்டிய கேள்விகள்')}
              </h2>
              <ol style={{ paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', gap: 6, fontSize: '0.925rem', color: '#334155' }}>
                {agr.questions_to_ask.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ol>
            </section>
          )}

          {/* SECTION 4: PROPERTY COMPARISON (IF APPLICABLE) */}
          {prop && prop.comparisons && (
            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ fontSize: '1.25rem', color: 'var(--color-navy)', borderBottom: '1px solid #cbd5e1', paddingBottom: 6, marginBottom: '1rem', fontWeight: 700 }}>
                4. {t('Property Document Triangulation (Patta, EC, Sale Deed)', '4. சொத்து ஆவணங்கள் ஒப்பாய்வு (பட்டா, EC, கிரயப் பத்திரம்)')}
              </h2>
              <ComparisonTable comparisons={prop.comparisons} />
            </section>
          )}

          {/* SECTION 5: REGISTRATION CHECKLIST SUMMARY */}
          <section style={{ marginBottom: '2.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', color: 'var(--color-navy)', borderBottom: '1px solid #cbd5e1', paddingBottom: 6, marginBottom: '1rem', fontWeight: 700 }}>
              5. {t('Conveyance Checklist Status', '5. பதிவு ஆவணங்கள் சரிபார்ப்பு நிலை')}
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.75rem' }}>
              {demoChecklist.slice(0, 6).map((chk) => (
                <div key={chk.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: '#f8fafc', borderRadius: 6, border: '1px solid #e2e8f0', fontSize: '0.85rem' }}>
                  <span style={{ fontWeight: 600, color: 'var(--color-navy)' }}>
                    {language === 'ta' && chk.name_ta ? chk.name_ta : chk.name}
                  </span>
                  <span style={{ 
                    padding: '2px 8px', 
                    borderRadius: 4, 
                    fontWeight: 700,
                    fontSize: '0.75rem',
                    background: chk.status === 'Obtained' ? '#dcfce7' : '#fef9c3',
                    color: chk.status === 'Obtained' ? '#166534' : '#854d0e'
                  }}>
                    {chk.status}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* SECTION 6: STATUTORY REFERENCES TABLE */}
          <section style={{ marginBottom: '2.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', color: 'var(--color-navy)', borderBottom: '1px solid #cbd5e1', paddingBottom: 6, marginBottom: '1rem', fontWeight: 700 }}>
              6. {t('Statutory References & Acts Cited', '6. குறிப்பிடப்பட்டுள்ள சட்ட ஆதாரங்கள்')}
            </h2>
            <ul style={{ paddingLeft: '1.25rem', color: '#475569', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: 4 }}>
              <li>Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017 (Tamil Nadu Act 42 of 2017)</li>
              <li>The Registration Act, 1908 & The Registration (Tamil Nadu Amendment) Act, 2016 (Section 22-A)</li>
              <li>The Indian Contract Act, 1872 (Section 74 — Liquidated Damages & Unreasonable Penalties)</li>
              <li>Tamil Nadu Survey and Boundaries Act, 1923 (FMB & Revenue Survey Demarcation)</li>
            </ul>
          </section>

          {/* SECTION 7: LIMITATIONS & RECOMMENDATIONS */}
          <div style={{ background: '#fffbeb', border: '1px solid #fef3c7', padding: '1.25rem', borderRadius: 8, marginTop: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#b45309', fontWeight: 700, marginBottom: 6 }}>
              <AlertCircle size={20} />
              <span>{t('Limitations & Legal Disclaimer', 'வரம்புகள் மற்றும் சட்ட மறுப்பு')}</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#92400e', lineHeight: 1.6 }}>
              {t(
                'Nilaayam AI is an automated document analysis engine designed to facilitate preliminary document transparency. It does not constitute legal counsel, nor does it create an attorney-client relationship. Neither Nilaayam AI nor its operators are liable for any contractual commitments made on the basis of this review. Always seek counsel from a registered member of the Bar Council of Tamil Nadu & Puducherry prior to executing binding deeds.',
                'நிலாயம் AI என்பது முதற்கட்ட ஆவண மதிப்பாய்வை எளிதாக்கும் ஒரு தொழில்நுட்பக் கருவியாகும். இது முறையான சட்ட ஆலோசனை அல்ல. எந்தவொரு ஒப்பந்தத்திலும் கையொப்பமிடுவதற்கு முன்பு வழக்கறிஞரின் ஆலோசனையைப் பெறவும்.'
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
