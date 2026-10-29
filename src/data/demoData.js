/**
 * Nilaayam AI Demo Data
 * Contains realistic Tamil Nadu tenancy and land registration sample data
 */

export const demoAgreementAnalysis = {
  id: 'demo-agr-101',
  isDemoData: true,
  document_name: 'Sample_Rental_Agreement_Chennai.pdf',
  uploaded_at: '2025-02-15T10:30:00Z',
  overall_status: 'High Risk Clauses Detected',
  overall_status_ta: 'அதிக ஆபத்துள்ள பிரிவுகள் கண்டறியப்பட்டுள்ளன',
  stats: {
    total_findings: 6,
    red_count: 3,
    yellow_count: 2,
    green_count: 1,
    grey_count: 0
  },
  summary: {
    risk_summary: 'The agreement contains 3 critical clauses that contradict the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017 (TNRRRLT Act). Specifically, it includes an excessive 10-month security deposit demand, an unfair 30-day eviction without grounds, and unilateral forfeiture of the entire deposit.',
    risk_summary_ta: 'இந்த வாடகை ஒப்பந்தத்தில் தமிழ்நாடு உரிமைகள் மற்றும் பொறுப்புகள் ஒழுங்குமுறை சட்டம் 2017 (TNRRRLT Act) விதிகளுக்கு முரணான 3 கடுமையான பிரிவுகள் உள்ளன. குறிப்பாக, 10 மாத முன்பணம் கோரிக்கை, காரணமின்றி 30 நாள் வெளியேற்ற நிபந்தனை மற்றும் முன்பணத்தை தன்னிச்சையாக பறிமுதல் செய்யும் விதி உள்ளன.'
  },
  findings: [
    {
      id: 'f-1',
      severity: 'red',
      category: 'Security Deposit Limit',
      clause_number: 4,
      original_text: 'The Tenant shall deposit a sum of Rs. 2,00,000 (equivalent to 10 months rent) with the Landlord as an interest-free advance security deposit, which shall be retained throughout the tenancy.',
      explanation: 'Demanding 10 months rent as security deposit violates Tamil Nadu tenancy regulations. Under TN law, the maximum allowable security deposit for residential premises is strictly capped at three times the monthly rent.',
      explanation_ta: '10 மாத வாடகையை முன்பணமாகக் கோருவது தமிழ்நாடு வாடகை சட்ட விதிகளுக்கு எதிரானது. தமிழ்நாடு சட்டப்படி, குடியிருப்பு வளாகங்களுக்கு அதிகபட்சமாக 3 மாத வாடகை மட்டுமே முன்பணமாக பெறப்பட வேண்டும்.',
      reason: 'Excessive advance locks up significant tenant capital and contradicts statutory protections intended to safeguard tenants from unfair financial lock-in.',
      reason_ta: 'அதிகப்படியான முன்பணம் வாடகைதாரரின் பணத்தை முடக்குகிறது மற்றும் சட்டப்பூர்வ உச்சவரம்பை மீறுகிறது.',
      legal_source: 'Tamil Nadu Act 42 of 2017 (TNRRRLT Act) — Section 13(1)',
      legal_source_url: 'https://www.tenancy.tn.gov.in/',
      suggested_question: 'Can we adjust the security deposit to 3 months of rent (Rs. 60,000) as mandated under Section 13 of the TNRRRLT Act 2017?',
      suggested_question_ta: 'TNRRRLT சட்டம் 2017 பிரிவு 13-ன் படி முன்பணத்தை 3 மாத வாடகையாக (ரூ. 60,000) குறைக்க முடியுமா?'
    },
    {
      id: 'f-2',
      severity: 'red',
      category: 'Unilateral Termination & Eviction',
      clause_number: 11,
      original_text: 'The Landlord reserves the absolute right to terminate this tenancy at any time by giving 15 days written notice without assigning any reason whatsoever, and the tenant shall vacate immediately upon expiry of said notice.',
      explanation: 'The landlord cannot evict a tenant arbitrarily or on short 15-day notice without statutory grounds (such as default in rent or structural repair necessity) recognized under the Tenancy Court framework.',
      explanation_ta: 'சட்டப்பூர்வ காரணமின்றி வெறும் 15 நாள் நோட்டீஸ் மூலம் வாடகைதாரரை தன்னிச்சையாக வெளியேற்றும் உரிமை நில உரிமையாளருக்கு கிடையாது.',
      reason: 'Arbitrary short-notice eviction creates acute housing instability and bypasses the Rent Court dispute resolution mechanisms established by Tamil Nadu law.',
      reason_ta: 'திடீர் வெளியேற்ற நிபந்தனை வாடகைதாரரின் பாதுகாப்பைப் பறித்து வாடகை நீதிமன்ற நடைமுறைகளை புறக்கணிக்கிறது.',
      legal_source: 'TNRRRLT Act 2017 — Section 21 (Protection Against Eviction)',
      legal_source_url: 'https://www.tenancy.tn.gov.in/',
      suggested_question: 'Could we revise this to a mutual 2-month notice period requiring legitimate grounds aligned with Section 21 of the TN Tenancy Act?',
      suggested_question_ta: 'இருதரப்பு ஒப்புதலுடன் 2 மாத நோட்டீஸ் காலத்தை மாற்றியமைக்க முடியுமா?'
    },
    {
      id: 'f-3',
      severity: 'red',
      category: 'Security Deposit Forfeiture',
      clause_number: 14,
      original_text: 'In the event the Tenant terminates this agreement prior to the completion of the 11-month lock-in period, the entire security deposit of Rs. 2,00,000 shall be unconditionally forfeited to the Landlord as liquidated damages.',
      explanation: 'Complete forfeiture of security deposit without proving actual damages or unpaid rent is punitive and unlawful under Indian Contract Law. Deposits can only cover actual unpaid arrears or proven physical damages.',
      explanation_ta: 'உண்மையான இழப்பீடு அல்லது வாடகை பாக்கி இல்லாமல் முழு முன்பணத்தையும் பறிமுதல் செய்வது இந்திய ஒப்பந்தச் சட்டத்தின் கீழ் தண்டனைக்குரியதும் சட்டவிரோதமானதும் ஆகும்.',
      reason: 'Penalty clauses that exceed reasonable compensation are void under Section 74 of the Indian Contract Act.',
      reason_ta: 'உண்மையான சேதத்தை விட கூடுதலான அபராதத்தை பறிமுதல் செய்வது சட்டப்படி செல்லாது.',
      legal_source: 'Indian Contract Act, 1872 — Section 74 (Compensation for Breach)',
      legal_source_url: 'https://indiankanoon.org/doc/171398/',
      suggested_question: 'Can the forfeiture clause be modified so deductions are limited strictly to actual unpaid utility bills or verified physical damage?',
      suggested_question_ta: 'உண்மையான வாடகை பாக்கி அல்லது பராமரிப்பு சேதங்களுக்கு மட்டுமே முன்பணத்தில் கழிக்கப்படும் என மாற்றலாமா?'
    },
    {
      id: 'f-4',
      severity: 'yellow',
      category: 'Structural Maintenance & Repairs',
      clause_number: 8,
      original_text: 'All internal and external repairs, including plumbing leakages, electrical wiring faults, external wall seepage, and whitewashing shall be carried out entirely at the tenant\'s expense.',
      explanation: 'Major structural repairs, external seepage, and roof leakages are standard landlord obligations under the Second Schedule of the TNRRRLT Act, while tenant responsibility is typically limited to routine minor wear and tear.',
      explanation_ta: 'கட்டடத்தின் பெரிய கட்டமைப்பு பழுதுகள் மற்றும் வெளிப்புற கசிவுகள் உரிமையாளரின் பொறுப்பாகும். வாடகைதாரர் சிறு பழுதுகளை மட்டுமே ஏற்க வேண்டும்.',
      reason: 'Transferring capital maintenance duties onto a residential lessee leads to disputes over preexisting structural defects.',
      reason_ta: 'கட்டடத்தின் முதன்மைப் பராமரிப்பை வாடகைதாரர் மீது சுமத்துவது எதிர்காலப் பூசல்களுக்கு வழிவகுக்கும்.',
      legal_source: 'TNRRRLT Act 2017 — Section 15 & Schedule II (Division of Maintenance Responsibilities)',
      legal_source_url: 'https://www.tenancy.tn.gov.in/',
      suggested_question: 'Can we specify that structural/external repairs remain the landlord\'s responsibility, with tenant handling minor consumable replacements up to Rs. 1,000?',
      suggested_question_ta: 'கட்டமைப்பு பழுதுகள் உரிமையாளருக்கும், சிறு பழுதுகள் மட்டுமே வாடகைதாரருக்கும் என பிரிக்க முடியுமா?'
    },
    {
      id: 'f-5',
      severity: 'yellow',
      category: 'Mandatory Portal Registration',
      clause_number: 16,
      original_text: 'This agreement is executed on a Rs. 100 non-judicial stamp paper and notarized. Neither party shall be obligated to register this agreement before any government authority.',
      explanation: 'Under Section 4(1) of the TNRRRLT Act 2017, all tenancy agreements MUST be registered with the Tenancy Portal (tenancy.tn.gov.in) within 90 days of execution. Failure to register bars either party from seeking relief from Rent Courts.',
      explanation_ta: 'TNRRRLT சட்டம் 2017 பிரிவு 4(1)-ன் படி அனைத்து வாடகை ஒப்பந்தங்களும் 90 நாட்களுக்குள் தமிழக வாடகை போர்ட்டலில் பதிவு செய்யப்பட வேண்டும்.',
      reason: 'Unregistered tenancy agreements cannot be admitted as valid evidence in Rent Court proceedings in Tamil Nadu.',
      reason_ta: 'பதிவு செய்யப்படாத ஒப்பந்தங்கள் வாடகை நீதிமன்றத்தில் ஆதாரமாக ஏற்றுக்கொள்ளப்படாது.',
      legal_source: 'TNRRRLT Act 2017 — Section 4(1) & Rule 3',
      legal_source_url: 'https://www.tenancy.tn.gov.in/',
      suggested_question: 'Will we be jointly filing this agreement on the Tamil Nadu Tenancy portal (tenancy.tn.gov.in) within the statutory 90-day window?',
      suggested_question_ta: 'இந்த ஒப்பந்தத்தை 90 நாட்களுக்குள் தமிழ்நாடு வாடகை போர்ட்டலில் (tenancy.tn.gov.in) பதிவு செய்வோமா?'
    },
    {
      id: 'f-6',
      severity: 'green',
      category: 'Rent Payment & Due Date',
      clause_number: 2,
      original_text: 'The monthly rent of Rs. 20,000 shall be paid on or before the 5th day of each English calendar month by electronic bank transfer to the Landlord\'s designated bank account against a valid written or digital receipt.',
      explanation: 'Clear rent payment terms, designated bank mode, and explicit provision for rent receipts align perfectly with fair tenancy standards and statutory receipt mandates.',
      explanation_ta: 'மாத வாடகை தேதி, வங்கி பரிமாற்ற முறை மற்றும் ரசீது வழங்கும் நிபந்தனை நியாயமாகவும் சட்ட விதிகளுக்கு இணங்கவும் உள்ளது.',
      reason: 'Protects both parties by establishing an unambiguous paper trail for all rental transactions.',
      reason_ta: 'இருதரப்புக்கும் வாடகை செலுத்தியதற்கான வெளிப்படையான ஆதாரத்தை உறுதி செய்கிறது.',
      legal_source: 'TNRRRLT Act 2017 — Section 10 (Rent Receipt Mandatory)',
      legal_source_url: 'https://www.tenancy.tn.gov.in/',
      suggested_question: 'Standard terms; no modification required.',
      suggested_question_ta: 'சரியான விதி; மாற்றம் தேவையில்லை.'
    }
  ],
  questions_to_ask: [
    'Can we reduce the security deposit from 10 months to 3 months (Rs. 60,000) as per Section 13(1) of TNRRRLT Act 2017?',
    'Will you agree to a mutual 2-month notice period for vacation, rather than the unilateral 15-day clause?',
    'Can we clarify that the deposit is non-forfeitable except for actual proven damages and outstanding electricity/water arrears?',
    'Who will be responsible for filing the agreement on tenancy.tn.gov.in and sharing the portal registration token?',
    'Can the maintenance clause explicitly assign major external and plumbing repairs to the landlord?'
  ]
}

