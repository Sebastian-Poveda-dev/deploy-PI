import { useEffect, useMemo, useState } from 'react'
import BeneficiaryCaseStatusModal from '../components/BeneficiaryCaseStatusModal'
import CaseDocumentsModal from '../components/CaseDocumentsModal'
import CaseLogsModal from '../components/CaseLogsModal'
import CaseModal from '../components/CaseModal'
import CasesTable from '../components/CasesTable'
import CreateCaseModal from '../components/CreateCaseModal'
import DashboardLayout from '../layouts/DashboardLayout'
import { getBeneficiaryCases, getCases } from '../services/caseService'
import { getCurrentUser } from '../services/userService'
import StatusBadge from '../components/StatusBadge'

function Cases() {
  const [cases, setCases] = useState([])
  const [beneficiaryMessage, setBeneficiaryMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({
    status: 'ALL',
    id: '',
    createdAt: '',
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
  const [isFiltersModalOpen, setIsFiltersModalOpen] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)

  const isBeneficiary = currentUser?.role === 'beneficiary'

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
      setCases((prev) => prev.map((caseItem) => (
        caseItem.id === updatedCase.id ? updatedCase : caseItem
      )))
      setSelectedCase(updatedCase)
      return
    }

    closeCaseDetails()
    getCases().then(setCases).catch(() => {})
  }

  const statusOptions = useMemo(() => {
    const uniqueStatuses = Array.from(new Set(cases.map((caseItem) => caseItem.status))).sort()
    return ['ALL', ...uniqueStatuses]
  }, [cases])

  const filteredCases = useMemo(() => {
    const idFilter = filters.id.trim()
    const createdAtFilter = filters.createdAt.trim()
    const beneficiaryFilter = filters.beneficiary.trim().toLowerCase()
    const assignedFilter = filters.assigned.trim().toLowerCase()

    return cases.filter((caseItem) => {
      const statusMatches = filters.status === 'ALL' || caseItem.status === filters.status
      const idMatches = !idFilter || String(caseItem.id).includes(idFilter)
      const createdAtMatches = !createdAtFilter || caseItem.createdAt === createdAtFilter

      const beneficiaryName = (caseItem.beneficiaryName || '').toLowerCase()
      const beneficiaryMatches = !beneficiaryFilter || beneficiaryName.includes(beneficiaryFilter)

      const assignedUsers = Array.isArray(caseItem.assignedUsersList) ? caseItem.assignedUsersList : []
      const assignedMatches =
        !assignedFilter ||
        assignedUsers.some((username) => username.toLowerCase().includes(assignedFilter))

      return statusMatches && idMatches && createdAtMatches && beneficiaryMatches && assignedMatches
    })
  }, [cases, filters])

  const hasActiveFilters = useMemo(() => {
    return (
      filters.status !== 'ALL' ||
      Boolean(filters.id.trim()) ||
      Boolean(filters.createdAt.trim()) ||
      Boolean(filters.beneficiary.trim()) ||
      Boolean(filters.assigned.trim())
    )
  }, [filters])

  const activeFiltersCount = useMemo(() => {
    let count = 0
    if (filters.status !== 'ALL') count += 1
    if (filters.id.trim()) count += 1
    if (filters.createdAt.trim()) count += 1
    if (filters.beneficiary.trim()) count += 1
    if (filters.assigned.trim()) count += 1
    return count
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
      createdAt: '',
      beneficiary: '',
      assigned: '',
    })
  }

  useEffect(() => {
    async function loadCasesPage() {
      setLoading(true)
      setError('')

      try {
        const user = await getCurrentUser()
        setCurrentUser(user)

        if (user?.role === 'beneficiary') {
          const result = await getBeneficiaryCases()
          setCases(result.cases)
          setBeneficiaryMessage(result.detail)
        } else {
          const data = await getCases()
          setCases(data)
          setBeneficiaryMessage('')
        }
      } catch {
        setError('No fue posible cargar los casos. Intenta de nuevo.')
      } finally {
        setLoading(false)
      }
    }

    loadCasesPage()
  }, [])

  function renderStaffContent() {
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

  function renderBeneficiaryContent() {
    if (loading) {
      return (
        <div className="flex min-h-64 items-center justify-center rounded-xl border border-slate-200 bg-white px-4">
          <p className="text-sm font-medium text-slate-400">Cargando estado del caso...</p>
        </div>
      )
    }

    if (error) {
      return (
        <div className="flex min-h-64 items-center justify-center rounded-xl border border-slate-200 bg-white px-4">
          <p className="text-sm font-medium text-red-500">{error}</p>
        </div>
      )
    }

    if (!cases.length) {
      return (
        <div className="flex min-h-64 items-center justify-center rounded-xl border border-slate-200 bg-white px-4">
          <p className="text-sm font-medium text-slate-500">
            {beneficiaryMessage || 'No tiene casos registrados'}
          </p>
        </div>
      )
    }

    return (
      <div className="grid gap-4 md:grid-cols-2">
        {cases.map((caseItem, index) => (
          <button
            key={caseItem.id}
            type="button"
            onClick={() => openCaseDetails(caseItem)}
            className="rounded-xl border border-slate-200 bg-white px-6 py-6 text-left shadow-sm transition-colors hover:bg-slate-50"
          >
            <p className="text-sm font-medium text-slate-500">Caso registrado {index + 1}</p>
            <div className="mt-4 flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Estado actual
                </p>
                <div className="mt-2">
                  <StatusBadge status={caseItem.status} />
                </div>
              </div>
            </div>
            <p className="mt-4 text-sm text-slate-500">
              Selecciona esta tarjeta para consultar el detalle del estado.
            </p>
          </button>
        ))}
      </div>
    )
  }

  return (
    <DashboardLayout>
      <section className="mx-auto w-full max-w-7xl space-y-6">
        {isBeneficiary ? (
          <>
            <header className="space-y-2">
              <h1 className="text-2xl font-bold text-slate-800">Estado de mi caso</h1>
              <p className="text-sm text-slate-500">
                Consulta el avance de tu caso. Esta vista es informativa y no permite cambios.
              </p>
            </header>
            {renderBeneficiaryContent()}
          </>
        ) : (
          <>
            <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <h1 className="text-2xl font-bold text-slate-800">Casos</h1>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={() => setIsFiltersModalOpen(true)}
                  className="inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100"
                >
                  {`Filtros (${activeFiltersCount})`}
                </button>
                <button
                  type="button"
                  onClick={clearFilters}
                  className="inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100"
                >
                  Limpiar
                </button>
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(true)}
                  className="inline-flex items-center justify-center rounded-lg bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7]"
                >
                  Crear Caso
                </button>
              </div>
            </header>
            {renderStaffContent()}
          </>
        )}
      </section>

      {!isBeneficiary ? (
        <>
          <div
            onClick={(event) => {
              if (event.target === event.currentTarget) {
                setIsFiltersModalOpen(false)
              }
            }}
            className={`fixed inset-0 z-[55] flex items-center justify-center bg-black/40 p-4 transition-opacity duration-300 ease-in-out ${
              isFiltersModalOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
            }`}
            aria-hidden={!isFiltersModalOpen}
          >
            <div
              className={`w-full max-w-3xl rounded-xl bg-white shadow-xl transition-all duration-300 ease-in-out ${
                isFiltersModalOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
              }`}
            >
              <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
                <h2 className="text-lg font-semibold text-slate-800">Filtros de Casos</h2>
                <button
                  type="button"
                  onClick={() => setIsFiltersModalOpen(false)}
                  className="rounded-md p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
                  aria-label="Cerrar filtros"
                >
                  <span className="text-lg leading-none">x</span>
                </button>
              </div>

              <div className="grid grid-cols-1 gap-3 px-6 py-5 sm:grid-cols-2 lg:grid-cols-3">
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
                  <label className="text-xs font-medium uppercase tracking-wide text-slate-500">Fecha de Creacion</label>
                  <input
                    type="date"
                    value={filters.createdAt}
                    onChange={setFilter('createdAt')}
                    className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 focus:border-[#5454F2] focus:outline-none"
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

                <div className="space-y-1.5 sm:col-span-2 lg:col-span-2">
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

              <div className="flex items-center justify-end gap-2 border-t border-slate-200 px-6 py-4">
                <button
                  type="button"
                  onClick={clearFilters}
                  className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
                >
                  Limpiar
                </button>
                <button
                  type="button"
                  onClick={() => setIsFiltersModalOpen(false)}
                  className="rounded-md bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7]"
                >
                  Aplicar
                </button>
              </div>
            </div>
          </div>

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
        </>
      ) : (
        <BeneficiaryCaseStatusModal
          caseData={selectedCase}
          isOpen={isDetailModalOpen}
          onClose={closeCaseDetails}
        />
      )}
    </DashboardLayout>
  )
}

export default Cases
