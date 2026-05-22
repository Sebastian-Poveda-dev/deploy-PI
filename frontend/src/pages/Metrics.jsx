import { useEffect, useState } from 'react'
import DashboardLayout from '../layouts/DashboardLayout'
import { getMetrics } from '../services/metricsService'

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
      </section>
    </DashboardLayout>
  )
}

export default Metrics
