import { buildApiUrl } from './apiClient'

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : ''
}

function formatDateTime(isoString) {
  if (!isoString) return '—'

  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) return isoString

  return date.toLocaleString('es-CO', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function mapLog(raw) {
  return {
    id: raw.id,
    content: raw.content,
    createdAt: formatDateTime(raw.created_at),
    createdById: raw.created_by,
    userName: raw.created_by_name ?? `Usuario #${raw.created_by}`,
    isCurrentUser: Boolean(raw.is_current_user),
  }
}

export async function getLogs(caseId) {
  const response = await fetch(buildApiUrl(`/cases/${caseId}/logs/`), {
    method: 'GET',
    credentials: 'include',
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible cargar el seguimiento del caso.')
  }

  const data = await response.json()
  return data.map(mapLog)
}

export async function createLog(caseId, data) {
  const response = await fetch(buildApiUrl(`/cases/${caseId}/logs/`), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail ?? 'No fue posible enviar el comentario.')
  }

  const raw = await response.json()
  return mapLog(raw)
}