import { useNavigate } from 'react-router-dom'
import logo from '../assets/logo/logo-icesi-white.png'

const NAV_ITEMS = [
  { label: 'Inicio' },
  { label: 'Casos' },
  { label: 'Chats' },
  { label: 'Permisos' },
  { label: 'Métricas' },
]

function Sidebar() {
  const navigate = useNavigate()

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
              <button className="w-full cursor-pointer rounded-md px-4 py-2.5 text-left text-sm font-medium text-[#FFFFFF] transition duration-200 hover:bg-white/10">
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
