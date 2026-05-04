const FILTERS = [
  { id: 'all', label: 'Todos' },
  { id: 'upcoming', label: 'Proximo a vencer' },
  { id: 'urgent', label: 'Urgentes' },
  { id: 'expired', label: 'Vencidos' },
]

const EVENT_COPY = {
  upcoming: {
    title: 'Proximo a vencer',
    dotClass: 'bg-[#5454E9]',
  },
  upcoming_urgent: {
    title: 'Urgente',
    dotClass: 'bg-[#E4EB60]',
  },
  expired: {
    title: 'Vencido',
    dotClass: 'bg-red-500',
  },
}

function formatDate(dateValue) {
  if (!dateValue) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(`${dateValue}T00:00:00`))
}

function formatSubtitle(notification) {
  if (notification.eventType === 'expired') {
    return `Vencio el ${formatDate(notification.expirationDate)}`
  }

  if (notification.daysUntilExpiration === 0) {
    return 'Vence hoy'
  }

  if (notification.daysUntilExpiration === 1) {
    return 'Vence en 1 dia'
  }

  if (typeof notification.daysUntilExpiration === 'number') {
    return `Vence en ${notification.daysUntilExpiration} dias`
  }

  return formatDate(notification.expirationDate)
}

function filterNotifications(notifications, activeFilter) {
  if (activeFilter === 'upcoming') {
    return notifications.filter((notification) => notification.eventType === 'upcoming')
  }

  if (activeFilter === 'urgent') {
    return notifications.filter((notification) => notification.eventType === 'upcoming_urgent')
  }

  if (activeFilter === 'expired') {
    return notifications.filter((notification) => notification.eventType === 'expired')
  }

  return notifications
}

function NotificationRow({ notification, onOpenCase }) {
  const copy = EVENT_COPY[notification.eventType] ?? EVENT_COPY.upcoming

  return (
    <button
      type="button"
      onClick={() => onOpenCase(notification)}
      className="flex w-full items-start gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-left transition hover:border-[#5454E9]/30 hover:bg-slate-50"
    >
      <span className={`mt-1.5 h-2.5 w-2.5 flex-shrink-0 rounded-full ${copy.dotClass}`} />

      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-slate-900">
              {notification.documentName}
            </p>
            <p className="mt-1 text-xs font-medium uppercase tracking-[0.16em] text-[#5454E9]">
              {copy.title}
            </p>
          </div>

          <span className="whitespace-nowrap text-xs text-slate-400">
            {formatDate(notification.expirationDate)}
          </span>
        </div>

        <p className="mt-2 line-clamp-2 text-sm leading-6 text-[#88898C]">
          {notification.message}
        </p>

        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
          <span>{`Caso #${notification.caseId}`}</span>
          <span>{formatSubtitle(notification)}</span>
        </div>
      </div>
    </button>
  )
}

function ImportantNoticesPanel({
  notifications,
  activeFilter,
  onFilterChange,
  onOpenCase,
  isOpen,
  onToggleOpen,
  isLoading,
  error,
}) {
  const visibleNotifications = filterNotifications(notifications, activeFilter)
  const urgentCount = notifications.filter(
    (notification) => notification.eventType === 'upcoming_urgent',
  ).length

  return (
    <section className="relative">
      <button
        type="button"
        onClick={onToggleOpen}
        className="flex w-full items-center justify-between rounded-[1.75rem] border border-slate-200 bg-white px-5 py-4 text-left shadow-[0_18px_50px_rgba(84,84,233,0.08)] transition hover:border-[#5454E9]/25 hover:bg-slate-50"
      >
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#5454E9]">
            Avisos importantes
          </p>
          <p className="mt-2 text-lg font-bold text-slate-900">
            {notifications.length > 0
              ? `${notifications.length} notificacion(es) pendientes`
              : 'Sin notificaciones pendientes'}
          </p>
          <p className="mt-1 text-sm text-[#88898C]">
            Centro de avisos sobre recursos juridicos proximos a vencer.
          </p>
        </div>

        <div className="ml-4 flex items-center gap-3">
          {urgentCount > 0 ? (
            <span className="inline-flex items-center rounded-full bg-[#E4EB60] px-3 py-1 text-sm font-semibold text-slate-900">
              {`${urgentCount} urgente(s)`}
            </span>
          ) : null}

          <span className="inline-flex items-center rounded-full bg-[#5454E9] px-3 py-1 text-sm font-semibold text-white">
            {notifications.length}
          </span>
        </div>
      </button>

      {isOpen ? (
        <div className="absolute left-0 right-0 top-[calc(100%+12px)] z-30 overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white shadow-[0_24px_70px_rgba(15,23,42,0.14)]">
          <div className="border-b border-slate-200 px-5 py-4">
            <div className="flex flex-wrap items-center gap-3">
              {FILTERS.map((filterOption) => (
                <button
                  key={filterOption.id}
                  type="button"
                  onClick={() => onFilterChange(filterOption.id)}
                  className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
                    activeFilter === filterOption.id
                      ? 'border-[#5454E9] bg-[#5454E9] text-white'
                      : 'border-slate-200 bg-white text-slate-700 hover:border-[#5454E9]/40 hover:bg-slate-50'
                  }`}
                >
                  {filterOption.label}
                </button>
              ))}
            </div>
          </div>

          <div className="max-h-[28rem] overflow-y-auto bg-slate-50 p-4">
            {isLoading ? (
              <div className="flex min-h-40 items-center justify-center rounded-2xl bg-white">
                <p className="text-sm font-medium text-slate-400">Cargando notificaciones...</p>
              </div>
            ) : null}

            {!isLoading && error ? (
              <div className="rounded-2xl border border-red-100 bg-red-50 px-5 py-4">
                <p className="text-sm font-medium text-red-700">{error}</p>
              </div>
            ) : null}

            {!isLoading && !error && visibleNotifications.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-200 bg-white px-6 py-10 text-center">
                <p className="text-base font-semibold text-slate-900">No hay avisos en esta vista.</p>
                <p className="mt-2 text-sm leading-6 text-[#88898C]">
                  Cuando un documento entre en alerta, aparecera aqui.
                </p>
              </div>
            ) : null}

            {!isLoading && !error && visibleNotifications.length > 0 ? (
              <div className="space-y-3">
                {visibleNotifications.map((notification) => (
                  <NotificationRow
                    key={notification.id}
                    notification={notification}
                    onOpenCase={onOpenCase}
                  />
                ))}
              </div>
            ) : null}
          </div>
        </div>
      ) : null}
    </section>
  )
}

export default ImportantNoticesPanel
