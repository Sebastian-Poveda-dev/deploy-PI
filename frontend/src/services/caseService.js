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
  }
}

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : ''
}

export async function createCase({ description, categoryId, subclinicId, beneficiaryId }) {
  const body = {
    description,
    category_id: categoryId,
    subclinic_id: subclinicId,
    beneficiary_id: beneficiaryId,
  }

  const response = await fetch('/cases/', {
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
  const response = await fetch(`/cases/${caseId}/approve/`, {
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
  const response = await fetch(`/cases/${caseId}/reject-assignment/`, {
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
  const response = await fetch('/cases/', {
    method: 'GET',
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error('Failed to fetch cases')
  }

  const data = await response.json()
  return data.map(mapCase)
}
