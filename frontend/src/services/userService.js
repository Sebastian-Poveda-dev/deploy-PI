export async function getCurrentUser() {
  const response = await fetch('/users/me/', {
    credentials: 'include',
  })
  if (!response.ok) return null
  return response.json()
}

export async function getProfessors() {
  const response = await fetch('/users/professors/', {
    credentials: 'include',
  })
  if (!response.ok) return []
  return response.json()
}
