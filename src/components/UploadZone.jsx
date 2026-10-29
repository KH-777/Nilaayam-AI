import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud, FileText, CheckCircle2, X, AlertCircle } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function UploadZone({
  label,
  sublabel,
  onFileSelect,
  selectedFile,
  onRemoveFile,
  acceptedTypes = {
    'application/pdf': ['.pdf'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
  },
  maxSize = 25 * 1024 * 1024, // 25 MB
  documentType = 'document',
  isUploading = false,
  progress = 0
}) {
  const { t } = useLanguage()
  const [errorMessage, setErrorMessage] = useState(null)

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setErrorMessage(null)
    if (rejectedFiles && rejectedFiles.length > 0) {
      const rej = rejectedFiles[0]
      if (rej.errors[0]?.code === 'file-too-large') {
        setErrorMessage(t('File is too large. Maximum size is 25 MB.', 'கோப்பின் அளவு அதிகம். அதிகபட்சம் 25 MB.'))
      } else {
        setErrorMessage(t('Unsupported file type. Please upload PDF, DOCX, or images (JPG, PNG).', 'ஆதரிக்கப்படாத கோப்பு வடிவம். PDF, DOCX அல்லது படங்களை பதிவேற்றவும்.'))
      }
      return
    }

    if (acceptedFiles && acceptedFiles.length > 0) {
      if (onFileSelect) {
        onFileSelect(acceptedFiles[0], documentType)
      }
    }
  }, [onFileSelect, documentType, t])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes,
    maxSize,
    multiple: false,
    disabled: isUploading || !!selectedFile
  })

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div style={{ marginBottom: '1.5rem' }}>
      {label && (
        <label style={{ display: 'block', fontWeight: 600, color: 'var(--color-navy)', marginBottom: '0.4rem', fontSize: '0.95rem' }}>
          {label}
        </label>
      )}

      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`upload-zone ${isDragActive ? 'active' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="upload-zone-icon">
            <UploadCloud size={28} />
          </div>
          <div className="upload-zone-title">
            {isDragActive
              ? t('Drop your file here...', 'கோப்பை இங்கே விடவும்...')
              : t('Drag & drop your file here, or browse', 'கோப்பை இங்கே இழுத்து விடவும் அல்லது கிளிக் செய்யவும்')}
          </div>
          <div className="upload-zone-desc">
            {sublabel || t('Supports PDF, DOCX, JPG, PNG (up to 25MB)', 'PDF, DOCX, JPG, PNG ஆதரிக்கப்படும் (அதிகபட்சம் 25MB)')}
          </div>
        </div>
      ) : (
        <div className="file-preview">
          <div className="file-info">
            <FileText size={32} style={{ color: 'var(--color-green)' }} />
            <div>
              <div className="file-name">{selectedFile.name}</div>
              <div className="file-size">{formatFileSize(selectedFile.size)}</div>
            </div>
          </div>
          {!isUploading && onRemoveFile && (
            <button
              type="button"
              className="remove-file-btn"
              onClick={() => onRemoveFile(documentType)}
              title={t('Remove file', 'கோப்பை நீக்கு')}
            >
              <X size={20} />
            </button>
          )}
        </div>
      )}

      {/* Upload / processing progress */}
      {isUploading && (
        <div style={{ marginTop: '0.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#64748b', marginBottom: 4 }}>
            <span>{t('Processing file...', 'கோப்பு செயலாக்கப்படுகிறது...')}</span>
            <span>{progress}%</span>
          </div>
          <div className="progress-container">
            <div className="progress-bar" style={{ width: `${progress}%` }}></div>
          </div>
        </div>
      )}

      {errorMessage && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-red)', fontSize: '0.85rem', marginTop: 8 }}>
          <AlertCircle size={16} />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  )
}
