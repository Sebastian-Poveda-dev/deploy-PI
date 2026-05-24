const STATUS_STYLES = {
  ACTIVE: 'bg-emerald-500 text-white',
  IN_PROGRESS: 'bg-blue-500 text-white',
  PENDING: 'bg-amber-400 text-slate-900',
  CANCELLED: 'bg-red-500 text-white',
  INACTIVE: 'bg-slate-400 text-white',
}

const STATUS_LABELS = {
  ACTIVE: 'Activo',
  IN_PROGRESS: 'En progreso',
  PENDING: 'Pendiente',
  CANCELLED: 'Cancelado',
  INACTIVE: 'Inactivo',
}

function formatStatusLabel(status) {
  return STATUS_LABELS[status] ?? status
    .toLowerCase()
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] ?? 'bg-slate-300 text-slate-900'

  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold tracking-wide ${style}`}
    >
      {formatStatusLabel(status)}
    </span>
  )
}

export default StatusBadge