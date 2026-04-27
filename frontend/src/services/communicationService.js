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

export async function getConversations() {
  const response = await fetch('/communications/conversations/', {
    credentials: 'include',
  })

  if (!response.ok) {
    const data = await readJson(response)
    throw new Error(messageFrom(data, 'No fue posible cargar las conversaciones.'))
  }

  return response.json()
}

export async function createConversation({ beneficiaryId, channel }) {
  const response = await fetch('/communications/conversations/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify({
      beneficiary_id: beneficiaryId,
      channel,
    }),
  })

  const data = await readJson(response)
  if (!response.ok) {
    throw new Error(messageFrom(data, 'No fue posible crear la conversación.'))
  }

  return data
}

export async function getMessages(conversationId) {
  const response = await fetch(`/communications/conversations/${conversationId}/messages/`, {
    credentials: 'include',
  })

  if (!response.ok) {
    const data = await readJson(response)
    throw new Error(messageFrom(data, 'No fue posible cargar los mensajes.'))
  }

  return response.json()
}

export async function sendMessage(conversationId, content) {
  const response = await fetch(`/communications/conversations/${conversationId}/messages/`, {
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
    throw new Error(messageFrom(data, 'No fue posible enviar el mensaje.'))
  }

  return data
}
