import { useCallback, useEffect, useMemo, useState } from 'react'
import DashboardLayout from '../layouts/DashboardLayout'
import {
  createConversation,
  getConversations,
  getMessages,
  sendMessage,
} from '../services/communicationService'
import { getBeneficiaries } from '../services/userService'

const CHANNELS = [
  { value: 'whatsapp', label: 'WhatsApp', action: 'Abrir WhatsApp' },
  { value: 'email', label: 'Correo electrónico', action: 'Abrir correo' },
  { value: 'phone', label: 'Llamada telefónica', action: 'Llamar' },
]

const EMPTY_FORM = {
  beneficiaryId: '',
  channel: 'whatsapp',
}

function getChannel(channel) {
  return CHANNELS.find((item) => item.value === channel) ?? CHANNELS[0]
}

function formatTime(value) {
  if (!value) return ''
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function participantName(conversation) {
  return conversation?.beneficiary_name ?? conversation?.beneficiary?.name ?? 'Beneficiario'
}

function creatorName(conversation) {
  return conversation?.creator_name ?? conversation?.creator?.name ?? 'Usuario'
}

function NewConversationModal({
  isOpen,
  beneficiaries,
  beneficiariesLoading,
  submitting,
  error,
  onClose,
  onCreate,
}) {
  const [form, setForm] = useState(EMPTY_FORM)
  const [fieldError, setFieldError] = useState('')

  if (!isOpen) return null

  function setField(field) {
    return (event) => {
      setForm((prev) => ({ ...prev, [field]: event.target.value }))
      setFieldError('')
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    if (!form.beneficiaryId) {
      setFieldError('Selecciona un beneficiario.')
      return
    }
    onCreate({
      beneficiaryId: Number(form.beneficiaryId),
      channel: form.channel,
    })
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={(event) => event.target === event.currentTarget && onClose()}
    >
      <div className="w-full max-w-md rounded-xl bg-white shadow-xl">
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

        <form onSubmit={handleSubmit} noValidate>
          <div className="space-y-4 px-6 py-5">
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Beneficiario</label>
              <select
                value={form.beneficiaryId}
                onChange={setField('beneficiaryId')}
                disabled={beneficiariesLoading || submitting}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60"
              >
                <option value="">
                  {beneficiariesLoading ? 'Cargando beneficiarios...' : 'Selecciona un beneficiario'}
                </option>
                {beneficiaries.map((beneficiary) => (
                  <option key={beneficiary.id} value={beneficiary.id}>
                    {beneficiary.name ?? beneficiary.username ?? `Beneficiario #${beneficiary.id}`}
                  </option>
                ))}
              </select>
              {fieldError && <p className="text-xs text-red-500">{fieldError}</p>}
            </div>

            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Canal</label>
              <select
                value={form.channel}
                onChange={setField('channel')}
                disabled={submitting}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60"
              >
                {CHANNELS.map((channel) => (
                  <option key={channel.value} value={channel.value}>
                    {channel.label}
                  </option>
                ))}
              </select>
            </div>

            {error && (
              <p className="rounded-lg bg-red-50 px-3 py-2 text-sm font-medium text-red-600">
                {error}
              </p>
            )}
          </div>

          <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 disabled:opacity-60"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={submitting || beneficiariesLoading}
              className="rounded-lg bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7] disabled:cursor-not-allowed disabled:opacity-60"
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
  const [conversations, setConversations] = useState([])
  const [selectedConversationId, setSelectedConversationId] = useState(null)
  const [messages, setMessages] = useState([])
  const [beneficiaries, setBeneficiaries] = useState([])
  const [loadingConversations, setLoadingConversations] = useState(true)
  const [loadingMessages, setLoadingMessages] = useState(false)
  const [beneficiariesLoading, setBeneficiariesLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')
  const [messageError, setMessageError] = useState('')
  const [createError, setCreateError] = useState('')
  const [content, setContent] = useState('')
  const [isNewConversationOpen, setIsNewConversationOpen] = useState(false)

  const selectedConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === selectedConversationId) ?? null,
    [conversations, selectedConversationId],
  )

  async function loadConversations(selectFirst = false) {
    setLoadingConversations(true)
    setError('')
    try {
      const data = await getConversations()
      setConversations(data)
      if (selectFirst && data.length > 0) {
        setSelectedConversationId((current) => current ?? data[0].id)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingConversations(false)
    }
  }

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
      setMessageError(err.message)
    } finally {
      setLoadingMessages(false)
    }
  }, [selectedConversationId])

  async function loadBeneficiaries() {
    setBeneficiariesLoading(true)
    try {
      const data = await getBeneficiaries()
      setBeneficiaries(data)
    } catch {
      setCreateError('No fue posible cargar los beneficiarios.')
    } finally {
      setBeneficiariesLoading(false)
    }
  }

  useEffect(() => {
    loadConversations(true)
  }, [])

  useEffect(() => {
    if (selectedConversationId) {
      loadMessages(selectedConversationId)
    } else {
      setMessages([])
    }
  }, [loadMessages, selectedConversationId])

  function openNewConversation() {
    setCreateError('')
    setIsNewConversationOpen(true)
    if (beneficiaries.length === 0) {
      loadBeneficiaries()
    }
  }

  async function handleCreateConversation(payload) {
    setCreating(true)
    setCreateError('')
    try {
      const conversation = await createConversation(payload)
      setConversations((prev) => [
        conversation,
        ...prev.filter((item) => item.id !== conversation.id),
      ])
      setSelectedConversationId(conversation.id)
      setIsNewConversationOpen(false)
      setMessages([])
      await loadMessages(conversation.id)
    } catch (err) {
      setCreateError(err.message)
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
      await sendMessage(selectedConversation.id, trimmed)
      setContent('')
      await loadMessages(selectedConversation.id)
      loadConversations()
    } catch (err) {
      setMessageError(err.message)
    } finally {
      setSending(false)
    }
  }

  const selectedChannel = selectedConversation ? getChannel(selectedConversation.channel) : null
  const canSend = Boolean(selectedConversation && content.trim() && !sending && !loadingMessages)

  return (
    <DashboardLayout>
      <section className="mx-auto flex h-full min-h-[calc(100vh-4rem)] w-full max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-bold text-slate-800">Chats</h1>
          <button
            type="button"
            onClick={openNewConversation}
            className="inline-flex items-center justify-center rounded-lg bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7]"
          >
            Nueva conversación
          </button>
        </header>

        {error && (
          <p className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm font-medium text-red-600">
            {error}
          </p>
        )}

        <div className="grid min-h-0 flex-1 grid-cols-1 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm lg:grid-cols-[20rem_minmax(0,1fr)]">
          <aside className="flex min-h-72 flex-col border-b border-slate-200 lg:border-b-0 lg:border-r">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <h2 className="text-sm font-semibold text-slate-800">Conversaciones</h2>
              <button
                type="button"
                onClick={() => loadConversations(true)}
                disabled={loadingConversations}
                className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Actualizar
              </button>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto">
              {loadingConversations && (
                <div className="flex h-full min-h-52 items-center justify-center px-4">
                  <p className="text-sm font-medium text-slate-400">Cargando conversaciones...</p>
                </div>
              )}

              {!loadingConversations && conversations.length === 0 && (
                <div className="flex h-full min-h-52 items-center justify-center px-6 text-center">
                  <p className="text-sm font-medium text-slate-400">No hay conversaciones.</p>
                </div>
              )}

              {!loadingConversations && conversations.length > 0 && (
                <ul className="divide-y divide-slate-100">
                  {conversations.map((conversation) => {
                    const channel = getChannel(conversation.channel)
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
                                {participantName(conversation)}
                              </p>
                              <p className="mt-1 text-xs font-medium text-slate-500">
                                {channel.label}
                              </p>
                            </div>
                            <span className="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-500">
                              #{conversation.id}
                            </span>
                          </div>
                        </button>
                      </li>
                    )
                  })}
                </ul>
              )}
            </div>
          </aside>

          <div className="flex min-h-0 flex-col">
            {selectedConversation ? (
              <>
                <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 xl:flex-row xl:items-center xl:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="truncate text-lg font-semibold text-slate-800">
                        {participantName(selectedConversation)}
                      </h2>
                      <span className="rounded-full bg-[#5454F2]/10 px-2.5 py-1 text-xs font-semibold text-[#5454F2]">
                        {selectedChannel.label}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-slate-500">
                      {selectedConversation.beneficiary_email || 'Sin correo registrado'} ·{' '}
                      {selectedConversation.beneficiary_phone
                        || selectedConversation.beneficiary_phone_number
                        || 'Sin teléfono registrado'}
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    {selectedConversation.external_url ? (
                      <a
                        href={selectedConversation.external_url}
                        target={selectedConversation.channel === 'whatsapp' ? '_blank' : undefined}
                        rel={selectedConversation.channel === 'whatsapp' ? 'noreferrer' : undefined}
                        className="inline-flex items-center justify-center rounded-lg bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7]"
                      >
                        {selectedChannel.action}
                      </a>
                    ) : (
                      <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm font-medium text-amber-700">
                        Este beneficiario no tiene datos de contacto para este canal.
                      </p>
                    )}
                    <button
                      type="button"
                      onClick={() => loadMessages(selectedConversation.id)}
                      disabled={loadingMessages}
                      className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      Actualizar
                    </button>
                  </div>
                </div>

                {messageError && (
                  <p className="mx-5 mt-4 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm font-medium text-red-600">
                    {messageError}
                  </p>
                )}

                <div className="min-h-0 flex-1 overflow-y-auto bg-slate-50 px-5 py-5">
                  {loadingMessages && (
                    <div className="flex h-full min-h-64 items-center justify-center">
                      <p className="text-sm font-medium text-slate-400">Cargando mensajes...</p>
                    </div>
                  )}

                  {!loadingMessages && messages.length === 0 && (
                    <div className="flex h-full min-h-64 items-center justify-center">
                      <p className="text-sm font-medium text-slate-400">No hay mensajes.</p>
                    </div>
                  )}

                  {!loadingMessages && messages.length > 0 && (
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
                              <span className="text-xs font-semibold">
                                {message.sender_name ?? message.sender?.name ?? creatorName(selectedConversation)}
                              </span>
                              <span
                                className={`text-[11px] ${
                                  message.is_current_user ? 'text-white/70' : 'text-slate-400'
                                }`}
                              >
                                {formatTime(message.created_at)}
                              </span>
                            </div>
                            <p className="whitespace-pre-wrap break-words text-sm leading-6">
                              {message.content}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <form onSubmit={handleSendMessage} className="border-t border-slate-200 bg-white px-5 py-4">
                  <div className="flex flex-col gap-3 sm:flex-row">
                    <textarea
                      value={content}
                      onChange={(event) => setContent(event.target.value)}
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
                <p className="text-sm font-medium text-slate-400">Selecciona una conversación.</p>
              </div>
            )}
          </div>
        </div>
      </section>

      <NewConversationModal
        key={isNewConversationOpen ? 'open' : 'closed'}
        isOpen={isNewConversationOpen}
        beneficiaries={beneficiaries}
        beneficiariesLoading={beneficiariesLoading}
        submitting={creating}
        error={createError}
        onClose={() => setIsNewConversationOpen(false)}
        onCreate={handleCreateConversation}
      />
    </DashboardLayout>
  )
}

export default Chats