export const demoPropertyComparison = {
  id: 'demo-prop-202',
  isDemoData: true,
  summary: {
    match_count: 2,
    mismatch_count: 1,
    flags_count: 1,
    overall_verdict: 'Survey Number Mismatch Detected — Official Verification Required',
    overall_verdict_ta: 'சர்வே எண் வேறுபாடு கண்டறியப்பட்டுள்ளது — வருவாய்த் துறை சரிபார்ப்பு அவசியம்'
  },
  documents_analyzed: [
    { type: 'Patta', filename: 'Patta_Tamil_Nadu_No_1842.pdf', date: '2024-01-10' },
    { type: 'Encumbrance Certificate (EC)', filename: 'EC_Form15_2010_2024.pdf', date: '2024-08-14' },
    { type: 'Sale Deed', filename: 'Parent_Sale_Deed_Doc_452_2018.pdf', date: '2018-05-22' }
  ],
  comparisons: [
    {
      field: 'Survey Number',
      field_label: 'Survey Number / உட்பிரிவு எண்',
      field_ta: 'சர்வே எண்',
      patta: { value: '142/3B', page: 1, confidence: 0.98 },
      ec: { value: '142/3A', page: 2, confidence: 0.94 },
      sale_deed: { value: '142/3B', page: 4, confidence: 0.99 },
      status: 'mismatch',
      notes: 'EC lists Survey No. 142/3A while Patta and Sale Deed list 142/3B. This could indicate a subdivision discrepancy or encumbrance search on adjacent parcel.'
    },
    {
      field: 'Owner Name',
      field_label: 'Current Owner / நில உரிமையாளர்',
      field_ta: 'உரிமையாளர் பெயர்',
      patta: { value: 'K. S. Ramanathan', page: 1, confidence: 0.96 },
      ec: { value: 'K. S. Ramanathan', page: 1, confidence: 0.97 },
      sale_deed: { value: 'K. S. Ramanathan', page: 2, confidence: 0.99 },
      status: 'match',
      notes: 'All documents consistently name K. S. Ramanathan as current title holder.'
    },
    {
      field: 'Total Extent / Area',
      field_label: 'Plot Area / பரப்பளவு',
      field_ta: 'நிலத்தின் பரப்பளவு',
      patta: { value: '2,400 sq.ft (5.5 cents)', page: 1, confidence: 0.95 },
      ec: { value: '2,400 sq.ft', page: 3, confidence: 0.92 },
      sale_deed: { value: '2,400 sq.ft (5.5 cents)', page: 3, confidence: 0.98 },
      status: 'match',
      notes: 'Extent matches exactly across Patta, EC schedule, and Sale deed recital.'
    }
  ],
  red_flags: [
    {
      id: 'rf-1',
      severity: 'high',
      title: 'Survey Subdivision Discrepancy (142/3B vs 142/3A)',
      title_ta: 'சர்வே உட்பிரிவு எண் முரண்பாடு (142/3B மற்றும் 142/3A)',
      description: 'The Encumbrance Certificate obtained from Inspector General of Registration (TNREGINET) lists transaction entries for Survey No. 142/3A, whereas both the computerised Patta (Anytime/Anywhere e-Patta) and the registered Sale Deed specify Survey No. 142/3B.',
      description_ta: 'பதிவுத் துறை வில்லங்கச் சான்றிதழில் சர்வே எண் 142/3A எனவும், கணினி பட்டா மற்றும் கிரயப் பத்திரத்தில் 142/3B எனவும் குறிப்பிடப்பட்டுள்ளது.',
      recommendation: 'Request a fresh Encumbrance Certificate specifically indexing Survey No. 142/3B from the Sub-Registrar Office, and inspect the Village FMB (Field Measurement Book) sketch at the Taluk Office to confirm the subdivision boundaries.',
      recommendation_ta: 'சார்-பதிவாளர் அலுவலகத்தில் சர்வே எண் 142/3B-க்கு புதிய வில்லங்கச் சான்று பெற்று, வட்டாட்சியர் அலுவலகத்தில் FMB வரைபடத்தை சரிபார்க்கவும்.',
      badge_text: 'Requires official verification',
      badge_text_ta: 'அரசுத் துறை சரிபார்ப்பு அவசியம்'
    }
  ]
}

