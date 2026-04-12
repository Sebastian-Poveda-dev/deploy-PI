import { useEffect, useState } from 'react'
import StatusBadge from './StatusBadge'
import { approveCase, rejectCase } from '../services/caseService'
import { canApproveCase, canRejectCase } from '../utils/permissions'

function CaseModal({ caseData, isOpen, onClose, onOpenLogs, onOpenDocuments, currentUser, onCaseUpdated }) {
  const [pendingAction, setPendingAction] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [actionError, setActionError] = useState('')

  useEffect(() => {
    if (!isOpen) {
      setPendingAction(null)
      setProcessing(false)
      setActionError('')
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
      } else {
        await rejectCase(caseData.id)
        setPendingAction(null)
        onCaseUpdated?.(null)
      }
    } catch (err) {
      setActionError(err.message)
    } finally {
      setProcessing(false)
    }
  }

  const showApprove = canApproveCase(currentUser, caseData)
  const showReject = canRejectCase(currentUser, caseData)

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

          {/* Footer */}
          <section className="space-y-3 border-t border-slate-200 pt-4">

            {/* Inline confirmation */}
            {pendingAction && (
              <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                <p className="text-sm font-medium text-slate-700">
                  {pendingAction === 'approve'
                    ? '¿Estás seguro de aprobar este caso?'
                    : '¿Estás seguro de rechazar tu asignación en este caso?'}
                </p>
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
                    onClick={() => { setPendingAction(null); setActionError('') }}
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
