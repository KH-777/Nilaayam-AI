import React from 'react'
import { Link } from 'react-router-dom'
import { 
  FileText, 
  ShieldCheck, 
  Upload, 
  Cpu, 
  CheckCircle, 
  BookOpen, 
  Languages, 
  ArrowRight,
  Scale,
  Sparkles,
  Search
} from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'
import DisclaimerBanner from '../components/DisclaimerBanner'

export default function Landing() {
  const { t } = useLanguage()

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="container hero-content">
          <div className="hero-badge animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            <Sparkles size={16} />
            <span>{t('Tamil Nadu AI Legal Document Assistant', 'தமிழ்நாடு சட்ட ஆவண AI உதவியாளர்')}</span>
          </div>

          <h1 className="hero-title animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            {t('Understand Before You Sign.', 'கையெழுத்திடும் முன் தெளிவாகப் புரிந்து கொள்ளுங்கள்.')}
          </h1>

          <p className="hero-subtitle animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            {t(
              'Automated AI risk scanner for Tamil Nadu rental agreements and multi-document cross-checker for Patta, EC, and Sale Deeds. Detect unfair clauses and survey discrepancies instantly.',
              'வாடகை ஒப்பந்தங்களில் உள்ள மறைமுக அபாயங்களை கண்டறிந்து, பட்டா, வில்லங்கச் சான்று மற்றும் கிரயப் பத்திரங்களின் முரண்பாடுகளை ஒப்பிட்டு சரிபார்க்கும் நவீன AI தளம்.'
            )}
          </p>

          <div className="hero-actions animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
            <Link to="/upload?tab=rental" className="btn-primary" style={{ padding: '0.9rem 1.75rem', fontSize: '1.05rem' }}>
              <Scale size={20} />
              {t('Analyze Rental Agreement', 'வாடகை ஒப்பந்தத்தை ஸ்கேன் செய்க')}
            </Link>
            <Link to="/upload?tab=property" className="btn-outline" style={{ padding: '0.9rem 1.75rem', fontSize: '1.05rem' }}>
              <ShieldCheck size={20} />
              {t('Verify Property Documents', 'சொத்து ஆவணங்களை சரிபார்க்க')}
            </Link>
          </div>
        </div>
      </section>

      {/* Disclaimer Banner right below Hero */}
      <div className="container" style={{ marginTop: '2rem' }}>
        <DisclaimerBanner />
      </div>

      {/* Two Main Service Cards */}
      <section className="services-section container">
        <div className="section-header" style={{ textAlign: 'center', maxWidth: 700, margin: '0 auto 2.5rem' }}>
          <h2 className="section-title" style={{ justifyContent: 'center' }}>
            {t('Specialized Review Engines for Tamil Nadu', 'தமிழ்நாட்டிற்கான பிரத்யேக சட்ட மதிப்பாய்வு சேவைகள்')}
          </h2>
          <p style={{ color: 'var(--color-text-muted)' }}>
            {t(
              'Trained on the TNRRRLT Act 2017, Registration Act 1908, and state revenue department standards.',
              'தமிழ்நாடு வாடகை சட்டம் 2017 மற்றும் பதிவுத் துறை வழிகாட்டுதல்களின் அடிப்படையில் வடிவமைக்கப்பட்டது.'
            )}
          </p>
        </div>

        <div className="service-cards-grid">
          {/* Service 1: Rental Agreement Scanner */}
          <div className="service-card animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="service-icon">
              <span>⚖️</span>
            </div>
            <h3 className="service-title">
              {t('Rental Agreement Risk Scanner', 'வாடகை ஒப்பந்த இடர் பகுப்பாய்வு')}
            </h3>
            <p className="service-desc">
              {t(
                'Upload your 11-month or registered residential lease. We analyze clauses against the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act (TNRRRLT Act 2017).',
                'உங்கள் வாடகை ஒப்பந்தத்தை பதிவேற்றி, அதிக முன்பணம், திடீர் வெளியேற்றம் மற்றும் நியாயமற்ற விதிமுறைகளை உடனடியாக கண்டறியுங்கள்.'
              )}
            </p>
            <ul className="service-features">
              <li>
                <CheckCircle size={16} />
                <span>{t('Flags excessive deposit demands (>3 months rent)', '3 மாதங்களுக்கு மேற்பட்ட அதிகப்படியான முன்பண எச்சரிக்கை')}</span>
              </li>
              <li>
                <CheckCircle size={16} />
                <span>{t('Detects unlawful 15-day unilateral eviction clauses', 'திடீர் 15 நாள் வெளியேற்ற நிபந்தனை ஆய்வு')}</span>
              </li>
              <li>
                <CheckCircle size={16} />
                <span>{t('Provides plain-language explanations in English & Tamil', 'எளிமையான ஆங்கிலம் மற்றும் தமிழ் விளக்கம்')}</span>
              </li>
              <li>
                <CheckCircle size={16} />
                <span>{t('Generates targeted questions to negotiate with your landlord', 'வீட்டு உரிமையாளரிடம் கேட்க வேண்டிய கேள்விகள்')}</span>
              </li>
            </ul>
            <Link to="/upload?tab=rental" className="btn-primary" style={{ marginTop: 'auto' }}>
              <span>{t('Scan Agreement Now', 'ஒப்பந்தத்தை ஸ்கேன் செய்')}</span>
              <ArrowRight size={18} />
            </Link>
          </div>

          {/* Service 2: Property Document Cross-Checker */}
          <div className="service-card animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            <div className="service-icon">
              <span>🏡</span>
            </div>
            <h3 className="service-title">
              {t('Property Document Cross-Checker', 'சொத்து ஆவணங்கள் ஒப்பீடு மற்றும் சரிபார்ப்பு')}
            </h3>
            <p className="service-desc">
              {t(
                'Cross-check your Patta, Encumbrance Certificate (EC), and Sale Deed side-by-side. Automatically identify critical discrepancies in survey numbers, plot extents, and ownership chains.',
                'பட்டா, வில்லங்கச் சான்றிதழ் மற்றும் கிரயப் பத்திரங்களை அருகருகே வைத்து ஒப்பிட்டு சர்வே எண் மற்றும் பரப்பளவு முரண்பாடுகளை வெளிக்கொணருங்கள்.'
              )}
            </p>
            <ul className="service-features">
              <li>
                <CheckCircle size={16} />
                <span>{t('Detects survey number & subdivision mismatches (e.g., 142/3A vs 3B)', 'சர்வே மற்றும் உட்பிரிவு எண் முரண்பாடுகள்')}</span>
              </li>
              <li>
                <CheckCircle size={16} />
                <span>{t('Verifies land measurement consistency (Sq.ft, Cents, Grounds)', 'பரப்பளவு சமநிலையை சரிபார்த்தல்')}</span>
              </li>
              <li>
                <CheckCircle size={16} />
                <span>{t('Matches owner names and parent title deed recitals', 'உரிமையாளர் பெயர் மற்றும் தாய் பத்திர தொடர்ச்சி')}</span>
              </li>
              <li>
                <CheckCircle size={16} />
                <span>{t('Direct guidance on Sub-Registrar & Taluk office verification', 'சார்-பதிவாளர் மற்றும் வட்டாட்சியர் அலுவலக வழிகாட்டல்')}</span>
              </li>
            </ul>
            <Link to="/upload?tab=property" className="btn-secondary" style={{ marginTop: 'auto' }}>
              <span>{t('Compare Property Docs', 'ஆவணங்களை ஒப்பிடுக')}</span>
              <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>

      {/* 3-Step Workflow Section */}
      <section className="workflow-section">
        <div className="container">
          <div style={{ textAlign: 'center', maxWidth: 650, margin: '0 auto' }}>
            <h2 className="section-title" style={{ justifyContent: 'center' }}>
              {t('How Nilaayam AI Works', 'எவ்வாறு செயல்படுகிறது?')}
            </h2>
            <p style={{ color: 'var(--color-text-muted)' }}>
              {t('From raw scan to actionable legal clarity in three simple steps.', 'மூன்று எளிய படிகளில் உங்கள் ஆவணங்களின் உண்மைத்தன்மையை அறியுங்கள்.')}
            </p>
          </div>

          <div className="workflow-grid">
            <div className="workflow-step animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              <div className="step-number">1</div>
              <div className="step-icon">📤</div>
              <h4 className="step-title">{t('1. Upload Documents', '1. ஆவணங்களைப் பதிவேற்றுங்கள்')}</h4>
              <p className="step-desc">
                {t(
                  'Upload PDF, DOCX, or scanned mobile photos of your tenancy agreement or revenue documents (Patta, EC, Sale Deed).',
                  'உங்கள் வாடகை ஒப்பந்தம் அல்லது பட்டா, EC, கிரயப் பத்திரம் போன்ற ஆவணங்களின் PDF அல்லது புகைப்படங்களை பதிவேற்றுங்கள்.'
                )}
              </p>
            </div>

            <div className="workflow-step animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="step-number">2</div>
              <div className="step-icon">⚡</div>
              <h4 className="step-title">{t('2. AI Deep Analysis', '2. நுண்ணறிவு சட்ட ஆய்வு')}</h4>
              <p className="step-desc">
                {t(
                  'Our engine extracts clauses, matches statutory benchmarks, verifies cross-document survey numbers, and checks TN tenancy laws.',
                  'எங்கள் AI எஞ்சின் பிரிவுகளைப் பிரித்தெடுத்து, சட்ட விதிகள் மற்றும் சர்வே எண்களை ஆழமாக ஆய்வு செய்கிறது.'
                )}
              </p>
            </div>

            <div className="workflow-step animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <div className="step-number">3</div>
              <div className="step-icon">💡</div>
              <h4 className="step-title">{t('3. Understand & Act', '3. தெளிவு பெற்று முடிவெடுங்கள்')}</h4>
              <p className="step-desc">
                {t(
                  'Review an intuitive, color-coded report with plain explanations, statutory citations, and specific questions to ask before signing.',
                  'வர்ணக் குறியீடு, சட்ட ஆதாரங்கள் மற்றும் கேட்க வேண்டிய கேள்விகள் அடங்கிய எளிய அறிக்கையைப் பெறுங்கள்.'
                )}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Why Nilaayam AI? */}
      <section className="why-section container">
        <div style={{ textAlign: 'center', maxWidth: 680, margin: '0 auto 2.5rem' }}>
          <h2 className="section-title" style={{ justifyContent: 'center' }}>
            {t('Why Nilaayam AI?', 'நிலாயம் AI-ஐ ஏன் தேர்ந்தெடுக்க வேண்டும்?')}
          </h2>
          <p style={{ color: 'var(--color-text-muted)' }}>
            {t('Designed specifically for Tamil Nadu citizens, tenants, buyers, and legal researchers.', 'தமிழ்நாட்டு மக்கள் மற்றும் சொத்து வாங்குவோருக்காக பிரத்யேகமாக உருவாக்கப்பட்டது.')}
          </p>
        </div>

        <div className="why-grid">
          <div className="why-card">
            <div className="why-card-icon">
              <Languages size={32} style={{ color: 'var(--color-green)' }} />
            </div>
            <h3>{t('Bilingual Tamil & English', 'தமிழ் மற்றும் ஆங்கிலம்')}</h3>
            <p className="text-tamil">
              {t(
                'Switch effortlessly between English and Tamil. Read complex legal conditions translated into clear, simple everyday language.',
                'கடினமான சட்ட விதிகளை அன்றாட எளிய தமிழில் புரிந்துகொள்ளும் வகையில் தமிழாக்க ஆதரவு.'
              )}
            </p>
          </div>

          <div className="why-card">
            <div className="why-card-icon">
              <BookOpen size={32} style={{ color: 'var(--color-navy)' }} />
            </div>
            <h3>{t('Evidence-Backed Findings', 'சட்ட ஆதார அடிப்படையிலான தகவல்கள்')}</h3>
            <p>
              {t(
                'No hallucinations. Every flagged risk links directly to explicit statutory sections (such as TNRRRLT Act 2017 or Indian Contract Act).',
                'ஒவ்வொரு எச்சரிக்கையும் தமிழ்நாடு சட்டப் பிரிவுகளுடன் இணைக்கப்பட்ட நம்பகமான ஆதாரமாகும்.'
              )}
            </p>
          </div>

          <div className="why-card">
            <div className="why-card-icon">
              <Search size={32} style={{ color: 'var(--color-yellow)' }} />
            </div>
            <h3>{t('Multi-Document Triangulation', 'பல்வேறு ஆவணங்களின் ஒருங்கிணைப்பு')}</h3>
            <p>
              {t(
                'Don\'t rely on a single document. Compare Patta, EC, and Sale deed side-by-side to catch hidden subdivision changes.',
                'ஒரே ஆவணத்தை மட்டும் நம்பாமல், மூன்று முக்கிய ஆவணங்களை அருகருகே வைத்து முழுமையாக ஒப்பிடுங்கள்.'
              )}
            </p>
          </div>

          <div className="why-card">
            <div className="why-card-icon">
              <ShieldCheck size={32} style={{ color: 'var(--color-green-light)' }} />
            </div>
            <h3>{t('Accessible to Everyone', 'அனைவருக்கும் எளிதில் கிடைக்கும்')}</h3>
            <p>
              {t(
                'Democratizing preliminary document review so every citizen can enter transactions with eyes wide open.',
                'சட்ட விழிப்புணர்வை எளிய மக்களுக்கும் கொண்டு சென்று பாதுகாப்பான பரிவர்த்தனைகளை உறுதி செய்தல்.'
              )}
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container footer-content">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
            <span>🏘️ Nilaayam AI</span>
          </div>
          <p>
            {t(
              'Nilaayam AI © 2024 | AI-Assisted Document Review Tool | Not a legal service',
              'நிலாயம் AI © 2024 | AI-உதவி ஆவண மதிப்பாய்வு தளம் | இது சட்ட நிறுவனம் அல்ல'
            )}
          </p>
          <p style={{ fontSize: '0.8rem', color: '#64748b', maxWidth: 600 }}>
            {t(
              'This application does not provide formal legal counsel or represent clients in court. Findings must be verified by a licensed advocate.',
              'இந்த செயலி முறையான சட்ட ஆலோசகர் அல்ல. முடிவுகளை வழக்கறிஞரிடம் உறுதிப்படுத்திக் கொள்ளவும்.'
            )}
          </p>
        </div>
      </footer>
    </div>
  )
}
