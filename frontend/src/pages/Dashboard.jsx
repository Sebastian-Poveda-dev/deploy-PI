import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import DashboardLayout from '../layouts/DashboardLayout'
import { getCurrentUser } from '../services/userService'

function Dashboard() {
  const [currentUser, setCurrentUser] = useState(null)

  useEffect(() => {
    getCurrentUser().then(setCurrentUser).catch(() => setCurrentUser(null))
  }, [])

  const isBeneficiary = currentUser?.role === 'beneficiary'

  return (
    <DashboardLayout>
      {isBeneficiary ? (
        <section className="mx-auto w-full max-w-4xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-800">Bienvenido</h1>
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
        <p className="text-sm text-[#88898C]">Bienvenido al sistema</p>
      )}
    </DashboardLayout>
  )
}

export default Dashboard
