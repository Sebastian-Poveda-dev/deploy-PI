import { buildApiUrl } from './apiClient'

const STATUS_MAP = {
  active: 'ACTIVE',
  pending_authorization: 'PENDING',
  in_progress: 'IN_PROGRESS',
  finished: 'INACTIVE',
  inactive: 'INACTIVE',
  canceled: 'CANCELLED',
}

function formatDate(isoString) {
  if (!isoString) return '—'
  return isoString.split('T')[0]
}

function mapCase(raw) {
  const assignedUsersList = Array.isArray(raw.assigned_users)
    ? raw.assigned_users.map((u) => u.name)
    : []

  return {
    id: raw.id,
    status: STATUS_MAP[raw.status] ?? raw.status.toUpperCase(),
    category: raw.category,
    createdAt: formatDate(raw.created_at),
    updatedAt: formatDate(raw.updated_at),
    beneficiaryId: raw.beneficiary,
    beneficiaryName: raw.beneficiary_name ?? '',
    assignedUsersList,
    assignedUsers: assignedUsersList.join(', '),
    description: raw.description ?? raw.details ?? '',
    pendingCancellation: raw.pending_cancellation_request,
  }
}

function mapBeneficiaryCase(raw) {
  return {
    id: raw.id,
    status: STATUS_MAP[raw.status] ?? raw.status.toUpperCase(),
    progressStatuses: Array.isArray(raw.progress_statuses) ? raw.progress_statuses : [],
  }
}

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : ''
}

export async function createCase({ description, categoryId, subclinicId, beneficiaryId, isImmediate, immediateResolution, attendedById }) {
  const body = {
    description,
    category_id: categoryId,
    subclinic_id: subclinicId,
    beneficiary_id: beneficiaryId,
    is_immediate: isImmediate ?? false,
  }
  if (isImmediate) {
    body.immediate_resolution = immediateResolution ?? ''
    if (attendedById) body.attended_by_id = attendedById
  }

  const response = await fetch(buildApiUrl('/cases/'), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible crear el caso.')
  }

  const raw = await response.json()
  return mapCase(raw)
}

export async function approveCase(caseId) {
  const response = await fetch(buildApiUrl(`/cases/${caseId}/approve/`), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible aprobar el caso.')
  }

  return mapCase(await response.json())
}

export async function rejectCase(caseId) {
  const response = await fetch(buildApiUrl(`/cases/${caseId}/reject-assignment/`), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible rechazar la asignación.')
  }
}

export async function getCases() {
  const response = await fetch(buildApiUrl('/cases/'), {
    method: 'GET',
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error('Failed to fetch cases')
  }

  const data = await response.json()
  return data.map(mapCase)
}

export async function getBeneficiaryCases() {
  const response = await fetch(buildApiUrl('/cases/beneficiary/'), {
    method: 'GET',
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error('No fue posible cargar el estado del caso.')
  }

  const data = await response.json()
  const cases = Array.isArray(data) ? data : data.cases ?? []

  return {
    cases: cases.map(mapBeneficiaryCase),
    detail: data.detail ?? '',
  }
}

export async function trackBeneficiaryCases(identificationNumber) {
  const response = await fetch(buildApiUrl('/cases/track/'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ identification_number: identificationNumber }),
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail ?? 'No fue posible consultar el estado del caso.')
  }

  return {
    cases: Array.isArray(data.cases) ? data.cases.map(mapBeneficiaryCase) : [],
    detail: data.detail ?? '',
  }
}

export async function requestCancellation(caseId, reason) {
  const response = await fetch(buildApiUrl(`/cases/${caseId}/request-cancellation/`), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify({ reason }),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible solicitar la reasignación.')
  }

  return await response.json()
}

export async function reviewCancellation(requestId, action) {
  const response = await fetch(buildApiUrl(`/cases/cancellation-requests/${requestId}/review/`), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify({ action }),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible procesar la solicitud.')
  }

  return await response.json()
}

export const CANCELLATION_REASONS = [
  { value: 'DESISTIMIENTO_TACITO', label: 'Desistimiento tácito del usuario' },
  { value: 'DESISTIMIENTO_EXPRESO', label: 'Desistimiento expreso del usuario' },
  { value: 'FINALIZADO_GANADO', label: 'Caso finalizado jurídicamente (ganado)' },
  { value: 'FINALIZADO_PERDIDO', label: 'Caso finalizado jurídicamente (perdido)' },
  { value: 'INFRINGIO_TERMINOS', label: 'Infringió los términos del consultorio jurídico' },
  { value: 'OTRO', label: 'Otro' },
]

export async function cancelCase(caseId, reason, reasonOther) {
  const body = { reason }
  if (reason === 'OTRO' && reasonOther) body.reason_other = reasonOther

  const response = await fetch(buildApiUrl(`/cases/${caseId}/cancel/`), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible cancelar el caso.')
  }

  return mapCase(await response.json())
}

export async function getCancellationNotifications() {
  const response = await fetch(buildApiUrl('/cases/cancellation-request-notifications/'), {
    credentials: 'include',
  })
  if (!response.ok) return []
  return response.json()
}

export async function markCancellationNotificationRead(id) {
  await fetch(buildApiUrl(`/cases/cancellation-request-notifications/${id}/read/`), {
    method: 'PATCH',
    credentials: 'include',
    headers: { 'X-CSRFToken': getCsrfToken() },
  })
}

export async function getSubclinics(categoryId) {
  const url = categoryId
    ? buildApiUrl(`/cases/subclinics/?category_id=${categoryId}`)
    : buildApiUrl('/cases/subclinics/')
  const response = await fetch(url, { credentials: 'include' })
  if (!response.ok) return []
  return response.json()
}

export async function getCaseProgressStatuses(caseId) {
  const response = await fetch(buildApiUrl(`/cases/${caseId}/progress-statuses/`), {
    credentials: 'include',
  })
  if (!response.ok) throw new Error('No fue posible cargar el progreso del caso.')
  return response.json()
}

export async function addCaseProgressStatus(caseId, label) {
  const response = await fetch(buildApiUrl(`/cases/${caseId}/progress-statuses/`), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify({ label }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible agregar el estado.')
  }
  return response.json()
}
