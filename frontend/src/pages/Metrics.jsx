import { useEffect, useRef, useState } from 'react'
import DashboardLayout from '../layouts/DashboardLayout'
import { getMetrics, searchUserCases } from '../services/metricsService'

// ─── Shared primitives ────────────────────────────────────────────────────────

function Card({ title, children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-slate-200 bg-white p-6 shadow-sm ${className}`}>
      {title && <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">{title}</h2>}
      {children}
    </div>
  )
}

function StatCard({ label, value, sub }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-4xl font-bold text-slate-900">{value}</p>
      {sub && <p className="mt-1 text-sm text-slate-400">{sub}</p>}
    </div>
  )
}

// ─── Horizontal bar chart ─────────────────────────────────────────────────────

const BAR_COLORS = [
  'bg-[#5454F2]', 'bg-violet-400', 'bg-sky-400', 'bg-emerald-400',
  'bg-amber-400', 'bg-rose-400', 'bg-cyan-400', 'bg-fuchsia-400',
]

function HorizontalBar({ label, count, max, colorClass }) {
  const pct = max > 0 ? Math.round((count / max) * 100) : 0
  return (
    <div className="flex items-center gap-3">
      <span className="w-32 shrink-0 truncate text-right text-xs text-slate-600">{label}</span>
      <div className="flex-1 overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-4 rounded-full transition-all duration-500 ${colorClass}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-8 shrink-0 text-right text-xs font-semibold text-slate-700">{count}</span>
    </div>
  )
}

function HorizontalBarChart({ title, rows, labelKey, countKey }) {
  const max = Math.max(...rows.map((r) => r[countKey]), 1)
  return (
    <Card title={title}>
      <div className="space-y-3">
        {rows.map((row, i) => (
          <HorizontalBar
            key={row[labelKey]}
            label={row[labelKey]}
            count={row[countKey]}
            max={max}
            colorClass={BAR_COLORS[i % BAR_COLORS.length]}
          />
        ))}
        {rows.length === 0 && <p className="text-sm text-slate-400">Sin datos</p>}
      </div>
    </Card>
  )
}

// ─── Column chart (for time series) ──────────────────────────────────────────

function ColumnChart({ title, data, bars }) {
  const maxVal = Math.max(...data.flatMap((d) => bars.map((b) => d[b.key] ?? 0)), 1)

  return (
    <Card title={title}>
      {data.length === 0 ? (
        <p className="text-sm text-slate-400">Sin datos en los ultimos 12 meses</p>
      ) : (
        <div className="flex items-end gap-2 overflow-x-auto pb-2">
          {data.map((point) => (
            <div key={point.month} className="flex flex-col items-center gap-1 min-w-[48px]">
              <div className="flex items-end gap-0.5 h-32">
                {bars.map((bar) => {
                  const val = point[bar.key] ?? 0
                  const heightPct = Math.round((val / maxVal) * 100)
                  return (
                    <div key={bar.key} className="flex flex-col items-center justify-end h-full">
                      <span className="text-[9px] text-slate-500 mb-0.5">{val}</span>
                      <div
                        className={`w-5 rounded-t transition-all duration-500 ${bar.color}`}
                        style={{ height: `${heightPct}%` }}
                        title={`${bar.label}: ${val}`}
                      />
                    </div>
                  )
                })}
              </div>
              <span className="text-[9px] text-slate-500 rotate-45 origin-left mt-2 whitespace-nowrap">
                {point.month}
              </span>
            </div>
          ))}
        </div>
      )}
      {bars.length > 1 && (
        <div className="mt-4 flex gap-4">
          {bars.map((bar) => (
            <div key={bar.key} className="flex items-center gap-1.5 text-xs text-slate-600">
              <span className={`inline-block h-3 w-3 rounded-sm ${bar.color}`} />
              {bar.label}
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

// ─── Users table ──────────────────────────────────────────────────────────────

function UsersTable({ users }) {
  return (
    <Card title="Casos activos por usuario">
      {users.length === 0 ? (
        <p className="text-sm text-slate-400">Sin datos</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-xs uppercase tracking-wide text-slate-500">
                <th className="py-2 pr-4 text-left">Usuario</th>
                <th className="py-2 pr-4 text-left">Rol</th>
                <th className="py-2 text-right">Casos activos</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-slate-50 last:border-0">
                  <td className="py-2 pr-4 font-medium text-slate-800">
                    {u.first_name || u.last_name
                      ? `${u.first_name} ${u.last_name}`.trim()
                      : u.username}
                  </td>
                  <td className="py-2 pr-4 capitalize text-slate-500">{u.role}</td>
                  <td className="py-2 text-right font-semibold text-slate-800">{u.active_cases}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )
}

// ─── Resolution time table ────────────────────────────────────────────────────

function ResolutionTimeTable({ data }) {
  return (
    <Card title="Tiempo promedio de resolucion por categoria">
      {data.length === 0 ? (
        <p className="text-sm text-slate-400">Sin casos finalizados</p>
      ) : (
        <div className="space-y-3">
          {data.map((item) => (
            <div key={item.category} className="flex items-center justify-between">
              <span className="capitalize text-sm text-slate-700">{item.category}</span>
              <span className="text-sm font-semibold text-[#5454F2]">
                {item.avg_days === 0 ? '< 1 dia' : `${item.avg_days} dias`}
              </span>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

// ─── Status label helpers ─────────────────────────────────────────────────────

const STATUS_LABELS = {
  active: 'Activo',
  pending_authorization: 'Pendiente',
  in_progress: 'En progreso',
  finished: 'Finalizado',
  inactive: 'Inactivo',
  canceled: 'Cancelado',
}

const STATUS_COLORS = {
  active: 'bg-emerald-100 text-emerald-700',
  pending_authorization: 'bg-amber-100 text-amber-700',
  in_progress: 'bg-sky-100 text-sky-700',
  finished: 'bg-slate-100 text-slate-600',
  inactive: 'bg-slate-100 text-slate-500',
  canceled: 'bg-rose-100 text-rose-700',
}

// ─── Student search ───────────────────────────────────────────────────────────

function StudentSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  async function handleSearch(e) {
    e.preventDefault()
    const q = query.trim()
    if (!q) return
    setLoading(true)
    setError('')
    setResults(null)
    try {
      const data = await searchUserCases(q)
      setResults(data)
    } catch {
      setError('No fue posible realizar la búsqueda.')
    } finally {
      setLoading(false)
    }
  }

  function handleClear() {
    setQuery('')
    setResults(null)
    setError('')
    inputRef.current?.focus()
  }

  return (
    <Card title="Búsqueda de casos por usuario">
      <p className="mb-4 text-sm text-slate-500">
        Busca un estudiante o asesor por nombre o usuario para ver el detalle de sus casos asignados.
      </p>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Nombre, apellido o usuario..."
          className="flex-1 rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-[#5454F2] focus:outline-none focus:ring-2 focus:ring-[#5454F2]/20"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="rounded-lg bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#4343D8] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Buscando…' : 'Buscar'}
        </button>
        {results !== null && (
          <button
            type="button"
            onClick={handleClear}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-500 transition hover:bg-slate-50"
          >
            Limpiar
          </button>
        )}
      </form>

      {error && (
        <p className="mt-3 text-sm text-rose-600">{error}</p>
      )}

      {results !== null && !loading && (
        <div className="mt-5 space-y-3">
          {results.length === 0 ? (
            <p className="text-sm text-slate-400 italic">
              No se encontraron estudiantes ni asesores que coincidan con "{query}".
            </p>
          ) : (
            results.map((student) => (
              <div
                key={student.id}
                className="rounded-xl border border-slate-100 bg-slate-50 px-4 py-4"
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-slate-800">{student.full_name}</p>
                    <p className="text-xs text-slate-400">@{student.username}</p>
                  </div>
                  <div className="flex gap-3 text-right shrink-0">
                    <div>
                      <p className="text-2xl font-bold text-[#5454F2]">{student.active_cases}</p>
                      <p className="text-[10px] uppercase tracking-wide text-slate-400">Activos</p>
                    </div>
                    <div className="border-l border-slate-200 pl-3">
                      <p className="text-2xl font-bold text-slate-700">{student.total_cases}</p>
                      <p className="text-[10px] uppercase tracking-wide text-slate-400">Total</p>
                    </div>
                  </div>
                </div>

                {/* Status breakdown */}
                {student.by_status.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {student.by_status.map((s) => (
                      <span
                        key={s.status}
                        className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[s.status] ?? 'bg-slate-100 text-slate-600'}`}
                      >
                        {STATUS_LABELS[s.status] ?? s.status}
                        <span className="font-bold">{s.count}</span>
                      </span>
                    ))}
                  </div>
                )}

                {student.by_status.length === 0 && (
                  <p className="mt-2 text-xs text-slate-400 italic">Sin casos asignados.</p>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </Card>
  )
}

