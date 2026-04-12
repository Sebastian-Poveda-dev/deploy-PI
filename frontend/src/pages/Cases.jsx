import { useEffect, useState } from 'react'
import DashboardLayout from '../layouts/DashboardLayout'
import CasesTable from '../components/CasesTable'
import { getCases } from '../services/caseService'

function Cases() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getCases()
      .then(setCases)
      .catch(() => setError('No fue posible cargar los casos. Intenta de nuevo.'))
      .finally(() => setLoading(false))
  }, [])

  function renderContent() {
    if (loading) {
      return (
        <div className="flex min-h-64 items-center justify-center">
          <p className="text-sm font-medium text-slate-400">Cargando casos...</p>
        </div>
      )
    }

    if (error) {
      return (
        <div className="flex min-h-64 items-center justify-center">
          <p className="text-sm font-medium text-red-500">{error}</p>
        </div>
      )
    }

    return <CasesTable cases={cases} />
  }

  return (
    <DashboardLayout>
      <section className="mx-auto w-full max-w-7xl space-y-6">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-bold text-slate-800">Casos</h1>
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-lg bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7]"
          >
            Crear Caso
          </button>
        </header>

        {renderContent()}
      </section>
    </DashboardLayout>
  )
}

export default Cases
