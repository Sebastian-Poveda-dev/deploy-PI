import { useEffect, useState } from 'react'
import StatusBadge from './StatusBadge'
import { approveCase, rejectCase, requestCancellation, reviewCancellation, getCaseProgressStatuses, addCaseProgressStatus } from '../services/caseService'
import { getBeneficiary, updateBeneficiary } from '../services/userService'
import { canApproveCase, canRejectCase, canRequestCancellation, canReviewCancellation } from '../utils/permissions'

function Field({ label, value }) {
  return (
    <div>
      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-0.5 text-sm text-slate-700 break-words">{value}</p>
    </div>
  )
}

function EditField({ label, field, type = 'text', draft, setDraft }) {
  return (
    <div>
      <label className="block text-[10px] font-semibold uppercase tracking-wide text-slate-500 mb-1">{label}</label>
      <input
        type={type}
        value={draft[field] ?? ''}
        onChange={(e) => setDraft((prev) => ({ ...prev, [field]: e.target.value }))}
        className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-800 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2]"
      />
    </div>
  )
}

function CaseModal({ caseData, isOpen, onClose, onOpenLogs, onOpenDocuments, currentUser, onCaseUpdated }) {
  const [pendingAction, setPendingAction] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [actionError, setActionError] = useState('')
  const [cancellationReason, setCancellationReason] = useState('')

  const [progressStatuses, setProgressStatuses] = useState([])
  const [progressLoading, setProgressLoading] = useState(false)
  const [newProgressLabel, setNewProgressLabel] = useState('')
  const [progressError, setProgressError] = useState('')
  const [progressSubmitting, setProgressSubmitting] = useState(false)

  const [beneficiary, setBeneficiary] = useState(null)
  const [beneficiaryLoading, setBeneficiaryLoading] = useState(false)
  const [editingBeneficiary, setEditingBeneficiary] = useState(false)
  const [beneficiaryDraft, setBeneficiaryDraft] = useState({})
  const [savingBeneficiary, setSavingBeneficiary] = useState(false)
  const [beneficiaryError, setBeneficiaryError] = useState('')

  const canAddProgress = currentUser && ['admin', 'advisor', 'student'].includes(currentUser.role)
  const canEditBeneficiary = currentUser && ['admin', 'advisor'].includes(currentUser.role)

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

  function startEditBeneficiary() {
    setBeneficiaryDraft({
      first_name: beneficiary?.first_name ?? '',
      last_name: beneficiary?.last_name ?? '',
      email: beneficiary?.email ?? '',
      identification_number: beneficiary?.identification_number ?? '',
      phone_number: beneficiary?.phone_number ?? '',
      residence_address: beneficiary?.residence_address ?? '',
    })
    setBeneficiaryError('')
    setEditingBeneficiary(true)
  }

  async function handleSaveBeneficiary(e) {
    e.preventDefault()
    setSavingBeneficiary(true)
    setBeneficiaryError('')
    try {
      const updated = await updateBeneficiary(caseData.beneficiaryId, beneficiaryDraft)
      setBeneficiary(updated)
      setEditingBeneficiary(false)
    } catch (err) {
      setBeneficiaryError(err.message)
    } finally {
      setSavingBeneficiary(false)
    }
  }

  useEffect(() => {
    if (!isOpen || !caseData?.beneficiaryId) {
      setBeneficiary(null)
      setEditingBeneficiary(false)
      setBeneficiaryDraft({})
      setBeneficiaryError('')
      return
    }
    setBeneficiaryLoading(true)
    getBeneficiary(caseData.beneficiaryId)
      .then(setBeneficiary)
      .catch(() => setBeneficiary(null))
      .finally(() => setBeneficiaryLoading(false))
  }, [isOpen, caseData?.beneficiaryId])

  useEffect(() => {
    if (!isOpen) {
      setPendingAction(null)
      setProcessing(false)
      setActionError('')
      setCancellationReason('')
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

          {/* Beneficiary */}
          <section>
            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Beneficiario</p>
              {canEditBeneficiary && beneficiary && !editingBeneficiary && (
                <button
                  type="button"
                  onClick={startEditBeneficiary}
                  className="flex items-center gap-1 rounded-md px-2 py-1 text-xs text-[#5454F2] transition hover:bg-indigo-50"
                  title="Editar beneficiario"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                  Editar
                </button>
              )}
            </div>

            {beneficiaryLoading && (
              <p className="mt-2 text-sm text-slate-400">Cargando...</p>
            )}

            {!beneficiaryLoading && !beneficiary && (
              <p className="mt-2 text-sm text-slate-400">No disponible.</p>
            )}

            {!beneficiaryLoading && beneficiary && !editingBeneficiary && (
              <div className="mt-2 grid grid-cols-1 gap-x-6 gap-y-2 rounded-lg border border-slate-100 bg-slate-50 p-3 sm:grid-cols-2">
                <Field label="Nombre" value={`${beneficiary.first_name} ${beneficiary.last_name}`.trim() || beneficiary.username} />
                <Field label="Usuario" value={`@${beneficiary.username}`} />
                <Field label="Cédula" value={beneficiary.identification_number || '—'} />
                <Field label="Correo" value={beneficiary.email || '—'} />
                <Field label="Teléfono" value={beneficiary.phone_number || '—'} />
                <Field label="Dirección" value={beneficiary.residence_address || '—'} />
              </div>
            )}

            {!beneficiaryLoading && editingBeneficiary && (
              <form onSubmit={handleSaveBeneficiary} className="mt-2 space-y-3 rounded-lg border border-indigo-100 bg-indigo-50/40 p-4">
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <EditField label="Nombre" field="first_name" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                  <EditField label="Apellido" field="last_name" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                  <EditField label="Cédula" field="identification_number" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                  <EditField label="Correo" field="email" type="email" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                  <EditField label="Teléfono" field="phone_number" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                  <EditField label="Dirección" field="residence_address" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                </div>
                {beneficiaryError && <p className="text-xs text-red-500">{beneficiaryError}</p>}
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={savingBeneficiary}
                    className="rounded-md bg-[#5454F2] px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-[#4747d7] disabled:opacity-50"
                  >
                    {savingBeneficiary ? 'Guardando...' : 'Guardar'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingBeneficiary(false)}
                    disabled={savingBeneficiary}
                    className="rounded-md border border-slate-300 px-3 py-1.5 text-xs text-slate-600 transition hover:bg-slate-100 disabled:opacity-50"
                  >
                    Cancelar
                  </button>
                </div>
              </form>
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
                    onClick={() => { setPendingAction(null); setActionError(''); setCancellationReason('') }}
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
