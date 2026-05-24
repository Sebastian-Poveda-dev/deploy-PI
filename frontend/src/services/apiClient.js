const rawApiBaseUrl = import.meta.env.VITE_API_URL ?? ''
const apiBaseUrl = rawApiBaseUrl.replace(/\/+$/, '')

function normalizePath(path) {
  return path.startsWith('/') ? path : `/${path}`
}

export function buildApiUrl(path) {
  const normalized = normalizePath(path)
  if (!apiBaseUrl) return normalized
  return `${apiBaseUrl}${normalized}`
}

// CSRF token — in cross-origin deployments the csrftoken cookie is set on the
// backend domain and is not readable by JS on the frontend domain, so we fetch
// it explicitly from /csrf/ and cache it in memory.
let _csrfToken = ''

export async function initCsrf() {
  try {
    const response = await fetch(buildApiUrl('/csrf/'), { credentials: 'include' })
    if (response.ok) {
      const data = await response.json()
      _csrfToken = data.csrfToken ?? ''
    }
  } catch {
    // silently ignore — getCsrfToken will fall back to cookie (works locally)
  }
}

export function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : _csrfToken
}

export function buildWsUrl(path) {
  const normalized = normalizePath(path)
  const rawWsBaseUrl = import.meta.env.VITE_WS_URL ?? ''
  const wsBaseUrl = rawWsBaseUrl.replace(/\/+$/, '')

  if (wsBaseUrl) {
    return `${wsBaseUrl}${normalized}`
  }

  if (apiBaseUrl) {
    const wsFromApi = apiBaseUrl.replace(/^http/, 'ws')
    return `${wsFromApi}${normalized}`
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}${normalized}`
}
