import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import ImportantNoticesPanel from '../components/ImportantNoticesPanel'
import DashboardLayout from '../layouts/DashboardLayout'
import { getDocumentNotifications } from '../services/documentService'
import { getCancellationNotifications, markCancellationNotificationRead } from '../services/caseService'
import { getCurrentUser } from '../services/userService'

function Dashboard() {
  const navigate = useNavigate()
  const [currentUser, setCurrentUser] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [activeFilter, setActiveFilter] = useState('all')
  const [isNoticesOpen, setIsNoticesOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [cancellationNotifs, setCancellationNotifs] = useState([])
  const isBeneficiary = currentUser?.role === 'beneficiary'

  useEffect(() => {
    let isMounted = true

    async function bootstrap() {
      setIsLoading(true)
      setError('')

      try {
        const user = await getCurrentUser()
        if (!isMounted) return
        setCurrentUser(user)

        if (user?.role !== 'beneficiary') {
          const [docNotifs, cancelNotifs] = await Promise.all([
            getDocumentNotifications(),
            user?.role === 'advisor' || user?.role === 'admin'
              ? getCancellationNotifications()
              : Promise.resolve([]),
          ])
          if (!isMounted) return
          setNotifications(docNotifs)
          setCancellationNotifs(cancelNotifs.filter((n) => !n.is_read))
        }
      } catch (requestError) {
        if (!isMounted) return
        setError(
          requestError?.message ??
            'No fue posible cargar la informacion inicial del panel de inicio.',
        )
      } finally {
        if (!isMounted) return
        setIsLoading(false)
      }
    }

    bootstrap()

    return () => { isMounted = false }
  }, [])

  async function handleDismissCancellationNotif(notif) {
    await markCancellationNotificationRead(notif.id)
    setCancellationNotifs((prev) => prev.filter((n) => n.id !== notif.id))
  }

  return (
    <DashboardLayout>
      <section className="mx-auto w-full max-w-7xl space-y-6">
        <header className="rounded-[2rem] border border-slate-200 bg-white px-6 py-6 shadow-[0_14px_40px_rgba(15,23,42,0.05)]">
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#5454E9]">
              Inicio
            </p>
            <h1 className="text-3xl font-bold text-slate-900">
              {`Bienvenido${currentUser?.username ? `, ${currentUser.username}` : ''}`}
            </h1>
            <p className="max-w-3xl text-sm leading-6 text-[#88898C]">
              Consulta rapidamente los avisos que requieren atencion dentro del consultorio.
            </p>
          </div>
        </header>

        {cancellationNotifs.length > 0 && (
          <section className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-amber-600">
              Solicitudes de reasignación pendientes
            </p>
            {cancellationNotifs.map((notif) => (
              <div
                key={notif.id}
                className="flex items-start justify-between gap-4 rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4 shadow-sm"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-amber-900">{notif.message}</p>
                  <p className="mt-1 text-xs text-amber-700">Caso #{notif.case_id}</p>
                </div>
                <div className="flex shrink-0 gap-2">
                  <button
                    type="button"
                    onClick={() => navigate('/dashboard/cases', { state: { openCaseId: notif.case_id } })}
                    className="rounded-lg bg-amber-500 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-amber-600"
                  >
                    Ver caso
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDismissCancellationNotif(notif)}
                    className="rounded-lg border border-amber-300 px-3 py-1.5 text-xs font-medium text-amber-700 transition hover:bg-amber-100"
                  >
                    Descartar
                  </button>
                </div>
              </div>
            ))}
          </section>
        )}

        {isBeneficiary ? (
          <section className="mx-auto w-full max-w-4xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-800">Bienvenido</h2>
            <p className="mt-3 text-sm leading-6 text-slate-500">
              Desde aqui puedes consultar el estado actual de tu caso de forma simple y segura.
            </p>
            <Link
              to="/dashboard/cases"
              className="mt-6 inline-flex rounded-lg bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7]"
            >
              Ver estado del caso
            </Link>
          </section>
        ) : (
          <ImportantNoticesPanel
            notifications={notifications}
            activeFilter={activeFilter}
            onFilterChange={setActiveFilter}
            onOpenCase={(notification) =>
              navigate('/dashboard/cases', {
                state: {
                  openCaseId: notification.caseId,
                  openDocuments: true,
                },
              })
            }
            isOpen={isNoticesOpen}
            onToggleOpen={() => setIsNoticesOpen((currentValue) => !currentValue)}
            isLoading={isLoading}
            error={error}
          />
        )}
      </section>
    </DashboardLayout>
  )
}

export default Dashboard
