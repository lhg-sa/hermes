/**
 * Frappe API utility for authentication and API calls
 */

const API_URL = '' // Use relative URL for same-origin

/**
 * Login to Frappe/ERPNext
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<{success: boolean, token?: string, user?: string, message?: string}>}
 */
export async function login(email, password) {
  try {
    const response = await fetch('/api/method/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        usr: email,
        pwd: password
      }),
      credentials: 'include'
    })

    if (response.ok) {
      // Get session info
      const sessionResponse = await fetch('/api/method/frappe.auth.get_logged_user', {
        credentials: 'include'
      })
      
      if (sessionResponse.ok) {
        const sessionData = await sessionResponse.json()
        return {
          success: true,
          token: 'authenticated',
          user: sessionData.message
        }
      }
      
      return {
        success: true,
        token: 'authenticated',
        user: email
      }
    } else {
      const errorData = await response.json()
      return {
        success: false,
        message: errorData.message || 'Credenciales inválidas'
      }
    }
  } catch (error) {
    console.error('Login error:', error)
    return {
      success: false,
      message: 'Error de conexión'
    }
  }
}

/**
 * Make authenticated API call to Frappe
 * @param {string} method - Frappe method (e.g., 'frappe.auth.get_logged_user')
 * @param {object} params - Method parameters
 * @returns {Promise<any>}
 */
export async function call(method, params = {}) {
  try {
    const response = await fetch(`/api/method/${method}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
      credentials: 'include'
    })

    if (response.status === 403) {
      // Session expired or not authenticated
      localStorage.removeItem('hermes_token')
      localStorage.removeItem('hermes_user')
      throw new Error('SESSION_EXPIRED')
    }

    if (!response.ok) {
      throw new Error(`API call failed: ${response.status}`)
    }

    const data = await response.json()
    return data.message
  } catch (error) {
    if (error.message === 'SESSION_EXPIRED') {
      throw error
    }
    throw new Error(`Network error: ${error.message}`)
  }
}

/**
 * Check if user is logged in via Frappe session
 * @returns {Promise<{authenticated: boolean, user?: string}>}
 */
export async function checkAuth() {
  try {
    const response = await fetch('/api/method/hermes.api.check_session', {
      method: 'POST',
      credentials: 'include'
    })
    if (response.ok) {
      const data = await response.json()
      return { 
        authenticated: data.message?.authenticated === true,
        user: data.message?.user 
      }
    }
    return { authenticated: false }
  } catch (error) {
    console.error('checkAuth error:', error)
    return { authenticated: false }
  }
}

/**
 * Logout from Frappe
 * @returns {Promise<void>}
 */
export async function logout() {
  try {
    await fetch('/api/method/logout', {
      method: 'POST',
      credentials: 'include'
    })
  } catch (error) {
    console.error('Logout error:', error)
  }
}
