import { buildApiUrl } from './apiClient'

export function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : ''
}

async function readJson(response) {
  return response.json().catch(() => ({}))
}

function messageFrom(data, fallback) {
  return data.detail ?? data.message ?? fallback
}

export async function getChatUsers() {
  const response = await fetch(buildApiUrl('/communications/users/'), {
    credentials: 'include',
  })

  if (!response.ok) {
    const data = await readJson(response)
    throw new Error(messageFrom(data, 'No se pudo cargar el chat'))
  }

  return response.json()
}

export async function getConversations() {
  const response = await fetch(buildApiUrl('/communications/conversations/'), {
    credentials: 'include',
  })

  if (!response.ok) {
    const data = await readJson(response)
    throw new Error(messageFrom(data, 'No se pudo cargar el chat'))
  }

  return response.json()
}

export async function createConversation({ participantIds, title = '' }) {
  const response = await fetch(buildApiUrl('/communications/conversations/'), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify({
      participant_ids: participantIds,
      title,
    }),
  })

  const data = await readJson(response)
  if (!response.ok) {
    throw new Error(messageFrom(data, 'No se pudo cargar el chat'))
  }

  return data
}

export async function getMessages(conversationId) {
  const response = await fetch(buildApiUrl(`/communications/conversations/${conversationId}/messages/`), {
    credentials: 'include',
  })

  if (!response.ok) {
    const data = await readJson(response)
    throw new Error(messageFrom(data, 'No se pudo cargar el chat'))
  }

  return response.json()
}

export async function sendMessage(conversationId, content) {
  const response = await fetch(buildApiUrl(`/communications/conversations/${conversationId}/messages/`), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify({ content }),
  })

  const data = await readJson(response)
  if (!response.ok) {
    throw new Error(messageFrom(data, 'No se pudo cargar el chat'))
  }

  return data
}
