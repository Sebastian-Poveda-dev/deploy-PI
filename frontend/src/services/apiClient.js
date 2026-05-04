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
