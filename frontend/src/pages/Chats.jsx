import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import DashboardLayout from '../layouts/DashboardLayout'
import {
  createConversation,
  getChatUsers,
  getConversations,
  getMessages,
  sendMessage,
} from '../services/communicationService'
import { createConversationSocket } from '../services/chatSocketService'

const SOCKET_OPEN = 1
const CONVERSATION_REFRESH_MS = 15000

function formatTime(value) {
  if (!value) return ''
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function userName(user) {
  if (!user) return 'Usuario'
  return user.full_name || user.name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username
}

function messageSenderName(message) {
  return message.sender_name || userName(message.sender) || message.sender_username || 'Usuario'
}

function conversationName(conversation) {
  if (!conversation) return ''
  if (conversation.title) return conversation.title
  const names = (conversation.participants || []).map(userName).filter(Boolean)
  return names.join(', ') || `Conversación #${conversation.id}`
}

function normalizeParticipantIds(ids) {
  return Array.from(new Set(ids.map(Number))).filter(Boolean)
}

function conversationTimestamp(conversation) {
  return new Date(
    conversation.last_message?.created_at || conversation.updated_at || conversation.created_at || 0,
  ).getTime()
}

function sortConversations(items) {
  return [...items].sort((a, b) => conversationTimestamp(b) - conversationTimestamp(a))
}

function mergeConversations(current, incoming) {
  const byId = new Map()
  current.forEach((conversation) => {
    byId.set(conversation.id, conversation)
  })
  incoming.forEach((conversation) => {
    const existing = byId.get(conversation.id)
    byId.set(conversation.id, existing ? { ...existing, ...conversation } : conversation)
  })
  return sortConversations(Array.from(byId.values()))
}

function connectionLabel(status) {
  if (status === 'connected') return 'Conectado'
  if (status === 'connecting') return 'Reconectando'
  return 'Sin conexión en tiempo real'
}

function NewConversationModal({
  isOpen,
  users,
  loadingUsers,
  submitting,
  error,
  onClose,
  onCreate,
}) {
  const [title, setTitle] = useState('')
  const [query, setQuery] = useState('')
  const [selectedIds, setSelectedIds] = useState([])
  const [fieldError, setFieldError] = useState('')

  const filteredUsers = useMemo(() => {
    const needle = query.trim().toLowerCase()
    if (!needle) return users
    return users.filter((user) => {
      const haystack = `${user.username} ${user.first_name} ${user.last_name} ${user.full_name} ${user.role}`.toLowerCase()
      return haystack.includes(needle)
    })
  }, [query, users])

  if (!isOpen) return null

  function toggleUser(userId) {
    setSelectedIds((current) => (
      current.includes(userId)
        ? current.filter((id) => id !== userId)
        : [...current, userId]
    ))
    setFieldError('')
  }

  function handleSubmit(event) {
    event.preventDefault()
    const participantIds = normalizeParticipantIds(selectedIds)
    if (participantIds.length === 0) {
      setFieldError('Selecciona al menos un participante.')
      return
    }
    onCreate({ participantIds, title: title.trim() })
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={(event) => event.target === event.currentTarget && onClose()}
    >
      <div className="flex max-h-[86vh] w-full max-w-2xl flex-col rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-800">Nueva conversación</h2>
          <button
            type="button"
            onClick={onClose}
            disabled={submitting}
            className="rounded-md px-2 py-1 text-lg leading-none text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 disabled:opacity-50"
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex min-h-0 flex-1 flex-col" noValidate>
          <div className="space-y-4 px-6 py-5">
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Título opcional</label>
              <input
                type="text"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                disabled={submitting}
                className="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60"
                placeholder="Ej. Equipo del caso civil"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Buscar usuario</label>
              <input
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                disabled={submitting}
                className="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60"
                placeholder="Buscar usuario"
              />
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between">
                <p className="text-sm font-semibold text-slate-800">Participantes</p>
                <p className="text-xs font-medium text-slate-400">{selectedIds.length} seleccionados</p>
              </div>

              <div className="max-h-64 overflow-y-auto rounded-xl border border-slate-200">
                {loadingUsers && (
                  <div className="px-4 py-8 text-center text-sm font-medium text-slate-400">
                    Cargando usuarios...
                  </div>
                )}

                {!loadingUsers && filteredUsers.length === 0 && (
                  <div className="px-4 py-8 text-center text-sm font-medium text-slate-400">
                    No hay usuarios disponibles.
                  </div>
                )}

                {!loadingUsers && filteredUsers.map((user) => (
                  <label
                    key={user.id}
                    className="flex cursor-pointer items-center gap-3 border-b border-slate-100 px-4 py-3 last:border-b-0 hover:bg-slate-50"
                  >
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(user.id)}
                      onChange={() => toggleUser(user.id)}
                      disabled={submitting}
                      className="h-4 w-4 rounded border-slate-300 text-[#5454F2] focus:ring-[#5454F2]"
                    />
                    <span className="flex min-w-0 flex-1 flex-col">
                      <span className="truncate text-sm font-semibold text-slate-800">{userName(user)}</span>
                      <span className="truncate text-xs text-slate-500">
                        {user.username} · {user.role || 'sin rol'}
                      </span>
                    </span>
                  </label>
                ))}
              </div>
              {fieldError && <p className="mt-2 text-xs font-medium text-red-500">{fieldError}</p>}
            </div>

            {error && (
              <p className="rounded-xl bg-red-50 px-3 py-2 text-sm font-medium text-red-600">
                {error}
              </p>
            )}
          </div>

          <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 disabled:opacity-60"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={submitting || loadingUsers}
              className="rounded-xl bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? 'Creando...' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function Chats() {
  const socketRef = useRef(null)
  const selectedConversationIdRef = useRef(null)
  const [conversations, setConversations] = useState([])
  const [selectedConversationId, setSelectedConversationId] = useState(null)
  const [messages, setMessages] = useState([])
  const [chatUsers, setChatUsers] = useState([])
  const [loadingConversations, setLoadingConversations] = useState(true)
  const [loadingMessages, setLoadingMessages] = useState(false)
  const [loadingUsers, setLoadingUsers] = useState(false)
  const [sending, setSending] = useState(false)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')
  const [messageError, setMessageError] = useState('')
  const [createError, setCreateError] = useState('')
  const [content, setContent] = useState('')
  const [socketStatus, setSocketStatus] = useState('disconnected')
  const [isNewConversationOpen, setIsNewConversationOpen] = useState(false)

  const selectedConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === selectedConversationId) ?? null,
    [conversations, selectedConversationId],
  )

  const selectedParticipants = selectedConversation?.participants || []
  const canSend = Boolean(selectedConversation && content.trim() && !sending && !loadingMessages)

  const mergeMessage = useCallback((message) => {
    setMessages((current) => {
      if (current.some((item) => item.id === message.id)) {
        return current.map((item) => (item.id === message.id ? { ...item, ...message } : item))
      }
      return [...current, message]
    })

    setConversations((current) => sortConversations(current.map((conversation) => (
      conversation.id === message.conversation
        ? { ...conversation, last_message: message, updated_at: message.created_at }
        : conversation
    ))))
  }, [])

  const loadConversations = useCallback(async ({ selectFirst = false, silent = false } = {}) => {
    if (!silent) {
      setLoadingConversations(true)
    }
    setError('')
    try {
      const data = await getConversations()
      setConversations(mergeConversations([], data))
      if (selectFirst && data.length > 0) {
        setSelectedConversationId((current) => current ?? data[0].id)
      }
      if (data.length === 0) {
        setSelectedConversationId(null)
      }
    } catch (err) {
      setError(err.message || 'No se pudo cargar el chat')
    } finally {
      if (!silent) {
        setLoadingConversations(false)
      }
    }
  }, [])

  const loadMessages = useCallback(async (conversationId = selectedConversationId) => {
    if (!conversationId) {
      setMessages([])
      return
    }

    setLoadingMessages(true)
    setMessageError('')
    try {
      const data = await getMessages(conversationId)
      setMessages(data)
    } catch (err) {
      setMessageError(err.message || 'No se pudo cargar el chat')
    } finally {
      setLoadingMessages(false)
    }
  }, [selectedConversationId])

  async function loadChatUsers() {
    setLoadingUsers(true)
    setCreateError('')
    try {
      const data = await getChatUsers()
      setChatUsers(data)
    } catch (err) {
      setCreateError(err.message || 'No se pudo cargar el chat')
    } finally {
      setLoadingUsers(false)
    }
  }

  useEffect(() => {
    loadConversations({ selectFirst: true })
  }, [loadConversations])

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      loadConversations({ silent: true })
    }, CONVERSATION_REFRESH_MS)

    return () => {
      window.clearInterval(intervalId)
    }
  }, [loadConversations])

  useEffect(() => {
    selectedConversationIdRef.current = selectedConversationId
    if (!selectedConversationId) {
      setMessages([])
      setSocketStatus('disconnected')
      socketRef.current?.close()
      socketRef.current = null
      return undefined
    }

    loadMessages(selectedConversationId)
    setSocketStatus('connecting')

    const socket = createConversationSocket(selectedConversationId, {
      onOpen: () => {
        if (selectedConversationIdRef.current === selectedConversationId) {
          setSocketStatus('connected')
        }
      },
      onMessage: (payload) => {
        if (payload?.type === 'message' && payload.message) {
          mergeMessage(payload.message)
          return
        }
        if (payload?.type === 'error') {
          setMessageError(payload.errors?.content || payload.errors?.detail || 'No se pudo cargar el chat')
        }
      },
      onError: () => {
        if (selectedConversationIdRef.current === selectedConversationId) {
          setSocketStatus('disconnected')
        }
      },
      onClose: () => {
        if (selectedConversationIdRef.current === selectedConversationId) {
          setSocketStatus('disconnected')
        }
      },
    })

    socketRef.current = socket

    return () => {
      socket.close()
      if (socketRef.current === socket) {
        socketRef.current = null
      }
    }
  }, [loadMessages, mergeMessage, selectedConversationId])

  function openNewConversation() {
    setCreateError('')
    setIsNewConversationOpen(true)
    if (chatUsers.length === 0) {
      loadChatUsers()
    }
  }

  async function handleCreateConversation(payload) {
    setCreating(true)
    setCreateError('')
    try {
      const conversation = await createConversation(payload)
      setConversations((current) => mergeConversations(current, [conversation]))
      setSelectedConversationId(conversation.id)
      setIsNewConversationOpen(false)
    } catch (err) {
      setCreateError(err.message || 'No se pudo cargar el chat')
    } finally {
      setCreating(false)
    }
  }

  async function handleSendMessage(event) {
    event.preventDefault()
    const trimmed = content.trim()
    if (!selectedConversation || !trimmed || sending) return

    setSending(true)
    setMessageError('')
    try {
      const socket = socketRef.current
      if (socket?.readyState === SOCKET_OPEN) {
        socket.sendMessage(trimmed)
        setContent('')
      } else {
        const message = await sendMessage(selectedConversation.id, trimmed)
        setContent('')
        mergeMessage(message)
        await loadMessages(selectedConversation.id)
      }
      loadConversations({ silent: true })
    } catch (err) {
      setMessageError(err.message || 'No se pudo cargar el chat')
    } finally {
      setSending(false)
    }
  }

  function handleMessageKeyDown(event) {
    if (event.key !== 'Enter' || event.shiftKey || !canSend) return
    event.preventDefault()
    handleSendMessage(event)
  }

  function renderConversationList() {
    if (loadingConversations) {
      return (
        <div className="flex h-full min-h-52 items-center justify-center px-4">
          <p className="text-sm font-medium text-slate-400">Cargando conversaciones...</p>
        </div>
      )
    }

    if (conversations.length === 0) {
      return (
        <div className="flex h-full min-h-52 items-center justify-center px-6 text-center">
          <p className="text-sm font-medium text-slate-400">No tienes conversaciones todavía</p>
        </div>
      )
    }

    return (
      <ul className="divide-y divide-slate-100">
        {conversations.map((conversation) => {
          const isSelected = conversation.id === selectedConversationId
          return (
            <li key={conversation.id}>
              <button
                type="button"
                onClick={() => setSelectedConversationId(conversation.id)}
                className={`w-full px-4 py-3 text-left transition-colors ${
                  isSelected ? 'bg-[#5454F2]/10' : 'hover:bg-slate-50'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-slate-800">
                      {conversationName(conversation)}
                    </p>
                    <p className="mt-1 truncate text-xs text-slate-500">
                      {conversation.last_message?.content || 'Sin mensajes'}
                    </p>
                  </div>
                  <span className="shrink-0 text-[11px] font-medium text-slate-400">
                    {formatTime(conversation.last_message?.created_at || conversation.updated_at)}
                  </span>
                </div>
              </button>
            </li>
          )
        })}
      </ul>
    )
  }

  function renderMessages() {
    if (loadingMessages) {
      return (
        <div className="flex h-full min-h-64 items-center justify-center">
          <p className="text-sm font-medium text-slate-400">Cargando mensajes...</p>
        </div>
      )
    }

    if (messages.length === 0) {
      return (
        <div className="flex h-full min-h-64 items-center justify-center">
          <p className="text-sm font-medium text-slate-400">No hay mensajes todavía.</p>
        </div>
      )
    }

    return (
      <div className="space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.is_current_user ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[78%] rounded-xl px-4 py-3 shadow-sm ${
                message.is_current_user
                  ? 'bg-[#5454F2] text-white'
                  : 'border border-slate-200 bg-white text-slate-800'
              }`}
            >
              <div className="mb-1 flex flex-wrap items-center gap-x-2 gap-y-1">
                <span className="text-xs font-semibold">{messageSenderName(message)}</span>
                <span className={`text-[11px] ${message.is_current_user ? 'text-white/70' : 'text-slate-400'}`}>
                  {formatTime(message.created_at)}
                </span>
              </div>
              <p className="whitespace-pre-wrap break-words text-sm leading-6">{message.content}</p>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <DashboardLayout>
      <section className="mx-auto flex h-full min-h-[calc(100vh-4rem)] w-full max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-bold text-slate-800">Chats</h1>
          <button
            type="button"
            onClick={openNewConversation}
            className="inline-flex items-center justify-center rounded-xl bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7]"
          >
            Nueva conversación
          </button>
        </header>

        {error && (
          <p className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm font-medium text-red-600">
            {error}
          </p>
        )}

        <div className="grid min-h-0 flex-1 grid-cols-1 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm lg:grid-cols-[21rem_minmax(0,1fr)]">
          <aside className="flex min-h-72 flex-col border-b border-slate-200 lg:border-b-0 lg:border-r">
            <div className="border-b border-slate-200 px-4 py-3">
              <h2 className="text-sm font-semibold text-slate-800">Chats</h2>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto">{renderConversationList()}</div>
          </aside>

          <div className="flex min-h-0 flex-col">
            {selectedConversation ? (
              <>
                <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 xl:flex-row xl:items-center xl:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="truncate text-lg font-semibold text-slate-800">
                        {conversationName(selectedConversation)}
                      </h2>
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                          socketStatus === 'connected'
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-slate-100 text-slate-500'
                        }`}
                      >
                        {connectionLabel(socketStatus)}
                      </span>
                    </div>
                    <p className="mt-1 truncate text-sm text-slate-500">
                      Participantes: {selectedParticipants.map(userName).join(', ')}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => loadMessages(selectedConversation.id)}
                    disabled={loadingMessages}
                    className="self-start rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60 xl:self-auto"
                  >
                    Actualizar
                  </button>
                </div>

                {messageError && (
                  <p className="mx-5 mt-4 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm font-medium text-red-600">
                    {messageError}
                  </p>
                )}

                <div className="min-h-0 flex-1 overflow-y-auto bg-slate-50 px-5 py-5">
                  {renderMessages()}
                </div>

                <form onSubmit={handleSendMessage} className="border-t border-slate-200 bg-white px-5 py-4">
                  <div className="flex flex-col gap-3 sm:flex-row">
                    <textarea
                      value={content}
                      onChange={(event) => setContent(event.target.value)}
                      onKeyDown={handleMessageKeyDown}
                      placeholder="Escribe un mensaje..."
                      rows={2}
                      disabled={sending}
                      className="min-h-12 flex-1 resize-none rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60"
                    />
                    <button
                      type="submit"
                      disabled={!canSend}
                      className="inline-flex items-center justify-center rounded-xl bg-[#5454F2] px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7] disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {sending ? 'Enviando...' : 'Enviar'}
                    </button>
                  </div>
                </form>
              </>
            ) : (
              <div className="flex h-full min-h-96 items-center justify-center px-6 text-center">
                <p className="text-sm font-medium text-slate-400">Selecciona una conversación</p>
              </div>
            )}
          </div>
        </div>
      </section>

      <NewConversationModal
        key={isNewConversationOpen ? 'new-conversation-open' : 'new-conversation-closed'}
        isOpen={isNewConversationOpen}
        users={chatUsers}
        loadingUsers={loadingUsers}
        submitting={creating}
        error={createError}
        onClose={() => setIsNewConversationOpen(false)}
        onCreate={handleCreateConversation}
      />
    </DashboardLayout>
  )
}

export default Chats
