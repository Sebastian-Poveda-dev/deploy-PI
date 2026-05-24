import { buildApiUrl } from './apiClient'

export async function getMetrics() {
  const response = await fetch(buildApiUrl('/metrics/'), {
    credentials: 'include',
  })
  if (!response.ok) throw new Error('Failed to fetch metrics')
  return response.json()
}

export async function searchStudentCases(query) {
  const url = buildApiUrl(`/metrics/student-cases/?q=${encodeURIComponent(query)}`)
  const response = await fetch(url, { credentials: 'include' })
  if (!response.ok) throw new Error('No fue posible realizar la búsqueda.')
  return response.json()
}
