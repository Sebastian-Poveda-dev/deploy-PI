import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ImportantNoticesPanel from '../components/ImportantNoticesPanel'
import DashboardLayout from '../layouts/DashboardLayout'
import { getDocumentNotifications } from '../services/documentService'
import { getCurrentUser } from '../services/userService'

function Dashboard() {
  const navigate = useNavigate()
  const [currentUser, setCurrentUser] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [activeFilter, setActiveFilter] = useState('all')
  const [isNoticesOpen, setIsNoticesOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let isMounted = true

    async function bootstrap() {
      setIsLoading(true)
      setError('')

      try {
        const [user, nextNotifications] = await Promise.all([
          getCurrentUser(),
          getDocumentNotifications(),
        ])

        if (!isMounted) return

        setCurrentUser(user)
        setNotifications(nextNotifications)
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

    return () => {
      isMounted = false
    }
  }, [])

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
      </section>
    </DashboardLayout>
  )
}

export default Dashboard
