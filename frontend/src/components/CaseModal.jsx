import { useEffect, useState } from 'react'
import StatusBadge from './StatusBadge'
import { approveCase, rejectCase, requestCancellation, reviewCancellation, cancelCase, getCaseProgressStatuses, addCaseProgressStatus, CANCELLATION_REASONS } from '../services/caseService'
import { canApproveCase, canRejectCase, canRequestCancellation, canReviewCancellation, canCancelCase } from '../utils/permissions'

function CaseModal({ caseData, isOpen, onClose, onOpenLogs, onOpenDocuments, currentUser, onCaseUpdated }) {
  const [pendingAction, setPendingAction] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [actionError, setActionError] = useState('')
  const [cancellationReason, setCancellationReason] = useState('')
  const [cancelReason, setCancelReason] = useState('')
  const [cancelReasonOther, setCancelReasonOther] = useState('')

  const [progressStatuses, setProgressStatuses] = useState([])
  const [progressLoading, setProgressLoading] = useState(false)
  const [newProgressLabel, setNewProgressLabel] = useState('')
  const [progressError, setProgressError] = useState('')
  const [progressSubmitting, setProgressSubmitting] = useState(false)

  const canAddProgress = currentUser && ['admin', 'advisor', 'student'].includes(currentUser.role)

  useEffect(() => {
    if (!isOpen || !caseData?.id) {
      setProgressStatuses([])
      setNewProgressLabel('')
      setProgressError('')
      return
    }
    setProgressLoading(true)
    getCaseProgressStatuses(caseData.id)
      .then(setProgressStatuses)
      .catch(() => setProgressStatuses([]))
      .finally(() => setProgressLoading(false))
  }, [isOpen, caseData?.id])

  async function handleAddProgress(e) {
    e.preventDefault()
    if (!newProgressLabel.trim()) return
    setProgressSubmitting(true)
    setProgressError('')
    try {
      const created = await addCaseProgressStatus(caseData.id, newProgressLabel.trim())
      setProgressStatuses((prev) => [...prev, created])
      setNewProgressLabel('')
    } catch (err) {
      setProgressError(err.message)
    } finally {
      setProgressSubmitting(false)
    }
  }

  useEffect(() => {
    if (!isOpen) {
      setPendingAction(null)
      setProcessing(false)
      setActionError('')
      setCancellationReason('')
      setCancelReason('')
      setCancelReasonOther('')
    }
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape') onClose()
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  async function handleConfirm() {
    setProcessing(true)
    setActionError('')
    try {
      if (pendingAction === 'approve') {
        const updated = await approveCase(caseData.id)
        setPendingAction(null)
        onCaseUpdated?.(updated)
      } else if (pendingAction === 'reject') {
        await rejectCase(caseData.id)
        setPendingAction(null)
        onCaseUpdated?.(null)
      } else if (pendingAction === 'request-cancellation') {
        if (!cancellationReason.trim()) {
          throw new Error('Por favor, indica un motivo para la reasignación.')
        }
        await requestCancellation(caseData.id, cancellationReason)
        setPendingAction(null)
        onClose() // Refresh needed, simpler to close and let parent refresh
        onCaseUpdated?.(null) // Signal refresh
      } else if (pendingAction === 'approve-cancellation') {
        await reviewCancellation(caseData.pendingCancellation.id, 'approve')
        setPendingAction(null)
        onCaseUpdated?.(null) // Signal refresh
      } else if (pendingAction === 'reject-cancellation') {
        await reviewCancellation(caseData.pendingCancellation.id, 'reject')
        setPendingAction(null)
        onCaseUpdated?.(null) // Signal refresh
      } else if (pendingAction === 'cancel-case') {
        if (!cancelReason) {
          throw new Error('Por favor, selecciona una razón de cancelación.')
        }
        if (cancelReason === 'OTRO' && !cancelReasonOther.trim()) {
          throw new Error('Por favor, describe la razón de cancelación.')
        }
        const updated = await cancelCase(caseData.id, cancelReason, cancelReasonOther)
        setPendingAction(null)
        onCaseUpdated?.(updated)
      }
    } catch (err) {
      setActionError(err.message)
    } finally {
      setProcessing(false)
    }
  }

  const showApprove = canApproveCase(currentUser, caseData)
  const showReject = canRejectCase(currentUser, caseData)
  const showRequestCancellation = canRequestCancellation(currentUser, caseData)
  const showReviewCancellation = canReviewCancellation(currentUser, caseData)
  const showCancelCase = canCancelCase(currentUser, caseData)

  const assignedUsersList = caseData?.assignedUsers
    ? caseData.assignedUsers.split(',').map((user) => user.trim()).filter(Boolean)
    : []

  return (
    <div
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
      className={`fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 transition-opacity duration-300 ease-in-out ${
        isOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
      }`}
      aria-hidden={!isOpen}
    >
      <div
        className={`w-full max-w-2xl rounded-xl bg-white shadow-xl transition-all duration-300 ease-in-out ${
          isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-4">
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-xl font-bold text-slate-800">Case #{caseData?.id}</h2>
            {caseData?.status ? <StatusBadge status={caseData.status} /> : null}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
            aria-label="Close case details"
          >
            <span className="text-lg leading-none">×</span>
          </button>
        </div>

        {/* Body */}
        <div className="max-h-[70vh] space-y-6 overflow-y-auto px-6 py-5">
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Category</p>
              <p className="mt-1 text-sm font-medium text-slate-700">{caseData?.category || '—'}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Creation Date</p>
              <p className="mt-1 text-sm font-medium text-slate-700">{caseData?.createdAt || '—'}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Last Updated Date</p>
              <p className="mt-1 text-sm font-medium text-slate-700">{caseData?.updatedAt || '—'}</p>
            </div>
          </section>

          <section>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Assigned Users</p>
            {assignedUsersList.length ? (
              <ul className="mt-2 space-y-1">
                {assignedUsersList.map((user) => (
                  <li key={user} className="text-sm text-slate-700">{user}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-2 text-sm text-slate-500">No assigned users.</p>
            )}
          </section>

          <section>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Description</p>
            <div className="mt-2 max-h-52 overflow-y-auto rounded-lg border border-slate-200 bg-slate-50 p-3">
              <p className="text-sm leading-6 text-slate-700">
                {caseData?.description || 'No description available.'}
              </p>
            </div>
          </section>

          {/* Progress statuses */}
          <section>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Progreso del caso</p>

            {progressLoading ? (
              <p className="mt-2 text-sm text-slate-400">Cargando...</p>
            ) : progressStatuses.length === 0 ? (
              <p className="mt-2 text-sm text-slate-400">Sin estados de progreso registrados.</p>
            ) : (
              <ol className="mt-3 space-y-2">
                {progressStatuses.map((ps, index) => (
                  <li key={ps.id} className="flex items-start gap-3">
                    <div className="flex flex-col items-center">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#5454F2] text-[10px] font-bold text-white">
                        {index + 1}
                      </span>
                      {index < progressStatuses.length - 1 && (
                        <div className="mt-1 h-full w-px bg-slate-200" style={{ minHeight: '1rem' }} />
                      )}
                    </div>
                    <div className="pb-1">
                      <p className="text-sm font-medium text-slate-800">{ps.label}</p>
                      <p className="text-xs text-slate-400">
                        {ps.created_by_name} · {ps.created_at?.split('T')[0]}
                      </p>
                    </div>
                  </li>
                ))}
              </ol>
            )}

            {canAddProgress && (
              <form onSubmit={handleAddProgress} className="mt-3 flex gap-2">
                <input
                  type="text"
                  value={newProgressLabel}
                  onChange={(e) => setNewProgressLabel(e.target.value)}
                  placeholder="Nuevo estado de progreso..."
                  maxLength={200}
                  className="flex-1 rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2]"
                />
                <button
                  type="submit"
                  disabled={progressSubmitting || !newProgressLabel.trim()}
                  className="rounded-md bg-[#5454F2] px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7] disabled:opacity-50"
                >
                  {progressSubmitting ? '...' : 'Agregar'}
                </button>
              </form>
            )}
            {progressError && <p className="mt-1 text-xs text-red-500">{progressError}</p>}
          </section>

          {caseData?.pendingCancellation && (
            <section className="rounded-lg border-2 border-amber-200 bg-amber-50 p-4">
              <h3 className="text-sm font-bold text-amber-800">Solicitud de Reasignación Pendiente</h3>
              <p className="mt-1 text-sm text-amber-700">
                <span className="font-semibold">Solicitado por:</span> {caseData.pendingCancellation.requested_by_name}
              </p>
              <p className="mt-1 text-sm text-amber-700 italic">
                "{caseData.pendingCancellation.reason}"
              </p>
            </section>
          )}

          {/* Footer */}
          <section className="space-y-3 border-t border-slate-200 pt-4">

            {/* Inline confirmation */}
            {pendingAction && (
              <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                <p className="text-sm font-medium text-slate-700">
                  {pendingAction === 'approve' && '¿Estás seguro de aprobar este caso?'}
                  {pendingAction === 'reject' && '¿Estás seguro de rechazar tu asignación?'}
                  {pendingAction === 'request-cancellation' && 'Solicitar reasignación del caso:'}
                  {pendingAction === 'approve-cancellation' && '¿Estás seguro de aprobar la reasignación? El estudiante actual será removido.'}
                  {pendingAction === 'reject-cancellation' && '¿Estás seguro de rechazar la reasignación?'}
                  {pendingAction === 'cancel-case' && 'Selecciona la razón de cancelación del caso:'}
                </p>

                {pendingAction === 'request-cancellation' && (
                  <textarea
                    value={cancellationReason}
                    onChange={(e) => setCancellationReason(e.target.value)}
                    placeholder="Describe el motivo (ej: sobrecarga académica)..."
                    className="mt-2 w-full rounded-md border border-slate-300 p-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                    rows={3}
                  />
                )}

                {pendingAction === 'cancel-case' && (
                  <div className="mt-3 space-y-2">
                    {CANCELLATION_REASONS.map((r) => (
                      <label key={r.value} className="flex cursor-pointer items-start gap-2">
                        <input
                          type="radio"
                          name="cancelReason"
                          value={r.value}
                          checked={cancelReason === r.value}
                          onChange={(e) => { setCancelReason(e.target.value); setCancelReasonOther('') }}
                          className="mt-0.5 accent-red-600"
                        />
                        <span className="text-sm text-slate-700">{r.label}</span>
                      </label>
                    ))}
                    {cancelReason === 'OTRO' && (
                      <textarea
                        value={cancelReasonOther}
                        onChange={(e) => setCancelReasonOther(e.target.value)}
                        placeholder="Describe la razón de cancelación..."
                        className="mt-1 w-full rounded-md border border-slate-300 p-2 text-sm focus:border-red-500 focus:ring-1 focus:ring-red-500"
                        rows={3}
                      />
                    )}
                  </div>
                )}

                {actionError && (
                  <p className="mt-1 text-xs text-red-500">{actionError}</p>
                )}
                <div className="mt-3 flex gap-2">
                  <button
                    type="button"
                    onClick={handleConfirm}
                    disabled={processing}
                    className="rounded-md bg-slate-800 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-slate-700 disabled:opacity-60"
                  >
                    {processing ? 'Procesando...' : 'Confirmar'}
                  </button>
                  <button
                    type="button"
                    onClick={() => { setPendingAction(null); setActionError(''); setCancellationReason(''); setCancelReason(''); setCancelReasonOther('') }}
                    disabled={processing}
                    className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-100 disabled:opacity-60"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            )}

            {/* Action + navigation buttons */}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex gap-2">
                {showApprove && !pendingAction && (
                  <button
                    type="button"
                    onClick={() => setPendingAction('approve')}
                    className="inline-flex items-center justify-center rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
                  >
                    Aprobar Caso
                  </button>
                )}
                {showReject && !pendingAction && (
                  <button
                    type="button"
                    onClick={() => setPendingAction('reject')}
                    className="inline-flex items-center justify-center rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-600"
                  >
                    Rechazar Caso
                  </button>
                )}
                {showRequestCancellation && !pendingAction && (
                  <button
                    type="button"
                    onClick={() => setPendingAction('request-cancellation')}
                    className="inline-flex items-center justify-center rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-amber-600"
                  >
                    Solicitar Reasignación
                  </button>
                )}
                {showReviewCancellation && !pendingAction && (
                  <>
                    <button
                      type="button"
                      onClick={() => setPendingAction('approve-cancellation')}
                      className="inline-flex items-center justify-center rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
                    >
                      Aprobar Reasignación
                    </button>
                    <button
                      type="button"
                      onClick={() => setPendingAction('reject-cancellation')}
                      className="inline-flex items-center justify-center rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-600"
                    >
                      Rechazar Reasignación
                    </button>
                  </>
                )}
                {showCancelCase && !pendingAction && (
                  <button
                    type="button"
                    onClick={() => { setCancelReason(''); setCancelReasonOther(''); setPendingAction('cancel-case') }}
                    className="inline-flex items-center justify-center rounded-lg bg-red-700 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-800"
                  >
                    Cerrar Caso
                  </button>
                )}
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => onOpenDocuments?.(caseData?.id)}
                  disabled={!caseData?.id}
                  className="inline-flex items-center justify-center rounded-lg border border-[#5454F2] px-4 py-2 text-sm font-semibold text-[#5454F2] transition-colors hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  Documentos
                </button>
                <button
                  type="button"
                  onClick={() => onOpenLogs?.(caseData?.id)}
                  disabled={!caseData?.id}
                  className="inline-flex items-center justify-center rounded-lg bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  Seguimiento
                </button>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default CaseModal
