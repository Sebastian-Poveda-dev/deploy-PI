import { buildApiUrl } from './apiClient'

export async function getCurrentUser() {
  const response = await fetch(buildApiUrl('/users/me/'), {
    credentials: 'include',
  })
  if (!response.ok) return null
  return response.json()
}

export async function registerBeneficiary(payload) {
  const body = new URLSearchParams(payload)

  const response = await fetch(buildApiUrl('/users/register/'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    },
    body,
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw data
  }

  return data
}

export async function getUsers() {
  const response = await fetch(buildApiUrl('/users/'), { credentials: 'include' })
  if (!response.ok) throw new Error('No fue posible cargar los usuarios.')
  return response.json()
}

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : ''
}

export async function createUserAsAdmin({ username, password, role, category_id }) {
  const body = { username, password, role }
  if (category_id) body.category_id = category_id

  const response = await fetch(buildApiUrl('/users/'), {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
    body: JSON.stringify(body),
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail ?? 'No fue posible crear el usuario.')
  return data
}

export async function getCategories() {
  const response = await fetch(buildApiUrl('/cases/categories/'), { credentials: 'include' })
  if (!response.ok) return []
  return response.json()
}

export async function updateUserAsAdmin(userId, patch) {
  const response = await fetch(buildApiUrl(`/users/${userId}/`), {
    method: 'PATCH',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
    body: JSON.stringify(patch),
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail ?? 'No fue posible actualizar el usuario.')
  return data
}

export async function getBeneficiaries() {
  const response = await fetch(buildApiUrl('/users/beneficiaries/'), {
    credentials: 'include',
  })
  if (!response.ok) return []
  return response.json()
}

export async function getBeneficiary(userId) {
  const response = await fetch(buildApiUrl(`/users/${userId}/`), {
    credentials: 'include',
  })
  if (!response.ok) throw new Error('No fue posible cargar el beneficiario.')
  return response.json()
}

export async function updateBeneficiary(userId, data) {
  const response = await fetch(buildApiUrl(`/users/${userId}/`), {
    method: 'PATCH',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
    body: JSON.stringify(data),
  })
  const responseData = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(responseData.detail ?? 'No fue posible actualizar el beneficiario.')
  return responseData
}

