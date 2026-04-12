import DashboardLayout from '../layouts/DashboardLayout'
import CasesTable from '../components/CasesTable'

const MOCK_CASES = [
  {
    id: 1,
    status: 'ACTIVE',
    category: 'Laboral',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-05',
    assignedUsers: 'John Doe, Jane Smith',
  },
  {
    id: 2,
    status: 'IN_PROGRESS',
    category: 'Familiar',
    createdAt: '2024-02-10',
    updatedAt: '2024-02-14',
    assignedUsers: 'Ana Gomez, Carlos Diaz',
  },
  {
    id: 3,
    status: 'PENDING',
    category: 'Civil',
    createdAt: '2024-03-02',
    updatedAt: '2024-03-09',
    assignedUsers: 'Laura Ruiz',
  },
]

function Cases() {
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

        <CasesTable cases={MOCK_CASES} />
      </section>
    </DashboardLayout>
  )
}

export default Cases