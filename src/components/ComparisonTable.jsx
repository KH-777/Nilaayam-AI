import React from 'react'
import { Check, X, AlertCircle, Minus } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function ComparisonTable({ comparisons = [] }) {
  const { t } = useLanguage()

  const getStatusBadge = (status) => {
    switch (status) {
      case 'match':
        return (
          <span className="status-cell-badge match">
            <Check size={14} /> {t('Match', 'பொருந்துகிறது')}
          </span>
        )
      case 'mismatch':
        return (
          <span className="status-cell-badge mismatch">
            <X size={14} /> {t('Mismatch', 'வேறுபடுகிறது')}
          </span>
        )
      case 'likely_ocr_error':
        return (
          <span className="status-cell-badge likely_ocr_error">
            <AlertCircle size={14} /> {t('Check OCR', 'எழுத்துப் பிழை')}
          </span>
        )
      case 'not_available':
      default:
        return (
          <span className="status-cell-badge not_available">
            <Minus size={14} /> {t('Not in Doc', 'கிடைக்கவில்லை')}
          </span>
        )
    }
  }

  const renderCell = (docData) => {
    if (!docData || docData.value === undefined || docData.value === null) {
      return <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.85rem' }}>—</span>
    }

    const { value, page, confidence } = docData

    return (
      <div className="cell-doc-val">
        <span className="cell-main-val">{String(value)}</span>
        {(page || confidence) && (
          <span className="cell-meta-val">
            {page && `p. ${page}`}
            {page && confidence && ` • `}
            {confidence && `${Math.round(confidence * 100)}% conf.`}
          </span>
        )}
      </div>
    )
  }

  if (!comparisons || comparisons.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
        <p>{t('No comparison fields available to display.', 'ஒப்பீட்டு புலங்கள் எதுவும் கிடைக்கவில்லை.')}</p>
      </div>
    )
  }

  return (
    <div className="comparison-table-wrapper">
      <table className="comparison-table">
        <thead>
          <tr>
            <th style={{ width: '22%' }}>{t('Field Name', 'புலத்தின் பெயர்')}</th>
            <th style={{ width: '22%' }}>{t('Patta', 'பட்டா')}</th>
            <th style={{ width: '22%' }}>{t('Encumbrance (EC)', 'வில்லங்கச் சான்று (EC)')}</th>
            <th style={{ width: '22%' }}>{t('Sale Deed', 'கிரயப் பத்திரம்')}</th>
            <th style={{ width: '12%', textAlign: 'center' }}>{t('Status', 'நிலை')}</th>
          </tr>
        </thead>
        <tbody>
          {comparisons.map((item, index) => {
            const isMismatch = item.status === 'mismatch'
            return (
              <tr key={index} className={isMismatch ? 'mismatch-row' : ''}>
                <td>
                  <strong style={{ color: 'var(--color-navy)', display: 'block' }}>
                    {item.field_label || item.field}
                  </strong>
                  {item.field_ta && (
                    <span className="text-tamil" style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      {item.field_ta}
                    </span>
                  )}
                  {item.notes && (
                    <div style={{ fontSize: '0.75rem', color: isMismatch ? '#b91c1c' : '#64748b', marginTop: 4 }}>
                      {item.notes}
                    </div>
                  )}
                </td>
                <td>{renderCell(item.patta)}</td>
                <td>{renderCell(item.ec)}</td>
                <td>{renderCell(item.sale_deed)}</td>
                <td style={{ textAlign: 'center' }}>{getStatusBadge(item.status)}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
