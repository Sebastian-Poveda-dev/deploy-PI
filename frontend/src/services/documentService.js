function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : ''
}

function formatDate(isoString) {
  if (!isoString) return null
  return isoString.split('T')[0]
}

function mapDocument(raw) {
  return {
    id: raw.id,
    name: raw.name,
    description: raw.description,
    uploadedAt: formatDate(raw.uploaded_at),
    uploadedBy: raw.uploaded_by,
    expirationDate: formatDate(raw.expiration_date),
  }
}

function mapNotification(raw) {
  return {
    id: raw.id,
    documentId: raw.document_id,
    documentName: raw.document_name,
    caseId: raw.case_id,
    caseDescription: raw.case_description,
    eventType: raw.event_type,
    priority: raw.priority,
    message: raw.message,
    createdAt: raw.created_at,
    expirationDate: raw.expiration_date,
    daysUntilExpiration: raw.days_until_expiration,
  }
}

export async function getDocumentsByCase(caseId) {
  const response = await fetch(`/cases/${caseId}/documents/`, {
    method: 'GET',
    credentials: 'include',
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible cargar los documentos.')
  }

  const data = await response.json()
  return data.map(mapDocument)
}

export async function uploadDocument(caseId, formData) {
  const response = await fetch(`/cases/${caseId}/documents/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRFToken': getCsrfToken(),
    },
    body: formData,
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible subir el documento.')
  }

  const raw = await response.json()
  return mapDocument(raw)
}

export async function downloadDocument(documentId, documentName) {
  const response = await fetch(`/documents/${documentId}/download/`, {
    method: 'GET',
    credentials: 'include',
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible descargar el documento.')
  }

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = documentName
  anchor.click()
  URL.revokeObjectURL(url)
}

export async function getDocumentNotifications() {
  const response = await fetch('/documents/notifications/', {
    method: 'GET',
    credentials: 'include',
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? 'No fue posible cargar los avisos importantes.')
  }

  const data = await response.json()
  return data.map(mapNotification)
}

export async function triggerDocumentNotificationCheck(payload = {}) {
  const response = await fetch('/documents/notifications/check/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(payload),
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail ?? 'No fue posible actualizar las notificaciones.')
  }

  return data
}
