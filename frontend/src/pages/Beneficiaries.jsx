import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DashboardLayout from '../layouts/DashboardLayout'
import { getBeneficiariesWithCases } from '../services/userService'

const STATUS_LABELS = {
  active: 'Activo',
  pending_authorization: 'Pendiente',
  in_progress: 'En progreso',
  finished: 'Inactivo',
  inactive: 'Inactivo',
  canceled: 'Cancelado',
}

const STATUS_COLORS = {
  active: 'bg-emerald-100 text-emerald-700',
  pending_authorization: 'bg-amber-100 text-amber-700',
  in_progress: 'bg-blue-100 text-blue-700',
  finished: 'bg-slate-100 text-slate-500',
  inactive: 'bg-slate-100 text-slate-500',
  canceled: 'bg-red-100 text-red-600',
}

function InfoRow({ label, value }) {
  if (!value) return null
  return (
    <div className="flex gap-1.5 text-sm">
      <span className="shrink-0 font-medium text-slate-500">{label}:</span>
      <span className="text-slate-700 break-words">{value}</span>
    </div>
  )
}

function BeneficiaryCard({ beneficiary, onCaseClick }) {
  const [expanded, setExpanded] = useState(false)
  const hasCases = beneficiary.cases.length > 0

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 px-5 py-4">
        <div className="min-w-0">
          <p className="truncate text-base font-semibold text-slate-800">{beneficiary.full_name}</p>
          <p className="text-xs text-slate-400">@{beneficiary.username}</p>
        </div>
        <span className="shrink-0 rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-[#5454F2]">
          {beneficiary.cases.length} {beneficiary.cases.length === 1 ? 'caso' : 'casos'}
        </span>
      </div>

      {/* Contact info */}
      <div className="space-y-1.5 border-t border-slate-100 px-5 py-3">
        <InfoRow label="Cédula" value={beneficiary.identification_number} />
        <InfoRow label="Correo" value={beneficiary.email} />
        <InfoRow label="Teléfono" value={beneficiary.phone_number} />
        <InfoRow label="Dirección" value={beneficiary.residence_address} />
      </div>

      {/* Cases */}
      <div className="border-t border-slate-100 px-5 py-3">
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="flex w-full items-center justify-between text-xs font-semibold uppercase tracking-wide text-slate-400 hover:text-slate-600"
        >
          <span>Casos asignados</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`h-4 w-4 transition-transform ${expanded ? 'rotate-180' : ''}`}
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>

        {expanded && (
          <ul className="mt-2 space-y-1.5">
            {!hasCases && (
              <li className="text-sm text-slate-400">Sin casos registrados.</li>
            )}
            {beneficiary.cases.map((c) => (
              <li key={c.id}>
                <button
                  type="button"
                  onClick={() => onCaseClick(c.id)}
                  className="flex w-full items-center justify-between gap-3 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-left transition hover:border-[#5454F2]/30 hover:bg-indigo-50"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-700">
                      Caso #{c.id}
                      {c.category && <span className="ml-1.5 font-normal text-slate-400">· {c.category}</span>}
                    </p>
                    {c.subclinic && <p className="text-xs text-slate-400">{c.subclinic}</p>}
                  </div>
                  <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${STATUS_COLORS[c.status] ?? 'bg-slate-100 text-slate-500'}`}>
                    {STATUS_LABELS[c.status] ?? c.status}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

function Beneficiaries() {
  const navigate = useNavigate()
  const [beneficiaries, setBeneficiaries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    getBeneficiariesWithCases()
      .then(setBeneficiaries)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  function handleCaseClick(caseId) {
    navigate('/dashboard/cases', { state: { openCaseId: caseId } })
  }

  const filtered = beneficiaries.filter((b) => {
    const q = search.trim().toLowerCase()
    if (!q) return true
    return (
      b.full_name.toLowerCase().includes(q) ||
      b.username.toLowerCase().includes(q) ||
      b.identification_number.toLowerCase().includes(q) ||
      b.email.toLowerCase().includes(q)
    )
  })

  return (
    <DashboardLayout>
      <section className="mx-auto w-full max-w-5xl space-y-6">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Beneficiarios</h1>
            {!loading && !error && (
              <p className="mt-0.5 text-sm text-slate-500">{beneficiaries.length} beneficiario{beneficiaries.length !== 1 ? 's' : ''} encontrado{beneficiaries.length !== 1 ? 's' : ''}</p>
            )}
          </div>
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nombre, cédula o correo..."
            className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] sm:max-w-xs"
          />
        </header>

        {loading && (
          <div className="flex min-h-64 items-center justify-center">
            <p className="text-sm font-medium text-slate-400">Cargando beneficiarios...</p>
          </div>
        )}

        {error && (
          <div className="flex min-h-64 items-center justify-center">
            <p className="text-sm font-medium text-red-500">{error}</p>
          </div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <div className="flex min-h-64 items-center justify-center rounded-xl border border-slate-200 bg-white">
            <p className="text-sm font-medium text-slate-400">
              {search ? 'No hay resultados para esa búsqueda.' : 'No hay beneficiarios registrados.'}
            </p>
          </div>
        )}

        {!loading && !error && filtered.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((b) => (
              <BeneficiaryCard key={b.id} beneficiary={b} onCaseClick={handleCaseClick} />
            ))}
          </div>
        )}
      </section>
    </DashboardLayout>
  )
}

export default Beneficiaries