// ─── Main page ────────────────────────────────────────────────────────────────

function Metrics() {
  const [metrics, setMetrics] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getMetrics()
      .then(setMetrics)
      .catch(() => setError('No se pudieron cargar las metricas.'))
      .finally(() => setIsLoading(false))
  }, [])

  return (
    <DashboardLayout>
      <section className="mx-auto w-full max-w-7xl space-y-6">

        <header className="rounded-[2rem] border border-slate-200 bg-white px-6 py-6 shadow-[0_14px_40px_rgba(15,23,42,0.05)]">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#5454E9]">Panel</p>
          <h1 className="text-3xl font-bold text-slate-900">Metricas</h1>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-[#88898C]">
            Estadisticas generales del consultorio juridico.
          </p>
        </header>

        {isLoading && (
          <p className="text-center text-sm text-slate-400">Cargando metricas...</p>
        )}

        {error && (
          <p className="rounded-xl bg-red-50 p-4 text-center text-sm text-red-600">{error}</p>
        )}

        {metrics && (
          <>
            {/* ── Summary stat cards ── */}
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <StatCard
                label="Casos sin asignar"
                value={metrics.unassigned_cases}
                sub="Con estado activo"
              />
              <StatCard
                label="Total de casos"
                value={metrics.cancellation_rate.total}
              />
              <StatCard
                label="Cancelados"
                value={metrics.cancellation_rate.canceled}
                sub={`${(metrics.cancellation_rate.rate * 100).toFixed(1)}% del total`}
              />
              <StatCard
                label="Documentos vencidos"
                value={metrics.document_expiration.expired}
                sub={`${metrics.document_expiration.expiring_soon} por vencer (7 dias)`}
              />
            </div>

            {/* ── Distribution charts ── */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <HorizontalBarChart
                title="Casos por estado"
                rows={metrics.cases_by_status}
                labelKey="status"
                countKey="count"
              />
              <HorizontalBarChart
                title="Casos por categoria"
                rows={metrics.cases_by_category}
                labelKey="category"
                countKey="count"
              />
              <HorizontalBarChart
                title="Casos por subclinica"
                rows={metrics.cases_by_subclinic}
                labelKey="subclinic"
                countKey="count"
              />
            </div>

            {/* ── Time series charts ── */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <ColumnChart
                title="Velocidad de trabajo — casos finalizados por mes"
                data={metrics.working_velocity}
                bars={[{ key: 'count', label: 'Finalizados', color: 'bg-[#5454F2]' }]}
              />
              <ColumnChart
                title="Casos abiertos vs cerrados por mes"
                data={metrics.opened_vs_closed}
                bars={[
                  { key: 'opened', label: 'Abiertos', color: 'bg-emerald-400' },
                  { key: 'closed', label: 'Cerrados', color: 'bg-rose-400' },
                ]}
              />
            </div>

            {/* ── User workload + resolution time ── */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <UsersTable users={metrics.cases_per_user} />
              <ResolutionTimeTable data={metrics.avg_resolution_time} />
            </div>
          </>
        )}

        {/* ── Student case search (always visible) ── */}
        <StudentSearch />

      </section>
    </DashboardLayout>
  )
}

export default Metrics
