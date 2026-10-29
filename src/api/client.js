import axios from 'axios'
import { demoPropertyComparison, demoChecklist } from '../data/demoData'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.warn('API call failed, operating in fallback / demo mode if available:', error?.message)
    return Promise.reject(error)
  }
)

/**
 * Upload a document (Rental Agreement, Patta, EC, Sale Deed)
 */
export async function uploadDocument(file, onProgress, documentType) {
  const formData = new FormData()
  formData.append('file', file)
  if (documentType) {
    formData.append('document_type', documentType)
  }

  const response = await api.post('/api/documents', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percentCompleted)
      }
    }
  })
  return response.data
}

/**
 * Check document processing status
 */
export async function getDocumentStatus(id) {
  try {
    const response = await api.get(`/api/documents/${id}/status`)
    return response.data
  } catch (error) {
    return {
      document_id: id,
      status: 'completed',
      isDemoData: true
    }
  }
}

/**
 * Retrieve extracted OCR text and metadata
 */
export async function getExtractedData(id) {
  try {
    const response = await api.get(`/api/documents/${id}/extracted`)
    return response.data
  } catch (error) {
    return {
      document_id: id,
      text: 'Sample extracted text content for Tamil Nadu document.',
      pages: 4,
      isDemoData: true
    }
  }
}

/**
 * Run Agreement Risk Scanner analysis
 */
export async function analyzeAgreement(documentId, language = 'en') {
  const response = await api.post('/api/agreements/analyze', {
    document_id: documentId,
    language
  })
  return response.data
}

/**
 * Fetch complete Agreement Analysis report by ID
 */
export async function getAgreementReport(analysisId) {
  const response = await api.get(`/api/agreements/${analysisId}/report`)
  return response.data
}

/**
 * Run Property Documents Cross-Checker comparison
 */
export async function compareProperties(pattaId, ecId, saleDeedId, language = 'en') {
  try {
    const response = await api.post('/api/properties/compare', {
      patta_id: pattaId,
      ec_id: ecId,
      sale_deed_id: saleDeedId,
      language
    })
    return response.data
  } catch (error) {
    console.warn('Property comparison API unavailable, loading demo comparison data')
    return {
      comparison_id: demoPropertyComparison.id,
      ...demoPropertyComparison
    }
  }
}

/**
 * Fetch Property Comparison report by ID
 */
export async function getPropertyComparison(comparisonId) {
  try {
    const response = await api.get(`/api/properties/${comparisonId}/comparison`)
    return response.data
  } catch (error) {
    return {
      ...demoPropertyComparison,
      id: comparisonId || demoPropertyComparison.id
    }
  }
}

/**
 * Generate Registration Checklist
 */
export async function generateChecklist(propertyType = 'residential', transactionType = 'sale', language = 'en') {
  try {
    const response = await api.post('/api/properties/checklist', {
      property_type: propertyType,
      transaction_type: transactionType,
      language
    })
    return response.data
  } catch (error) {
    console.warn('Checklist API unavailable, returning standard Tamil Nadu registration checklist')
    return {
      property_type: propertyType,
      transaction_type: transactionType,
      items: demoChecklist,
      isDemoData: true
    }
  }
}

/**
 * Fetch legal statutory references
 */
export async function getLegalReferences() {
  try {
    const response = await api.get('/api/references')
    return response.data
  } catch (error) {
    return [
      { id: 'tnrrlt-2017', name: 'Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017' },
      { id: 'reg-act-1908', name: 'The Registration Act, 1908 & Tamil Nadu Amendments' },
      { id: 'stamp-act-1899', name: 'Indian Stamp Act, 1899 (Tamil Nadu Stamp Schedule)' }
    ]
  }
}

/**
 * Export report in PDF/JSON format
 */
export async function exportReport(reportId, format = 'pdf', language = 'en') {
  try {
    const response = await api.post(`/api/reports/${reportId}/export`, {
      format,
      language
    }, {
      responseType: format === 'pdf' ? 'blob' : 'json'
    })
    return response.data
  } catch (error) {
    // In fallback mode, return a dummy blob or message
    return new Blob(['Nilaayam AI Demo Report'], { type: 'application/pdf' })
  }
}

export default api
