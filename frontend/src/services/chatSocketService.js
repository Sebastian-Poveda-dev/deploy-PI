import { buildWsUrl } from './apiClient'

function buildSocketUrl(conversationId) {
  return buildWsUrl(`/ws/communications/conversations/${conversationId}/`)
}

export function createConversationSocket(conversationId, handlers = {}) {
  const socket = new WebSocket(buildSocketUrl(conversationId))

  socket.addEventListener('open', (event) => {
    handlers.onOpen?.(event)
  })

  socket.addEventListener('message', (event) => {
    let payload = null
    try {
      payload = JSON.parse(event.data)
    } catch {
      payload = event.data
    }
    handlers.onMessage?.(payload, event)
  })

  socket.addEventListener('error', (event) => {
    handlers.onError?.(event)
  })

  socket.addEventListener('close', (event) => {
    handlers.onClose?.(event)
  })

  return {
    sendMessage(content) {
      socket.send(JSON.stringify({ type: 'message', content }))
    },
    close() {
      socket.close()
    },
    get readyState() {
      return socket.readyState
    },
    get rawSocket() {
      return socket
    },
  }
}
