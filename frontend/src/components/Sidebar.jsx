import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import logo from '../assets/logo/logo-icesi-white.png'
import { getCurrentUser } from '../services/userService'

const NAV_ITEMS = [
  { label: 'Inicio', path: '/dashboard' },
  { label: 'Casos', path: '/dashboard/cases' },
  { label: 'Chats' },
  { label: 'Permisos', path: '/dashboard/permissions' },
  { label: 'Metricas' },
]

function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const [currentUser, setCurrentUser] = useState(null)

  useEffect(() => {
    getCurrentUser().then(setCurrentUser).catch(() => setCurrentUser(null))
  }, [])

  const visibleItems = useMemo(() => {
    if (currentUser?.role === 'beneficiary') {
      return NAV_ITEMS.filter((item) => ['/dashboard', '/dashboard/cases'].includes(item.path))
    }

    return NAV_ITEMS
  }, [currentUser])

  return (
    <aside className="flex h-screen w-64 flex-shrink-0 flex-col bg-[#5454F2]">
      <div className="flex items-center justify-center px-6 py-8">
        <img src={logo} alt="Logo" className="h-20 w-auto" />
      </div>

      <nav className="flex-1 px-3">
        <ul className="space-y-1">
          {visibleItems.map((item) => (
            <li key={item.label}>
              <button
                type="button"
                onClick={() => item.path && navigate(item.path)}
                className={`w-full cursor-pointer rounded-md px-4 py-2.5 text-left text-sm font-medium text-[#FFFFFF] transition duration-200 hover:bg-white/10 ${
                  item.path && location.pathname === item.path ? 'bg-white/20' : ''
                }`}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="px-3 pb-6">
        <button
          type="button"
          onClick={() => navigate('/login')}
          className="w-full cursor-pointer rounded-md px-4 py-2.5 text-left text-sm font-medium text-[#CECFD4] transition duration-200 hover:bg-white/10 hover:text-[#FFFFFF]"
        >
          Cerrar sesion
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
