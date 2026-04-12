import { useEffect, useState } from 'react'
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

    return <CasesTable cases={cases} onRowClick={openCaseDetails} />
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
