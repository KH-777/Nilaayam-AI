import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { 
  FileText, 
  Home, 
  Scale, 
  Upload, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles,
  ArrowRight,
  ListChecks
} from 'lucide-react'

import { useLanguage } from '../context/LanguageContext'
import UploadZone from '../components/UploadZone'
import DisclaimerBanner from '../components/DisclaimerBanner'
import { 
  uploadDocument, 
  analyzeAgreement, 
  compareProperties,
  generateChecklist 
} from '../api/client'

export default function UploadPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const { language, t } = useLanguage()

  const initialTab = searchParams.get('tab') === 'property' ? 'property' : 'rental'
  const [activeTab, setActiveTab] = useState(initialTab)

  // Rental state
  const [rentalFile, setRentalFile] = useState(null)
  const [isRentalProcessing, setIsRentalProcessing] = useState(false)
  const [rentalStatusStage, setRentalStatusStage] = useState('') // 'uploading' | 'extracting' | 'analyzing'
  const [rentalProgress, setRentalProgress] = useState(0)

  // Property state
  const [pattaFile, setPattaFile] = useState(null)
  const [ecFile, setEcFile] = useState(null)
  const [saleDeedFile, setSaleDeedFile] = useState(null)
  const [isPropertyProcessing, setIsPropertyProcessing] = useState(false)
  const [propertyProgress, setPropertyProgress] = useState(0)

  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab === 'property' || tab === 'rental') {
      setActiveTab(tab)
    }
  }, [searchParams])

  const handleTabChange = (tab) => {
    setActiveTab(tab)
    setSearchParams({ tab })
  }

  // Handle Rental Agreement Analysis
  const handleAnalyzeAgreement = async () => {
    if (!rentalFile) {
      toast.error(t('Please select a rental agreement document first.', 'முதலில் வாடகை ஒப்பந்த ஆவணத்தைத் தேர்ந்தெடுக்கவும்.'))
      return
    }

    setIsRentalProcessing(true)
    setRentalProgress(15)
    setRentalStatusStage(t('Uploading document...', 'ஆவணம் பதிவேற்றப்படுகிறது...'))

    try {
      // Step 1: Upload
      const uploadRes = await uploadDocument(rentalFile, (p) => {
        setRentalProgress(Math.min(60, Math.round(p * 0.6)))
      }, 'rental_agreement')
      if (!uploadRes?.document_id || uploadRes.is_demo) {
        throw new Error(t('The uploaded file was not processed by the analysis service.', 'பதிவேற்றிய கோப்பு பகுப்பாய்வு சேவையால் செயலாக்கப்படவில்லை.'))
      }

      // Step 2: Extracting OCR
      setRentalProgress(70)
      setRentalStatusStage(t('Extracting legal clauses & text...', 'சட்டப் பிரிவுகள் பிரித்தெடுக்கப்படுகின்றன...'))
      await new Promise(r => setTimeout(r, 600))

      // Step 3: Analyzing Risk
      setRentalProgress(85)
      setRentalStatusStage(t('Analyzing against TNRRRLT Act 2017...', 'TNRRRLT சட்டம் 2017 உடன் ஒப்பிட்டு ஆய்வு செய்யப்படுகிறது...'))
      
      const analysisRes = await analyzeAgreement(uploadRes.document_id, language)
      const analysisId = analysisRes?.analysis_id || analysisRes?.id
      if (!analysisId || analysisRes.is_demo) {
        throw new Error(t('A document-based analysis could not be generated.', 'ஆவண அடிப்படையிலான பகுப்பாய்வை உருவாக்க முடியவில்லை.'))
      }
      
      setRentalProgress(100)
      setRentalStatusStage(t('Analysis Complete!', 'பகுப்பாய்வு முடிந்தது!'))
      toast.success(t('Agreement analyzed successfully!', 'வாடகை ஒப்பந்தம் வெற்றிகரமாக ஆய்வு செய்யப்பட்டது!'))

      // Save to localStorage
      if (analysisRes) {
        localStorage.setItem(`nilaayam_agr_${analysisId}`, JSON.stringify(analysisRes))
      }

      setTimeout(() => {
        navigate(`/analysis/${analysisId}`)
      }, 500)
    } catch (err) {
      console.error(err)
      const detail = err?.response?.data?.detail
      const errorMessage = typeof detail === 'string'
        ? detail
        : detail?.message || err?.message
      toast.error(errorMessage || t('Failed to analyze the uploaded document. Please check the file and try again.', 'பதிவேற்றிய ஆவணத்தை ஆய்வு செய்ய முடியவில்லை. கோப்பைச் சரிபார்த்து மீண்டும் முயற்சிக்கவும்.'))
    } finally {
      setIsRentalProcessing(false)
    }
  }

  // Handle Property Comparison
  const handleCompareProperties = async () => {
    if (!pattaFile && !ecFile && !saleDeedFile) {
      toast.error(t('Please upload at least one property document to compare.', 'ஒப்பிடுவதற்கு குறைந்தபட்சம் ஒரு ஆவணத்தையாவது பதிவேற்றவும்.'))
      return
    }

    setIsPropertyProcessing(true)
    setPropertyProgress(25)

    try {
      // Upload docs
      const pattaRes = pattaFile ? await uploadDocument(pattaFile) : null
      setPropertyProgress(50)
      const ecRes = ecFile ? await uploadDocument(ecFile) : null
      setPropertyProgress(75)
      const saleDeedRes = saleDeedFile ? await uploadDocument(saleDeedFile) : null
      setPropertyProgress(90)

      const compareRes = await compareProperties(
        pattaRes?.document_id || 'patta-demo',
        ecRes?.document_id || 'ec-demo',
        saleDeedRes?.document_id || 'sale-demo',
        language
      )

      setPropertyProgress(100)
      toast.success(t('Property documents compared successfully!', 'சொத்து ஆவணங்கள் வெற்றிகரமாக ஒப்பிடப்பட்டன!'))

      if (compareRes) {
        localStorage.setItem(`nilaayam_prop_${compareRes.id || 'demo'}`, JSON.stringify(compareRes))
      }

      setTimeout(() => {
        navigate(`/property/${compareRes.id || 'demo'}`)
      }, 500)
    } catch (err) {
      console.error(err)
      toast.error(t('Comparison error. Loading demo comparison.', 'ஒப்பீட்டில் பிழை. மாதிரி ஒப்பீடு ஏற்றப்படுகிறது.'))
      navigate('/property/demo')
    } finally {
      setIsPropertyProcessing(false)
    }
  }

  // Handle Generate Checklist
  const handleGenerateChecklist = async () => {
    try {
      const chkRes = await generateChecklist('residential', 'sale', language)
      if (chkRes && chkRes.items) {
        localStorage.setItem('nilaayam_custom_checklist', JSON.stringify(chkRes.items))
      }
      toast.success(t('Registration checklist prepared!', 'பதிவு சரிபார்ப்புப் பட்டியல் தயாரானது!'))
      navigate('/checklist')
    } catch (err) {
      navigate('/checklist')
    }
  }

  // Quick Demo Preload Buttons
  const handleLoadDemoAgreement = () => {
    setRentalFile({
      name: 'Sample_Rental_Agreement_Chennai_2024.pdf',
      size: 1.8 * 1024 * 1024
    })
    toast.success(t('Demo agreement file loaded.', 'மாதிரி ஒப்பந்தக் கோப்பு ஏற்றப்பட்டது.'))
  }

  const handleLoadDemoPropertyDocs = () => {
    setPattaFile({ name: 'Computerised_Patta_TN_142_3B.pdf', size: 640 * 1024 })
    setEcFile({ name: 'Encumbrance_Cert_TNREGINET.pdf', size: 1.2 * 1024 * 1024 })
    setSaleDeedFile({ name: 'Parent_Sale_Deed_Doc_452.pdf', size: 3.5 * 1024 * 1024 })
    toast.success(t('Demo property documents loaded.', 'மாதிரி சொத்து ஆவணங்கள் ஏற்றப்பட்டன.'))
  }

  return (
    <div className="container" style={{ padding: '3rem 20px 5rem' }}>
      <div className="upload-container">
        {/* Page Title */}
        <div className="page-header" style={{ textAlign: 'center' }}>
          <h1>{t('Document Upload & Verification', 'ஆவணப் பதிவேற்றம் மற்றும் சரிபார்ப்பு')}</h1>
          <p>
            {t(
              'Upload your legal documents for rapid AI risk scanning and discrepancy detection.',
              'உங்கள் ஆவணங்களைப் பதிவேற்றி சட்ட இடர்கள் மற்றும் முரண்பாடுகளை உடனடியாக அறியுங்கள்.'
            )}
          </p>
        </div>

        <DisclaimerBanner />

        {/* Tab Navigation */}
        <div className="tab-nav">
          <button
            type="button"
            className={`tab-button ${activeTab === 'rental' ? 'active' : ''}`}
            onClick={() => handleTabChange('rental')}
          >
            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
              <Scale size={18} />
              {t('Rental Agreement Scanner', 'வாடகை ஒப்பந்த ஸ்கேனர்')}
            </span>
          </button>
          <button
            type="button"
            className={`tab-button ${activeTab === 'property' ? 'active' : ''}`}
            onClick={() => handleTabChange('property')}
          >
            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
              <Home size={18} />
              {t('Property Documents Cross-Check', 'சொத்து ஆவணங்கள் ஒப்பீடு')}
            </span>
          </button>
        </div>

        {/* TAB 1: RENTAL AGREEMENT */}
        {activeTab === 'rental' && (
          <div className="card animate-fade-in-up">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
              <div>
                <h2 style={{ fontSize: '1.35rem', color: 'var(--color-navy)', fontWeight: 700 }}>
                  {t('Upload Residential Rental Agreement', 'வாடகை ஒப்பந்தத்தைப் பதிவேற்றவும்')}
                </h2>
                <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
                  {t(
                    'Scans for deposit caps, termination notice period, maintenance liability, and TN portal registration.',
                    'முன்பண உச்சவரம்பு, வெளியேற்ற நோட்டீஸ் மற்றும் பராமரிப்பு விதிகளை ஆய்வு செய்கிறது.'
                  )}
                </p>
              </div>
              <button
                type="button"
                className="btn-outline-dark"
                onClick={handleLoadDemoAgreement}
                style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
              >
                <Sparkles size={14} />
                {t('Load Sample File', 'மாதிரிக் கோப்பை ஏற்று')}
              </button>
            </div>

            <UploadZone
              label={t('Agreement Document (PDF / DOCX / Image)', 'ஒப்பந்த ஆவணம் (PDF / DOCX / படம்)')}
              sublabel={t('Supports Tamil & English rental agreements up to 25 MB', 'தமிழ் மற்றும் ஆங்கில வாடகை ஒப்பந்தங்கள் (25 MB வரை)')}
              documentType="rental"
              selectedFile={rentalFile}
              onFileSelect={(file) => setRentalFile(file)}
              onRemoveFile={() => setRentalFile(null)}
              isUploading={isRentalProcessing}
              progress={rentalProgress}
            />

            {isRentalProcessing && (
              <div style={{ textAlign: 'center', margin: '1rem 0', color: 'var(--color-green)', fontWeight: 600 }}>
                {rentalStatusStage}
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                {t('Security guarantee: Files are processed securely and deleted post-analysis.', 'பாதுகாப்பு: ஆவணங்கள் ஆய்வு முடிந்தபின் தானாக நீக்கப்படும்.')}
              </div>
              <button
                type="button"
                className="btn-primary"
                onClick={handleAnalyzeAgreement}
                disabled={!rentalFile || isRentalProcessing}
                style={{ minWidth: 200 }}
              >
                <Scale size={18} />
                <span>
                  {isRentalProcessing 
                    ? t('Analyzing Clauses...', 'ஆய்வு செய்யப்படுகிறது...') 
                    : t('Analyze Agreement', 'ஒப்பந்தத்தை ஆய்வு செய்')}
                </span>
              </button>
            </div>
          </div>
        )}

        {/* TAB 2: PROPERTY DOCUMENTS */}
        {activeTab === 'property' && (
          <div className="card animate-fade-in-up">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
              <div>
                <h2 style={{ fontSize: '1.35rem', color: 'var(--color-navy)', fontWeight: 700 }}>
                  {t('Cross-Check Property Documents', 'சொத்து ஆவணங்களை ஒப்பிடுக')}
                </h2>
                <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
                  {t(
                    'Upload Patta, Encumbrance Certificate (EC), and Sale Deed to detect survey number, extent, and ownership mismatches.',
                    'பட்டா, வில்லங்கச் சான்றிதழ் மற்றும் கிரயப் பத்திரங்களை பதிவேற்றி சர்வே எண் முரண்பாடுகளை கண்டறியவும்.'
                  )}
                </p>
              </div>
              <button
                type="button"
                className="btn-outline-dark"
                onClick={handleLoadDemoPropertyDocs}
                style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
              >
                <Sparkles size={14} />
                {t('Load 3 Sample Docs', '3 மாதிரிக் கோப்புகளை ஏற்று')}
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
              {/* Document 1: Patta */}
              <div>
                <UploadZone
                  label={t('1. Patta / Chitta', '1. பட்டா / சிட்டா நகல்')}
                  sublabel={t('Anytime/Anywhere e-Patta', 'வருவாய்த் துறை கணினி பட்டா')}
                  documentType="patta"
                  selectedFile={pattaFile}
                  onFileSelect={(file) => setPattaFile(file)}
                  onRemoveFile={() => setPattaFile(null)}
                  isUploading={isPropertyProcessing}
                />
              </div>

              {/* Document 2: Encumbrance Certificate */}
              <div>
                <UploadZone
                  label={t('2. Encumbrance Certificate (EC)', '2. வில்லங்கச் சான்றிதழ் (EC)')}
                  sublabel={t('TNREGINET Form 15 / 16', 'பதிவுத் துறை படிவம் 15')}
                  documentType="ec"
                  selectedFile={ecFile}
                  onFileSelect={(file) => setEcFile(file)}
                  onRemoveFile={() => setEcFile(null)}
                  isUploading={isPropertyProcessing}
                />
              </div>

              {/* Document 3: Sale Deed */}
              <div>
                <UploadZone
                  label={t('3. Registered Sale Deed', '3. கிரயப் பத்திரம்')}
                  sublabel={t('Parent title deed copy', 'அசல் அல்லது தாய் பத்திரம்')}
                  documentType="sale_deed"
                  selectedFile={saleDeedFile}
                  onFileSelect={(file) => setSaleDeedFile(file)}
                  onRemoveFile={() => setSaleDeedFile(null)}
                  isUploading={isPropertyProcessing}
                />
              </div>
            </div>

            {isPropertyProcessing && (
              <div style={{ marginTop: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--color-navy)', fontWeight: 600, marginBottom: 4 }}>
                  <span>{t('Comparing documents across revenue databases...', 'வருவாய்த் துறை தரவுகளுடன் ஒப்பிடப்படுகிறது...')}</span>
                  <span>{propertyProgress}%</span>
                </div>
                <div className="progress-container">
                  <div className="progress-bar" style={{ width: `${propertyProgress}%` }}></div>
                </div>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.75rem', flexWrap: 'wrap', gap: '1rem' }}>
              <button
                type="button"
                className="btn-outline-dark"
                onClick={handleGenerateChecklist}
              >
                <ListChecks size={18} />
                <span>{t('View Registration Checklist Only', 'பதிவு சரிபார்ப்புப் பட்டியல் மட்டும்')}</span>
              </button>

              <button
                type="button"
                className="btn-primary"
                onClick={handleCompareProperties}
                disabled={(!pattaFile && !ecFile && !saleDeedFile) || isPropertyProcessing}
                style={{ minWidth: 220 }}
              >
                <Home size={18} />
                <span>
                  {isPropertyProcessing 
                    ? t('Cross-Checking...', 'ஒப்பிடப்படுகிறது...') 
                    : t('Compare Documents', 'ஆவணங்களை ஒப்பிடு')}
                </span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