export const demoChecklist = [
  {
    id: 'chk-1',
    name: 'Original Parent Title Deed & Chain Documents',
    name_ta: 'அசல் தாய் பத்திரம் மற்றும் முந்தைய ஆவணங்கள்',
    status: 'Obtained',
    is_mandatory: true,
    why_needed: 'Establishes continuous, unbroken chain of ownership for minimum 30 years prior to transaction.',
    why_needed_ta: 'குறைந்தது 30 ஆண்டுகளுக்கான தடையற்ற உரிமைத் தொடர்ச்சியை நிரூபிக்க அவசியம்.',
    official_source: 'Tamil Nadu Registration Act, 1908 — Section 17',
    official_source_url: 'https://tnreginet.gov.in/',
    last_verified: '2024-11-01',
    notes: 'Verify original documents; never rely solely on photocopies.'
  },
  {
    id: 'chk-2',
    name: 'Encumbrance Certificate (EC) for 30+ Years',
    name_ta: '30 ஆண்டுகளுக்கான வில்லங்கச் சான்றிதழ் (EC)',
    status: 'Obtained',
    is_mandatory: true,
    why_needed: 'Confirms that the property is free from undisclosed mortgages, court attachments, or prior sale agreements.',
    why_needed_ta: 'சொத்தின் மீது அடமானம், நீதிமன்ற ஜப்தி அல்லது வில்லங்கம் இல்லை என்பதை உறுதிப்படுத்த.',
    official_source: 'TNREGINET — Form No. 15',
    official_source_url: 'https://tnreginet.gov.in/',
    last_verified: '2024-10-15',
    notes: 'Must cover from 1994 up to the date of registration.'
  },
  {
    id: 'chk-3',
    name: 'Online Computerised Patta Transfer / Chitta Extract',
    name_ta: 'கணினி பட்டா மற்றும் சிட்டா நகல்',
    status: 'Pending',
    is_mandatory: true,
    why_needed: 'Proves current revenue ownership in Tamil Nadu Government Revenue records (Tamil Nilam portal).',
    why_needed_ta: 'தமிழ் நிலம் வருவாய்த் துறை பதிவேடுகளில் தற்போதைய உரிமையை நிரூபிக்க.',
    official_source: 'TN e-Services (eservices.tn.gov.in)',
    official_source_url: 'https://eservices.tn.gov.in/eservicesnew/land/chitta.html',
    last_verified: '2024-11-15',
    notes: 'Ensure the seller\'s name is explicitly registered in the Patta before executing deed.'
  },
  {
    id: 'chk-4',
    name: 'Field Measurement Book (FMB) Sketch',
    name_ta: 'நில அளவை வரைபடம் (FMB Sketch)',
    status: 'Needs Verification',
    is_mandatory: true,
    why_needed: 'Demarcates exact physical boundaries, subdivisions, and measurements of the land parcel.',
    why_needed_ta: 'நிலத்தின் எல்லைகள், அளவுகள் மற்றும் அமைப்பை துல்லியமாக அறிய.',
    official_source: 'Survey and Land Records Dept, Tamil Nadu',
    official_source_url: 'https://eservices.tn.gov.in/',
    last_verified: '2024-09-20',
    notes: 'Survey subdivision mismatch noted between EC and Patta.'
  },
  {
    id: 'chk-5',
    name: 'Property Tax Receipts (Up to Date)',
    name_ta: 'சொத்து வரி ரசீதுகள் (நடப்பு ஆண்டு வரை)',
    status: 'Obtained',
    is_mandatory: true,
    why_needed: 'Demonstrates physical possession and absence of civic municipal property tax arrears.',
    why_needed_ta: 'உள்ளாட்சி மன்ற வரி பாக்கிகள் இல்லை என்பதையும் உடைமையையும் நிரூபிக்க.',
    official_source: 'Greater Chennai Corporation / Respective Municipality',
    official_source_url: 'https://chennaicorporation.gov.in/',
    last_verified: '2024-10-01',
    notes: 'Demand receipt for the current half-year.'
  },
  {
    id: 'chk-6',
    name: 'Aadhaar & PAN Cards of Buyer and Seller',
    name_ta: 'வாங்குபவர் மற்றும் விற்பனையாளரின் ஆதார் & பான் கார்டுகள்',
    status: 'Obtained',
    is_mandatory: true,
    why_needed: 'Compulsory biometric identity verification at the Sub-Registrar Office (SRO) for fraud prevention.',
    why_needed_ta: 'சார்-பதிவாளர் அலுவலகத்தில் பயோமெட்ரிக் சரிபார்ப்புக்கு கட்டாயம்.',
    official_source: 'Registration Department of Tamil Nadu Guidelines',
    official_source_url: 'https://tnreginet.gov.in/',
    last_verified: '2024-11-10',
    notes: 'PAN is mandatory for transactions above Rs. 10 Lakhs (Form 60/61 if PAN unavailable).'
  },
  {
    id: 'chk-7',
    name: 'DTCP / CMDA Approved Layout Plan',
    name_ta: 'DTCP அல்லது CMDA அங்கீகரிக்கப்பட்ட மனை வரைபடம்',
    status: 'Needs Verification',
    is_mandatory: true,
    why_needed: 'Unapproved layouts cannot be registered under Section 22-A of the Registration (TN Amendment) Act, 2016.',
    why_needed_ta: 'அங்கீகரிக்கப்படாத மனைகள் பதிவுச் சட்டம் 22-A படி பதிவு செய்யப்பட முடியாது.',
    official_source: 'Section 22-A, TN Registration Amendment Act 2016',
    official_source_url: 'https://tnreginet.gov.in/',
    last_verified: '2024-10-30',
    notes: 'Verify layout approval number directly on CMDA/DTCP portal.'
  },
  {
    id: 'chk-8',
    name: 'TNEB Electricity Bill & Water Connection Proof',
    name_ta: 'மின் கட்டண ரசீது மற்றும் குடிநீர் இணைப்பு அட்டை',
    status: 'Pending',
    is_mandatory: false,
    why_needed: 'Confirms active utility services and facilitates smooth name transfer post-registration.',
    why_needed_ta: 'பயன்பாட்டு சேவைகள் இருப்பதையும், பதிவு செய்தபின் பெயர் மாற்றம் செய்வதையும் எளிதாக்குகிறது.',
    official_source: 'TANGEDCO / CMWSSB',
    official_source_url: 'https://www.tangedco.org/',
    last_verified: '2024-10-25',
    notes: 'Check for pending high-tariff arrears.'
  }
]
