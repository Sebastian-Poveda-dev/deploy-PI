import { useEffect, useMemo, useState } from 'react'
import DashboardLayout from '../layouts/DashboardLayout'
import CasesTable from '../components/CasesTable'
import CaseModal from '../components/CaseModal'
import CaseLogsModal from '../components/CaseLogsModal'
import CaseDocumentsModal from '../components/CaseDocumentsModal'
import CreateCaseModal from '../components/CreateCaseModal'
import { getCases } from '../services/caseService'
import { getCurrentUser } from '../services/userService'

function Cases() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({
    status: 'ALL',
    id: '',
    beneficiary: '',
    assigned: '',
  })
  const [selectedCase, setSelectedCase] = useState(null)
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false)
  const [logsCaseId, setLogsCaseId] = useState(null)
  const [isLogsModalOpen, setIsLogsModalOpen] = useState(false)
  const [documentsCaseId, setDocumentsCaseId] = useState(null)
  const [isDocumentsModalOpen, setIsDocumentsModalOpen] = useState(false)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)

  function openCaseDetails(caseItem) {
    setSelectedCase(caseItem)
    setIsDetailModalOpen(true)
  }

  function closeCaseDetails() {
    setIsDetailModalOpen(false)
    setSelectedCase(null)
  }

  function openCaseLogs(caseId) {
    if (!caseId) return
    setLogsCaseId(caseId)
    setIsLogsModalOpen(true)
  }

  function closeCaseLogs() {
    setIsLogsModalOpen(false)
    setLogsCaseId(null)
  }

  function openCaseDocuments(caseId) {
    if (!caseId) return
    setDocumentsCaseId(caseId)
    setIsDocumentsModalOpen(true)
  }

  function closeCaseDocuments() {
    setIsDocumentsModalOpen(false)
    setDocumentsCaseId(null)
  }

  function handleCaseCreated(newCase) {
    setCases((prev) => [newCase, ...prev])
  }

  function handleCaseUpdated(updatedCase) {
    if (updatedCase) {
      // Approve: update case in list and keep modal open with new status
      setCases((prev) => prev.map((c) => c.id === updatedCase.id ? updatedCase : c))
      setSelectedCase(updatedCase)
    } else {
      // Reject: user lost their assignment — close modal and refresh list
      closeCaseDetails()
      getCases().then(setCases).catch(() => {})
    }
  }

  const statusOptions = useMemo(() => {
    const uniqueStatuses = Array.from(new Set(cases.map((caseItem) => caseItem.status))).sort()
    return ['ALL', ...uniqueStatuses]
  }, [cases])

  const filteredCases = useMemo(() => {
    const idFilter = filters.id.trim()
    const beneficiaryFilter = filters.beneficiary.trim().toLowerCase()
    const assignedFilter = filters.assigned.trim().toLowerCase()

    return cases.filter((caseItem) => {
      const statusMatches = filters.status === 'ALL' || caseItem.status === filters.status
      const idMatches = !idFilter || String(caseItem.id).includes(idFilter)

      const beneficiaryName = (caseItem.beneficiaryName || '').toLowerCase()
      const beneficiaryMatches = !beneficiaryFilter || beneficiaryName.includes(beneficiaryFilter)

      const assignedUsers = Array.isArray(caseItem.assignedUsersList) ? caseItem.assignedUsersList : []
      const assignedMatches =
        !assignedFilter ||
        assignedUsers.some((username) => username.toLowerCase().includes(assignedFilter))

      return statusMatches && idMatches && beneficiaryMatches && assignedMatches
    })
  }, [cases, filters])

  const hasActiveFilters = useMemo(() => {
    return (
      filters.status !== 'ALL' ||
      Boolean(filters.id.trim()) ||
      Boolean(filters.beneficiary.trim()) ||
      Boolean(filters.assigned.trim())
    )
  }, [filters])

  function setFilter(field) {
    return (event) => {
      const value = event.target.value
      setFilters((prev) => ({ ...prev, [field]: value }))
    }
  }

  function clearFilters() {
    setFilters({
      status: 'ALL',
      id: '',
      beneficiary: '',
      assigned: '',
    })
  }

  useEffect(() => {
    getCurrentUser().then(setCurrentUser)
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

    return (
      <CasesTable
        cases={filteredCases}
        onRowClick={openCaseDetails}
        emptyMessage={
          hasActiveFilters
            ? 'No hay casos que coincidan con los filtros seleccionados'
            : 'No tienes casos asignados'
        }
      />
    )
  }

  return (
    <DashboardLayout>
      <section className="mx-auto w-full max-w-7xl space-y-6">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-bold text-slate-800">Casos</h1>
          <button
            type="button"
            onClick={() => setIsCreateModalOpen(true)}
            className="inline-flex items-center justify-center rounded-lg bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7]"
          >
            Crear Caso
          </button>
        </header>

        <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">Filtros</h2>
            <button
              type="button"
              onClick={clearFilters}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-100"
            >
              Limpiar
            </button>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium uppercase tracking-wide text-slate-500">Estado</label>
              <select
                value={filters.status}
                onChange={setFilter('status')}
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 focus:border-[#5454F2] focus:outline-none"
              >
                {statusOptions.map((statusOption) => (
                  <option key={statusOption} value={statusOption}>
                    {statusOption === 'ALL' ? 'Todos' : statusOption}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium uppercase tracking-wide text-slate-500">ID del Caso</label>
              <input
                type="text"
                value={filters.id}
                onChange={setFilter('id')}
                placeholder="Ej. 12"
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 placeholder:text-slate-400 focus:border-[#5454F2] focus:outline-none"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium uppercase tracking-wide text-slate-500">Beneficiario</label>
              <input
                type="text"
                value={filters.beneficiary}
                onChange={setFilter('beneficiary')}
                placeholder="Nombre del beneficiario"
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 placeholder:text-slate-400 focus:border-[#5454F2] focus:outline-none"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium uppercase tracking-wide text-slate-500">Persona Asignada</label>
              <input
                type="text"
                value={filters.assigned}
                onChange={setFilter('assigned')}
                placeholder="Usuario asignado"
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 placeholder:text-slate-400 focus:border-[#5454F2] focus:outline-none"
              />
            </div>
          </div>
        </section>

        {renderContent()}
      </section>

      <CaseModal
        caseData={selectedCase}
        isOpen={isDetailModalOpen}
        onClose={closeCaseDetails}
        onOpenLogs={openCaseLogs}
        onOpenDocuments={openCaseDocuments}
        currentUser={currentUser}
        onCaseUpdated={handleCaseUpdated}
      />

      <CaseLogsModal caseId={logsCaseId} isOpen={isLogsModalOpen} onClose={closeCaseLogs} />

      <CaseDocumentsModal
        caseId={documentsCaseId}
        isOpen={isDocumentsModalOpen}
        onClose={closeCaseDocuments}
      />

      <CreateCaseModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCaseCreated={handleCaseCreated}
      />
    </DashboardLayout>
  )
}

export default Cases
