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
