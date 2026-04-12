export async function getCurrentUser() {
  const response = await fetch('/users/me/', {
    credentials: 'include',
  })
  if (!response.ok) return null
  return response.json()
}

export async function registerBeneficiary(payload) {
  const body = new URLSearchParams(payload)

  const response = await fetch('/users/register/', {
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

export async function getProfessors() {
  const response = await fetch('/users/professors/', {
    credentials: 'include',
  })
  if (!response.ok) return []
  return response.json()
}

export async function getBeneficiaries() {
  const response = await fetch('/users/beneficiaries/', {
    credentials: 'include',
  })
  if (!response.ok) return []
  return response.json()
}
