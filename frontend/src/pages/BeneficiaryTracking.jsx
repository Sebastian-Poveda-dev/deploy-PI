import { useState } from 'react'
import { Link } from 'react-router-dom'
import bgImage from '../assets/images/login-bg.png'
import logo from '../assets/logo/logo-icesi-white.png'
import StatusBadge from '../components/StatusBadge'
import { trackBeneficiaryCases } from '../services/caseService'

function formatDate(isoString) {
  if (!isoString) return ''
  const [date, time] = isoString.split('T')
  const [y, m, d] = date.split('-')
  return `${d}/${m}/${y}${time ? ' ' + time.slice(0, 5) : ''}`
}

function ProgressTimeline({ items }) {
  if (!items.length) {
    return (
      <p className="mt-3 text-sm italic text-slate-400">
        Aún no hay actualizaciones de progreso para este caso.
      </p>
    )
  }

  return (
    <ol className="relative mt-4 ml-3 border-l-2 border-[#5454F2]/25 space-y-5">
      {items.map((item, i) => (
        <li key={i} className="ml-5">
          <span className="absolute -left-[11px] flex h-5 w-5 items-center justify-center rounded-full bg-[#5454F2] ring-4 ring-white text-white text-[10px] font-bold">
            {i + 1}
          </span>
          <p className="text-sm font-medium text-slate-800 leading-snug">{item.label}</p>
          {item.created_at && (
            <time className="text-xs text-slate-400">{formatDate(item.created_at)}</time>
          )}
        </li>
      ))}
    </ol>
  )
}

function BeneficiaryTracking() {
  const [identificationNumber, setIdentificationNumber] = useState('')
  const [cases, setCases] = useState([])
  const [detail, setDetail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setDetail('')
    setHasSearched(true)

    const trimmedId = identificationNumber.trim()
    if (!trimmedId) {
      setCases([])
      setError('Ingresa tu cédula para consultar el estado del caso.')
      return
    }

    setLoading(true)
    try {
      const result = await trackBeneficiaryCases(trimmedId)
      setCases(result.cases)
      setDetail(result.detail)
    } catch (requestError) {
      setCases([])
      setError(requestError.message || 'No fue posible consultar el estado del caso.')
    } finally {
      setLoading(false)
    }
  }

  function renderResults() {
    if (!hasSearched) return null

    if (error) {
      return <p className="text-sm text-[#D92D20]">{error}</p>
    }

    if (!cases.length) {
      return <p className="text-sm text-[#667085]">{detail || 'No tiene casos registrados'}</p>
    }

    return (
      <div className="space-y-4">
        {cases.map((caseItem, index) => (
          <article
            key={`${caseItem.status}-${index}`}
            className="rounded-lg border border-slate-200 bg-white px-5 py-4 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Caso {index + 1}
              </p>
              <StatusBadge status={caseItem.status} />
            </div>

            <div className="mt-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-[#5454F2]">
                Progreso del caso
              </p>
              <ProgressTimeline items={caseItem.progressStatuses} />
            </div>
          </article>
        ))}
      </div>
    )
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#000000]">
      <img
        src={bgImage}
        alt="Meeting background"
        className="absolute inset-0 h-full w-full object-cover object-center"
      />
      <div className="absolute inset-0 bg-[#000000]/45" aria-hidden="true" />

      <main className="relative z-10 flex min-h-screen items-center justify-center px-4 py-10 pb-28 sm:px-6 lg:px-8">
        <section className="w-full max-w-xl rounded-lg bg-[#FFFFFF] p-6 shadow-2xl sm:p-8">
          <h1 className="mb-2 text-center text-3xl font-bold tracking-tight text-[#5454F2]">
            Consulta el estado de tu caso
          </h1>
          <p className="mb-6 text-center text-sm text-[#667085]">
            Ingresa tu cédula para conocer el progreso de los casos asociados a tu identidad.
          </p>

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <label
                htmlFor="identification_number"
                className="block text-left text-sm font-medium text-[#000000]"
              >
                Cédula
              </label>
              <input
                id="identification_number"
                name="identification_number"
                type="text"
                value={identificationNumber}
                onChange={(event) => setIdentificationNumber(event.target.value)}
                placeholder="Ingresa tu número de cédula"
                className="w-full rounded-md border border-[#CECFD4] bg-[#FFFFFF] px-4 py-2.5 text-sm text-[#000000] placeholder:text-[#98A2B3] transition duration-200 focus:border-[#5454F2] focus:outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-[#FFFFFF] transition duration-200 hover:bg-[#4343D8] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading ? 'Consultando...' : 'Consultar estado'}
            </button>
          </form>

          <div className="mt-6 space-y-4">
            {renderResults()}
            <p className="text-center text-sm text-[#667085]">
              Si eres parte del consultorio,{' '}
              <Link to="/login" className="font-semibold text-[#5454F2] hover:text-[#4343D8]">
                inicia sesión
              </Link>
            </p>
          </div>
        </section>
      </main>

      <footer className="fixed inset-x-0 bottom-0 z-20 border-t border-[#FFFFFF]/20 bg-[#5454F2]">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <img src={logo} alt="Icesi logo" className="h-20 w-auto" />

          <nav className="grid w-full grid-cols-2 gap-x-6 gap-y-2 text-sm text-[#FFFFFF] sm:w-auto sm:grid-cols-4 sm:gap-6">
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">
              Ir a ICESI
            </a>
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">
              Más Información
            </a>
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">
              Soporte
            </a>
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">
              Ubicación
            </a>
          </nav>
        </div>
      </footer>
    </div>
  )
}

export default BeneficiaryTracking
