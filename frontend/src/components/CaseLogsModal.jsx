import { useCallback, useEffect, useMemo, useState } from 'react'
import { createLog, getLogs } from '../services/logService'

function CaseLogsModal({ caseId, isOpen, onClose }) {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [newLog, setNewLog] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const canSend = useMemo(() => newLog.trim().length > 0 && !isSubmitting, [newLog, isSubmitting])

  const loadLogs = useCallback(async () => {
    if (!caseId) return

    setLoading(true)
    setError('')

    try {
      const data = await getLogs(caseId)
      setLogs(data)
    } catch (fetchError) {
      setError(fetchError.message || 'No fue posible cargar el seguimiento del caso.')
    } finally {
      setLoading(false)
    }
  }, [caseId])

  useEffect(() => {
    if (!isOpen || !caseId) return
    loadLogs()
  }, [isOpen, caseId, loadLogs])

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  async function handleSubmit(event) {
    event.preventDefault()

    const content = newLog.trim()
    if (!content || !caseId) return

    setIsSubmitting(true)
    setError('')

    try {
      await createLog(caseId, { content })
      setNewLog('')
      await loadLogs()
    } catch (submitError) {
      setError(submitError.message || 'No fue posible enviar el comentario.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div
      onClick={(event) => {
        if (event.target === event.currentTarget) {
          onClose()
        }
      }}
      className={`fixed inset-0 z-[60] flex items-center justify-center bg-black/40 p-4 transition-opacity duration-300 ease-in-out ${
        isOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
      }`}
      aria-hidden={!isOpen}
    >
      <div
        className={`flex h-[75vh] w-full max-w-2xl flex-col rounded-xl bg-white shadow-xl transition-all duration-300 ease-in-out ${
          isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h3 className="text-lg font-bold text-slate-800">Seguimiento del Caso #{caseId}</h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
            aria-label="Close case logs"
          >
            <span className="text-lg leading-none">×</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-5">
          {loading ? <p className="text-sm text-slate-500">Cargando...</p> : null}

          {!loading && error ? <p className="text-sm text-red-500">{error}</p> : null}

          {!loading && !error && logs.length === 0 ? (
            <p className="text-sm text-slate-400">No hay comentarios aún</p>
          ) : null}

          {!loading && !error && logs.length > 0 ? (
            <div className="space-y-3">
              {logs.map((logItem) => (
                <div
                  key={logItem.id}
                  className={`flex ${logItem.isCurrentUser ? 'justify-end' : 'justify-start'}`}
                >
                  <article
                    className={`max-w-[85%] rounded-xl px-4 py-3 shadow-sm ${
                      logItem.isCurrentUser ? 'bg-[#5454F2] text-white' : 'bg-slate-100 text-slate-800'
                    }`}
                  >
                    <p
                      className={`text-xs font-semibold ${
                        logItem.isCurrentUser ? 'text-indigo-100' : 'text-slate-500'
                      }`}
                    >
                      {logItem.userName}
                    </p>
                    <p className="mt-1 text-sm leading-6">{logItem.content}</p>
                    <p
                      className={`mt-2 text-[11px] ${
                        logItem.isCurrentUser ? 'text-indigo-100' : 'text-slate-500'
                      }`}
                    >
                      {logItem.createdAt}
                    </p>
                  </article>
                </div>
              ))}
            </div>
          ) : null}
        </div>

        <form onSubmit={handleSubmit} className="border-t border-slate-200 px-6 py-4">
          <div className="space-y-3">
            <textarea
              value={newLog}
              onChange={(event) => setNewLog(event.target.value)}
              placeholder="Escribe un comentario de seguimiento..."
              rows={3}
              className="w-full resize-none rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-[#5454F2] focus:outline-none"
            />
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={!canSend}
                className="inline-flex items-center justify-center rounded-lg bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSubmitting ? 'Enviando...' : 'Enviar'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CaseLogsModal