import { useLocation, useNavigate } from 'react-router-dom'
import logo from '../assets/logo/logo-icesi-white.png'

const NAV_ITEMS = [
  { label: 'Inicio', path: '/dashboard' },
  { label: 'Casos', path: '/dashboard/cases' },
  { label: 'Chats', path: '/dashboard/chats' },
  { label: 'Permisos', path: '/dashboard/permissions' },
  { label: 'Métricas' },
]

function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  function isActive(path) {
    if (!path) return false
    if (path === '/dashboard') return location.pathname === path
    return location.pathname === path || location.pathname.startsWith(`${path}/`)
  }

  return (
    <aside className="flex h-screen w-64 flex-shrink-0 flex-col bg-[#5454F2]">

      {/* Logo */}
      <div className="flex items-center justify-center px-6 py-8">
        <img src={logo} alt="Logo" className="h-20 w-auto" />
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3">
        <ul className="space-y-1">
          {NAV_ITEMS.map((item) => (
            <li key={item.label}>
              <button
                type="button"
                onClick={() => item.path && navigate(item.path)}
                className={`w-full cursor-pointer rounded-md px-4 py-2.5 text-left text-sm font-medium text-[#FFFFFF] transition duration-200 hover:bg-white/10 ${
                  isActive(item.path) ? 'bg-white/20' : ''
                }`}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Logout */}
      <div className="px-3 pb-6">
        <button
          onClick={() => navigate('/login')}
          className="w-full cursor-pointer rounded-md px-4 py-2.5 text-left text-sm font-medium text-[#CECFD4] transition duration-200 hover:bg-white/10 hover:text-[#FFFFFF]"
        >
          Cerrar sesión
        </button>
      </div>

    </aside>
  )
}

export default Sidebar
