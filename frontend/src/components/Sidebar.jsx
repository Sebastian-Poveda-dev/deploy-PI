import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import logo from '../assets/logo/logo-icesi-white.png'
import { getCurrentUser, changeOwnPassword } from '../services/userService'

const ROLE_LABELS = {
  admin: 'Administrador',
  advisor: 'Asesor',
  student: 'Estudiante',
  beneficiary: 'Beneficiario',
}

function ProfileModal({ user, onClose }) {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [changingPassword, setChangingPassword] = useState(false)

  function handleClose() {
    setChangingPassword(false)
    setCurrentPassword('')
    setNewPassword('')
    setConfirmPassword('')
    setError('')
    setSuccess(false)
    onClose()
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess(false)
    if (newPassword !== confirmPassword) {
      setError('Las contraseñas nuevas no coinciden.')
      return
    }
    setSaving(true)
    try {
      await changeOwnPassword({ currentPassword, newPassword })
      setSuccess(true)
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setChangingPassword(false)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const inputClass = 'w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60'

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-start p-4 sm:items-center sm:justify-start sm:pl-72"
      onClick={(e) => e.target === e.currentTarget && handleClose()}
    >
      <div className="w-full max-w-sm rounded-xl bg-white shadow-2xl ring-1 ring-slate-200">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <h2 className="text-base font-semibold text-slate-800">Mi perfil</h2>
          <button
            type="button"
            onClick={handleClose}
            className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            ✕
          </button>
        </div>

        {/* User info */}
        <div className="flex items-center gap-3 px-5 py-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#5454F2] text-sm font-bold text-white">
            {user?.username?.[0]?.toUpperCase() ?? '?'}
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-800">{user?.username}</p>
            <p className="text-xs text-slate-400">{ROLE_LABELS[user?.role] ?? user?.role}</p>
          </div>
        </div>

        {/* Change password */}
        <div className="border-t border-slate-100 px-5 py-4">
          {success && (
            <p className="mb-3 rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
              Contraseña actualizada correctamente.
            </p>
          )}

          {!changingPassword ? (
            <button
              type="button"
              onClick={() => { setSuccess(false); setChangingPassword(true) }}
              className="flex items-center gap-2 text-sm font-medium text-[#5454F2] hover:text-[#4343D8]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
              Cambiar contraseña
            </button>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Nueva contraseña</p>
                <button
                  type="button"
                  onClick={() => { setChangingPassword(false); setError(''); setCurrentPassword(''); setNewPassword(''); setConfirmPassword('') }}
                  className="text-xs text-slate-400 hover:text-slate-600"
                >
                  Cancelar
                </button>
              </div>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Contraseña actual"
                disabled={saving}
                className={inputClass}
                autoComplete="current-password"
                autoFocus
              />
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Nueva contraseña (mín. 8 caracteres)"
                disabled={saving}
                className={inputClass}
                autoComplete="new-password"
              />
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirmar nueva contraseña"
                disabled={saving}
                className={inputClass}
                autoComplete="new-password"
              />
              {error && <p className="text-xs text-red-500">{error}</p>}
              <button
                type="submit"
                disabled={saving || !currentPassword || !newPassword || !confirmPassword}
                className="w-full rounded-md bg-[#5454F2] py-2 text-sm font-semibold text-white transition hover:bg-[#4747d7] disabled:opacity-50"
              >
                {saving ? 'Guardando...' : 'Actualizar contraseña'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

const NAV_ITEMS = [
  { label: 'Inicio', path: '/dashboard' },
  { label: 'Casos', path: '/dashboard/cases' },
  { label: 'Beneficiarios', path: '/dashboard/beneficiaries' },
  { label: 'Chats', path: '/dashboard/chats' },
  { label: 'Métricas', path: '/dashboard/metrics', roles: ['admin', 'advisor'] },
  { label: 'Permisos', path: '/dashboard/permissions', roles: ['admin'] },
]

function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const [currentUser, setCurrentUser] = useState(null)
  const [profileOpen, setProfileOpen] = useState(false)

  useEffect(() => {
    getCurrentUser().then(setCurrentUser).catch(() => setCurrentUser(null))
  }, [])

  const visibleItems = useMemo(() => {
    if (currentUser?.role === 'beneficiary') {
      return NAV_ITEMS.filter((item) => ['/dashboard', '/dashboard/cases'].includes(item.path))
    }

    return NAV_ITEMS.filter((item) => !item.roles || item.roles.includes(currentUser?.role))
  }, [currentUser])

  function isActive(path) {
    if (!path) return false
    if (path === '/dashboard') return location.pathname === path
    return location.pathname === path || location.pathname.startsWith(`${path}/`)
  }

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
                  isActive(item.path) ? 'bg-white/20' : ''
                }`}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="px-3 pb-6 space-y-1">
        {currentUser && currentUser.role !== 'beneficiary' && (
          <button
            type="button"
            onClick={() => setProfileOpen(true)}
            className="flex w-full items-center gap-2.5 cursor-pointer rounded-md px-4 py-2.5 text-left text-sm font-medium text-[#CECFD4] transition duration-200 hover:bg-white/10 hover:text-[#FFFFFF]"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
            Mi perfil
          </button>
        )}
        <button
          type="button"
          onClick={() => navigate('/login')}
          className="w-full cursor-pointer rounded-md px-4 py-2.5 text-left text-sm font-medium text-[#CECFD4] transition duration-200 hover:bg-white/10 hover:text-[#FFFFFF]"
        >
          Cerrar sesion
        </button>
      </div>

      {profileOpen && (
        <ProfileModal user={currentUser} onClose={() => setProfileOpen(false)} />
      )}
    </aside>
  )
}

export default Sidebar
