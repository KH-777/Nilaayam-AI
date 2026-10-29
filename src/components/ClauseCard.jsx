import React, { useState } from 'react'
import { ChevronDown, ChevronUp, ExternalLink, HelpCircle, BookOpen, AlertOctagon } from 'lucide-react'
import RiskBadge from './RiskBadge'
import { useLanguage } from '../context/LanguageContext'

export default function ClauseCard({ finding, language: propLang }) {
  const { language: ctxLang, t } = useLanguage()
  const lang = propLang || ctxLang
  const [isExpanded, setIsExpanded] = useState(false)
  const [showFullClause, setShowFullClause] = useState(false)

  if (!finding) return null

  const severity = (finding.severity || finding.risk_level || 'grey').toLowerCase()
  const rawClause = finding.original_text || finding.clause_text || ''
  const isClauseLong = rawClause.length > 150
  const displayedClause = showFullClause || !isClauseLong 
    ? rawClause 
    : `${rawClause.slice(0, 150)}...`

  // Bilingual support for explanation & reason
  const explanation = lang === 'ta' && finding.explanation_ta
    ? finding.explanation_ta
    : finding.explanation || finding.description || finding.issue || ''

  const reason = lang === 'ta' && finding.reason_ta
    ? finding.reason_ta
    : finding.reason || finding.recommendation || ''

  const question = lang === 'ta' && finding.suggested_question_ta
    ? finding.suggested_question_ta
    : finding.suggested_question || ''

  const category = finding.category || finding.clause_category || finding.clause_title || 'General Clause'
  const source = finding.legal_source || finding.source_reference || finding.legal_reference || null
  const sourceUrl = finding.source_url || finding.legal_source_url || '#'

  return (
    <div className={`clause-card ${severity} animate-slide-in`}>
      <div className="clause-card-header">
        <div className="clause-card-meta">
          <RiskBadge level={severity} />
          <span className="clause-category">{category}</span>
          {finding.clause_number && (
            <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>
              Clause #{finding.clause_number}
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          style={{ display: 'flex', alignItems: 'center', gap: 4, color: '#475569', fontSize: '0.85rem', fontWeight: 600 }}
          aria-expanded={isExpanded}
        >
          {isExpanded ? (
            <>
              {t('Show Less', 'குறைவாகக் காட்டு')} <ChevronUp size={16} />
            </>
          ) : (
            <>
              {t('View Details', 'விவரங்களைக் காட்டு')} <ChevronDown size={16} />
            </>
          )}
        </button>
      </div>

      <div className="clause-card-body">
        {/* Original Clause Text */}
        {rawClause && (
          <div className="original-clause-box">
            <p>"{displayedClause}"</p>
            {isClauseLong && (
              <button
                type="button"
                onClick={() => setShowFullClause(!showFullClause)}
                style={{
                  color: 'var(--color-navy)',
                  fontWeight: 600,
                  fontSize: '0.8rem',
                  marginTop: 6,
                  textDecoration: 'underline'
                }}
              >
                {showFullClause 
                  ? t('Show truncated', 'சுருக்கமாகக் காட்டு') 
                  : t('Show full clause', 'முழு வாக்கியத்தைக் காட்டு')}
              </button>
            )}
          </div>
        )}

        {/* Explanation */}
        <div className="clause-explanation-section">
          <div className="explanation-title">
            {t('Plain-English Meaning', 'எளிமையான விளக்கம்')}
          </div>
          <p className="explanation-text">{explanation}</p>
        </div>

        {/* Reason / Why it's a risk */}
        {reason && (
          <div style={{ marginBottom: '1rem', background: '#f8fafc', padding: '0.75rem 1rem', borderRadius: 8 }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: 4 }}>
              {t('Why this matters / Risk Rationale', 'ஏன் இது முக்கியம் / ஆபத்து காரணம்')}
            </div>
            <p style={{ fontSize: '0.925rem', color: '#334155' }}>{reason}</p>
          </div>
        )}

        {/* Legal Source & Question */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center', justifyContent: 'space-between' }}>
          {source && (
            <a
              href={sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="clause-source-chip"
              title="View statutory reference"
            >
              <BookOpen size={14} />
              <span>{source}</span>
              <ExternalLink size={12} />
            </a>
          )}
        </div>

        {/* Suggested Question to Ask */}
        {question && (
          <div className="suggested-question-box">
            <HelpCircle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
            <div>
              <strong style={{ display: 'block', fontSize: '0.825rem', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 2 }}>
                {t('Suggested Question to Ask Landlord / Drafter:', 'உரிமையாளரிடம் கேட்க வேண்டிய கேள்வி:')}
              </strong>
              <span>"{question}"</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
