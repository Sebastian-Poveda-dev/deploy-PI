import { buildApiUrl } from './apiClient'

export async function getMetrics() {
  const response = await fetch(buildApiUrl('/metrics/'), {
    credentials: 'include',
  })
  if (!response.ok) throw new Error('Failed to fetch metrics')
  return response.json()
}
