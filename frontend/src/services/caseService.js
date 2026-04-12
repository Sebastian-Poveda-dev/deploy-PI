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
  return {
    id: raw.id,
    status: STATUS_MAP[raw.status] ?? raw.status.toUpperCase(),
    category: raw.category,
    createdAt: formatDate(raw.created_at),
    updatedAt: formatDate(raw.updated_at),
    assignedUsers: raw.assigned_users.map((u) => u.name).join(', '),
    description: raw.description ?? raw.details ?? '',
  }
}

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : ''
}

export async function createCase({ description, categoryId, subclinicId }) {
  const response = await fetch('/cases/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify({
      description,
      category_id: categoryId,
      subclinic_id: subclinicId,
    }),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible crear el caso.')
  }

  const raw = await response.json()
  return mapCase(raw)
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
