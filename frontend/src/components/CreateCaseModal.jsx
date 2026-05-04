import { useEffect, useState } from 'react'
import { createCase } from '../services/caseService'
import { getBeneficiaries } from '../services/userService'

const CATEGORIES = [
  { id: 1, label: 'Laboral' },
  { id: 2, label: 'Penal' },
]

const SUBCLINICS = [
  { id: 1, label: 'Civil' },
  { id: 2, label: 'Laboral' },
  { id: 3, label: 'Penal' },
  { id: 4, label: 'Familia' },
]

const EMPTY_FORM = { description: '', categoryId: '', subclinicId: '', beneficiaryId: '' }

function Field({ label, error, children }) {
  return (
    <div className="space-y-1.5">
      <label className="block text-sm font-medium text-slate-700">{label}</label>
      {children}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  )
}

function CreateCaseModal({ isOpen, onClose, onCaseCreated }) {
  const [form, setForm] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState('')
  const [beneficiaries, setBeneficiaries] = useState([])

  useEffect(() => {
    if (!isOpen) return
    getBeneficiaries().then(setBeneficiaries)
  }, [isOpen])

  if (!isOpen) return null

  function set(field) {
    return (e) => {
      setForm((prev) => ({ ...prev, [field]: e.target.value }))
      setErrors((prev) => ({ ...prev, [field]: '' }))
    }
  }

  function validate() {
    const next = {}
    if (!form.description.trim()) next.description = 'La descripción es requerida.'
    if (!form.categoryId) next.categoryId = 'Selecciona una categoría.'
    if (!form.subclinicId) next.subclinicId = 'Selecciona una subclínica.'
    if (!form.beneficiaryId) next.beneficiaryId = 'Selecciona un beneficiario.'
    return next
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setApiError('')

    const fieldErrors = validate()
    if (Object.keys(fieldErrors).length > 0) {
      setErrors(fieldErrors)
      return
    }

    setLoading(true)
    try {
      const newCase = await createCase({
        description: form.description.trim(),
        categoryId: Number(form.categoryId),
        subclinicId: Number(form.subclinicId),
        beneficiaryId: Number(form.beneficiaryId),
      })
      setForm(EMPTY_FORM)
      setErrors({})
      onCaseCreated(newCase)
      onClose()
    } catch (err) {
      setApiError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function handleOverlayClick(e) {
    if (e.target === e.currentTarget) onClose()
  }

  const inputClass =
    'w-full rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 transition focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60'

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 animate-fade"
      onClick={handleOverlayClick}
    >
      <div className="w-full max-w-xl rounded-lg bg-white shadow-xl animate-scale">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-800">Crear Caso</h2>
          <button
            type="button"
            aria-label="Cerrar"
            onClick={onClose}
            className="rounded-md p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} noValidate>
          <div className="space-y-5 px-6 py-5">
            <Field label="Descripción" error={errors.description}>
              <textarea
                rows={4}
                placeholder="Describe el caso..."
                value={form.description}
                onChange={set('description')}
                disabled={loading}
                className={`${inputClass} resize-none`}
              />
            </Field>

            <Field label="Categoría" error={errors.categoryId}>
              <select
                value={form.categoryId}
                onChange={set('categoryId')}
                disabled={loading}
                className={inputClass}
              >
                <option value="">Selecciona una categoría</option>
                {CATEGORIES.map((c) => (
                  <option key={c.id} value={c.id}>{c.label}</option>
                ))}
              </select>
            </Field>

            <Field label="Subclínica" error={errors.subclinicId}>
              <select
                value={form.subclinicId}
                onChange={set('subclinicId')}
                disabled={loading}
                className={inputClass}
              >
                <option value="">Selecciona una subclínica</option>
                {SUBCLINICS.map((s) => (
                  <option key={s.id} value={s.id}>{s.label}</option>
                ))}
              </select>
            </Field>

            <Field label="Beneficiario" error={errors.beneficiaryId}>
              <select
                value={form.beneficiaryId}
                onChange={set('beneficiaryId')}
                disabled={loading}
                className={inputClass}
              >
                <option value="">Selecciona un beneficiario</option>
                {beneficiaries.map((b) => (
                  <option key={b.id} value={b.id}>{b.full_name}</option>
                ))}
              </select>
            </Field>

            {apiError && (
              <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{apiError}</p>
            )}
          </div>

          <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-md bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#4343D8] disabled:opacity-60"
            >
              {loading ? 'Creando...' : 'Crear Caso'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateCaseModal
