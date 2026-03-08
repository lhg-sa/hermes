import { ref } from 'vue'

const DEFAULT_TIMEOUT = 30000
const DEFAULT_RETRIES = 0
const RETRY_DELAY = 1000

export function useApi() {
  const loading = ref(false)
  const error = ref(null)
  
  /**
   * Make a fetch request with timeout and retry support
   */
  async function request(url, options = {}) {
    const {
      timeout = DEFAULT_TIMEOUT,
      retries = DEFAULT_RETRIES,
      ...fetchOptions
    } = options
    
    let lastError = null
    
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        loading.value = true
        error.value = null
        
        // Create abort controller for timeout
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), timeout)
        
        const response = await fetch(url, {
          ...fetchOptions,
          signal: controller.signal,
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            ...fetchOptions.headers
          }
        })
        
        clearTimeout(timeoutId)
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        loading.value = false
        return data
        
      } catch (err) {
        lastError = err
        loading.value = false
        
        // Don't retry on abort (timeout)
        if (err.name === 'AbortError') {
          error.value = 'Tiempo de espera agotado'
          throw err
        }
        
        // Wait before retrying
        if (attempt < retries) {
          await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
        }
      }
    }
    
    error.value = lastError?.message || 'Error de conexión'
    throw lastError
  }
  
  /**
   * GET request
   */
  async function get(url, params = {}, options = {}) {
    const queryString = new URLSearchParams(params).toString()
    const fullUrl = queryString ? `${url}?${queryString}` : url
    
    return request(fullUrl, {
      ...options,
      method: 'GET'
    })
  }
  
  /**
   * POST request
   */
  async function post(url, data = {}, options = {}) {
    return request(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    })
  }
  
  /**
   * PUT request
   */
  async function put(url, data = {}, options = {}) {
    return request(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }
  
  /**
   * DELETE request
   */
  async function del(url, options = {}) {
    return request(url, {
      ...options,
      method: 'DELETE'
    })
  }
  
  /**
   * Call a Frappe API method
   */
  async function callMethod(method, data = {}, options = {}) {
    return post(`/api/method/${method}`, data, options)
  }
  
  /**
   * Get a document from Frappe
   */
  async function getDoc(doctype, name, options = {}) {
    return get(`/api/resource/${doctype}/${name}`, {}, options)
  }
  
  /**
   * Create or update a document
   */
  async function saveDoc(doc, options = {}) {
    return post('/api/resource/' + doc.doctype, doc, options)
  }
  
  return {
    loading,
    error,
    request,
    get,
    post,
    put,
    del,
    callMethod,
    getDoc,
    saveDoc
  }
}