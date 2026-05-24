import { useEffect, useState } from 'react'
import StatusBadge from './StatusBadge'
import { approveCase, rejectCase, requestCancellation, reviewCancellation, cancelCase, getCaseProgressStatuses, addCaseProgressStatus, reassignCase, CANCELLATION_REASONS } from '../services/caseService'
import { getBeneficiary, updateBeneficiary, getStaff } from '../services/userService'
import { canApproveCase, canRejectCase, canRequestCancellation, canReviewCancellation, canCancelCase } from '../utils/permissions'

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
  const [cancelReason, setCancelReason] = useState('')
  const [cancelReasonOther, setCancelReasonOther] = useState('')

  const [progressStatuses, setProgressStatuses] = useState([])
  const [progressLoading, setProgressLoading] = useState(false)
  const [newProgressLabel, setNewProgressLabel] = useState('')
  const [progressError, setProgressError] = useState('')
  const [progressSubmitting, setProgressSubmitting] = useState(false)

  const [beneficiary, setBeneficiary] = useState(null)
  const [beneficiaryLoading, setBeneficiaryLoading] = useState(false)
  const [editingBeneficiary, setEditingBeneficiary] = useState(false)
  const [beneficiaryDraft, setBeneficiaryDraft] = useState({})
  const [extraFieldsDraft, setExtraFieldsDraft] = useState([])
  const [savingBeneficiary, setSavingBeneficiary] = useState(false)
  const [beneficiaryError, setBeneficiaryError] = useState('')
  const [showMoreInfo, setShowMoreInfo] = useState(false)

  const [reassigning, setReassigning] = useState(false)
  const [staffList, setStaffList] = useState([])
  const [reassignStudentId, setReassignStudentId] = useState('')
  const [reassignAdvisorId, setReassignAdvisorId] = useState('')
  const [reassignError, setReassignError] = useState('')
  const [reassignSaving, setReassignSaving] = useState(false)

  const canAddProgress = currentUser && ['admin', 'advisor', 'student'].includes(currentUser.role)
  const canEditBeneficiary = currentUser && ['admin', 'advisor'].includes(currentUser.role)
  const canReassign = currentUser?.role === 'admin'

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
      document_type: beneficiary?.document_type ?? '',
      expedition_place: beneficiary?.expedition_place ?? '',
      landline_phone: beneficiary?.landline_phone ?? '',
      phone_number: beneficiary?.phone_number ?? '',
      residence_address: beneficiary?.residence_address ?? '',
      neighborhood: beneficiary?.neighborhood ?? '',
      city: beneficiary?.city ?? '',
      department: beneficiary?.department ?? '',
      stratum: beneficiary?.stratum ?? '',
      reception_medium: beneficiary?.reception_medium ?? '',
      how_they_found_out: beneficiary?.how_they_found_out ?? '',
      marital_status: beneficiary?.marital_status ?? '',
      education_level: beneficiary?.education_level ?? '',
      occupation: beneficiary?.occupation ?? '',
      return_date: beneficiary?.return_date ?? '',
    })
    const extra = beneficiary?.extra_info ?? {}
    setExtraFieldsDraft(Object.entries(extra).map(([key, value]) => ({ key, value })))
    setBeneficiaryError('')
    setEditingBeneficiary(true)
  }

  async function handleSaveBeneficiary(e) {
    e.preventDefault()
    setSavingBeneficiary(true)
    setBeneficiaryError('')
    try {
      const extra_info = {}
      for (const { key, value } of extraFieldsDraft) {
        if (key.trim()) extra_info[key.trim()] = value
      }
      const updated = await updateBeneficiary(caseData.beneficiaryId, { ...beneficiaryDraft, extra_info })
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
      setExtraFieldsDraft([])
      setBeneficiaryError('')
      setShowMoreInfo(false)
      return
    }
    setBeneficiaryLoading(true)
    getBeneficiary(caseData.beneficiaryId)
      .then(setBeneficiary)
      .catch(() => setBeneficiary(null))
      .finally(() => setBeneficiaryLoading(false))
  }, [isOpen, caseData?.beneficiaryId])

  useEffect(() => {
    if (!isOpen || !canReassign) {
      setReassigning(false)
      setReassignStudentId('')
      setReassignAdvisorId('')
      setReassignError('')
      return
    }
    getStaff().then(setStaffList).catch(() => setStaffList([]))
  }, [isOpen, canReassign])

  function openReassign() {
    setReassignStudentId(caseData?.assignedStudent?.id ? String(caseData.assignedStudent.id) : '')
    setReassignAdvisorId(caseData?.assignedAdvisor?.id ? String(caseData.assignedAdvisor.id) : '')
    setReassignError('')
    setReassigning(true)
  }

  async function handleReassign(e) {
    e.preventDefault()
    setReassignSaving(true)
    setReassignError('')
    try {
      const updated = await reassignCase(caseData.id, {
        newStudentId: reassignStudentId || null,
        newAdvisorId: reassignAdvisorId || null,
      })
      setReassigning(false)
      onCaseUpdated?.(updated)
    } catch (err) {
      setReassignError(err.message)
    } finally {
      setReassignSaving(false)
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
            <h2 className="text-xl font-bold text-slate-800">Caso #{caseData?.id}</h2>
            {caseData?.status ? <StatusBadge status={caseData.status} /> : null}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
            aria-label="Cerrar detalles del caso"
          >
            <span className="text-lg leading-none">×</span>
          </button>
        </div>

        {/* Body */}
        <div className="max-h-[70vh] space-y-6 overflow-y-auto px-6 py-5">
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Categoría</p>
              <p className="mt-1 text-sm font-medium text-slate-700">{caseData?.category || '—'}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Fecha de creación</p>
              <p className="mt-1 text-sm font-medium text-slate-700">{caseData?.createdAt || '—'}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Última actualización</p>
              <p className="mt-1 text-sm font-medium text-slate-700">{caseData?.updatedAt || '—'}</p>
            </div>
          </section>

          <section>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Usuarios asignados</p>
            {assignedUsersList.length ? (
              <ul className="mt-2 space-y-1">
                {assignedUsersList.map((user) => (
                  <li key={user} className="text-sm text-slate-700">{user}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-2 text-sm text-slate-500">Sin usuarios asignados.</p>
            )}
          </section>

          {/* Manual reassignment — admin only */}
          {canReassign && (
            <section>
              {!reassigning ? (
                <button
                  type="button"
                  onClick={openReassign}
                  className="flex items-center gap-1.5 text-sm font-medium text-[#5454F2] hover:text-[#4343D8]"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M8 5a1 1 0 100 2h5.586l-1.293 1.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L13.586 5H8zM12 15a1 1 0 100-2H6.414l1.293-1.293a1 1 0 10-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L6.414 15H12z" />
                  </svg>
                  Reasignar caso
                </button>
              ) : (
                <form onSubmit={handleReassign} className="space-y-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Reasignación manual</p>
                    <button
                      type="button"
                      onClick={() => setReassigning(false)}
                      disabled={reassignSaving}
                      className="text-xs text-slate-400 hover:text-slate-600 disabled:opacity-50"
                    >
                      Cancelar
                    </button>
                  </div>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <div className="space-y-1">
                      <label className="block text-[10px] font-semibold uppercase tracking-wide text-slate-500">Estudiante</label>
                      <select
                        value={reassignStudentId}
                        onChange={(e) => setReassignStudentId(e.target.value)}
                        disabled={reassignSaving}
                        className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-800 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60"
                      >
                        <option value="">Sin cambio</option>
                        {staffList.filter((u) => u.role === 'student').map((u) => (
                          <option key={u.id} value={u.id}>{u.username}</option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-1">
                      <label className="block text-[10px] font-semibold uppercase tracking-wide text-slate-500">Asesor</label>
                      <select
                        value={reassignAdvisorId}
                        onChange={(e) => setReassignAdvisorId(e.target.value)}
                        disabled={reassignSaving}
                        className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-800 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60"
                      >
                        <option value="">Sin cambio</option>
                        {staffList.filter((u) => u.role === 'advisor').map((u) => (
                          <option key={u.id} value={u.id}>{u.username}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  {reassignError && <p className="text-xs text-red-500">{reassignError}</p>}
                  <button
                    type="submit"
                    disabled={reassignSaving || (!reassignStudentId && !reassignAdvisorId)}
                    className="rounded-md bg-[#5454F2] px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-[#4747d7] disabled:opacity-50"
                  >
                    {reassignSaving ? 'Guardando...' : 'Guardar reasignación'}
                  </button>
                </form>
              )}
            </section>
          )}

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
              <div className="mt-2 rounded-lg border border-slate-100 bg-slate-50 p-3 space-y-3">
                {/* Always-visible summary */}
                <div className="grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
                  <Field label="Nombre" value={`${beneficiary.first_name} ${beneficiary.last_name}`.trim() || '—'} />
                  <Field label="Número de identificación" value={`${beneficiary.document_type ? `(${beneficiary.document_type}) ` : ''}${beneficiary.identification_number || '—'}`} />
                  <Field label="Teléfono" value={beneficiary.phone_number || '—'} />
                  <Field label="Correo" value={beneficiary.email || '—'} />
                </div>

                {/* Expandable detail */}
                <button
                  type="button"
                  onClick={() => setShowMoreInfo((v) => !v)}
                  className="flex items-center gap-1 text-xs font-medium text-[#5454F2] hover:underline"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className={`h-3.5 w-3.5 transition-transform ${showMoreInfo ? 'rotate-180' : ''}`}
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                  {showMoreInfo ? 'Menos información' : 'Más información'}
                </button>

                {showMoreInfo && (
                  <div className="space-y-3 border-t border-slate-200 pt-3">
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Datos personales</p>
                      <div className="grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
                        <Field label="Lugar de expedición" value={beneficiary.expedition_place || '—'} />
                        <Field label="Estado civil" value={beneficiary.marital_status || '—'} />
                        <Field label="Escolaridad" value={beneficiary.education_level || '—'} />
                        <Field label="Ocupación" value={beneficiary.occupation || '—'} />
                      </div>
                    </div>
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Ubicación</p>
                      <div className="grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
                        <Field label="Teléfono fijo" value={beneficiary.landline_phone || '—'} />
                        <Field label="Dirección" value={beneficiary.residence_address || '—'} />
                        <Field label="Barrio" value={beneficiary.neighborhood || '—'} />
                        <Field label="Ciudad" value={beneficiary.city || '—'} />
                        <Field label="Departamento" value={beneficiary.department || '—'} />
                        <Field label="Estrato" value={beneficiary.stratum || '—'} />
                      </div>
                    </div>
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Información adicional</p>
                      <div className="grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
                        <Field label="Medio de recepción" value={beneficiary.reception_medium || '—'} />
                        <Field label="Medio por el cual se enteró" value={beneficiary.how_they_found_out || '—'} />
                        <Field label="Fecha de regreso" value={beneficiary.return_date || '—'} />
                      </div>
                    </div>
                    {Object.keys(beneficiary.extra_info ?? {}).length > 0 && (
                      <div>
                        <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Campos adicionales</p>
                        <div className="grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
                          {Object.entries(beneficiary.extra_info).map(([key, value]) => (
                            <Field key={key} label={key} value={value || '—'} />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {!beneficiaryLoading && editingBeneficiary && (
              <form onSubmit={handleSaveBeneficiary} className="mt-2 space-y-4 rounded-lg border border-indigo-100 bg-indigo-50/40 p-4">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500 mb-2">Datos personales</p>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <EditField label="Nombre" field="first_name" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Apellido" field="last_name" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Número de identificación" field="identification_number" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Lugar de expedición" field="expedition_place" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Estado civil" field="marital_status" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Escolaridad" field="education_level" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Ocupación" field="occupation" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                  </div>
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500 mb-2">Contacto y ubicación</p>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <EditField label="Correo" field="email" type="email" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Teléfono" field="phone_number" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Teléfono fijo" field="landline_phone" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Dirección" field="residence_address" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Barrio" field="neighborhood" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Ciudad" field="city" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Departamento" field="department" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Estrato" field="stratum" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                  </div>
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500 mb-2">Información adicional</p>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <EditField label="Medio de recepción" field="reception_medium" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Medio por el cual se enteró" field="how_they_found_out" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                    <EditField label="Fecha de regreso" field="return_date" type="date" draft={beneficiaryDraft} setDraft={setBeneficiaryDraft} />
                  </div>
                </div>

                {/* Custom extra fields */}
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500 mb-2">Campos adicionales</p>
                  <div className="space-y-2">
                    {extraFieldsDraft.map((entry, idx) => (
                      <div key={idx} className="flex gap-2 items-center">
                        <input
                          type="text"
                          placeholder="Nombre del campo"
                          value={entry.key}
                          onChange={(e) => setExtraFieldsDraft((prev) => prev.map((f, i) => i === idx ? { ...f, key: e.target.value } : f))}
                          className="flex-1 rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs text-slate-800 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2]"
                        />
                        <input
                          type="text"
                          placeholder="Valor"
                          value={entry.value}
                          onChange={(e) => setExtraFieldsDraft((prev) => prev.map((f, i) => i === idx ? { ...f, value: e.target.value } : f))}
                          className="flex-1 rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs text-slate-800 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2]"
                        />
                        <button
                          type="button"
                          onClick={() => setExtraFieldsDraft((prev) => prev.filter((_, i) => i !== idx))}
                          className="rounded-md p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500 transition"
                          title="Eliminar campo"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={() => setExtraFieldsDraft((prev) => [...prev, { key: '', value: '' }])}
                      className="flex items-center gap-1 text-xs font-medium text-[#5454F2] hover:underline"
                    >
                      + Agregar campo
                    </button>
                  </div>
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
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Descripción</p>
            <div className="mt-2 max-h-52 overflow-y-auto rounded-lg border border-slate-200 bg-slate-50 p-3">
              <p className="text-sm leading-6 text-slate-700">
                {caseData?.description || 'Sin descripción disponible.'}
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
