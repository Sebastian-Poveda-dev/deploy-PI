import { useEffect, useState } from 'react'
import DashboardLayout from '../layouts/DashboardLayout'
import { getUsers, createUserAsAdmin, updateUserAsAdmin, getCategories } from '../services/userService'

const STAFF_ROLES = ['admin', 'advisor', 'student']

const ROLE_LABELS = {
  admin: 'Admin',
  advisor: 'Asesor',
  student: 'Estudiante',
  beneficiary: 'Beneficiario',
}

const ROLE_COLORS = {
  admin: 'bg-purple-100 text-purple-700',
  advisor: 'bg-blue-100 text-blue-700',
  student: 'bg-green-100 text-green-700',
  beneficiary: 'bg-slate-100 text-slate-600',
}

const EMPTY_CREATE_FORM = { username: '', password: '', role: '', category_id: '', first_name: '', last_name: '', email: '', phone_number: '', identification_number: '' }

function RoleBadge({ role }) {
  const color = ROLE_COLORS[role] ?? 'bg-slate-100 text-slate-600'
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${color}`}>
      {ROLE_LABELS[role] ?? role}
    </span>
  )
}

function CreateUserModal({ isOpen, onClose, onCreated }) {
  const [form, setForm] = useState(EMPTY_CREATE_FORM)
  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState('')
  const [loading, setLoading] = useState(false)
  const [categories, setCategories] = useState([])

  useEffect(() => {
    if (isOpen) {
      getCategories().then(setCategories)
    } else {
      setForm(EMPTY_CREATE_FORM)
      setErrors({})
      setApiError('')
    }
  }, [isOpen])

  if (!isOpen) return null

  function set(field) {
    return (e) => {
      setForm((prev) => ({ ...prev, [field]: e.target.value }))
      setErrors((prev) => ({ ...prev, [field]: '' }))
    }
  }

  function validate() {
    const next = {}
    if (!form.username.trim()) next.username = 'El nombre de usuario es requerido.'
    if (!form.password.trim()) next.password = 'La contraseña es requerida.'
    if (!form.role) next.role = 'Selecciona un rol.'
    if (form.role === 'advisor' && !form.category_id) next.category_id = 'Selecciona una sala legal.'
    return next
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setApiError('')
    const fieldErrors = validate()
    if (Object.keys(fieldErrors).length > 0) { setErrors(fieldErrors); return }

    setLoading(true)
    try {
      const newUser = await createUserAsAdmin({
        username: form.username.trim(),
        password: form.password.trim(),
        role: form.role,
        category_id: form.role === 'advisor' ? form.category_id : undefined,
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        phone_number: form.phone_number.trim(),
        identification_number: form.identification_number.trim(),
      })
      setForm(EMPTY_CREATE_FORM)
      setErrors({})
      onCreated(newUser)
      onClose()
    } catch (err) {
      setApiError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const inputClass = 'w-full rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800 transition focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="w-full max-w-md rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-800">Crear Usuario</h2>
          <button type="button" onClick={onClose} className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600">✕</button>
        </div>
        <form onSubmit={handleSubmit} noValidate>
          <div className="space-y-4 px-6 py-5">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">Nombre</label>
                <input type="text" value={form.first_name} onChange={set('first_name')} disabled={loading} className={inputClass} placeholder="Nombre" />
              </div>
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">Apellido</label>
                <input type="text" value={form.last_name} onChange={set('last_name')} disabled={loading} className={inputClass} placeholder="Apellido" />
              </div>
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Cédula</label>
              <input type="text" value={form.identification_number} onChange={set('identification_number')} disabled={loading} className={inputClass} placeholder="Número de identificación" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">Teléfono</label>
                <input type="text" value={form.phone_number} onChange={set('phone_number')} disabled={loading} className={inputClass} placeholder="3001234567" />
              </div>
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">Correo</label>
                <input type="email" value={form.email} onChange={set('email')} disabled={loading} className={inputClass} placeholder="correo@ejemplo.com" />
              </div>
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Usuario</label>
              <input type="text" value={form.username} onChange={set('username')} disabled={loading} className={inputClass} placeholder="nombre_usuario" />
              {errors.username && <p className="text-xs text-red-500">{errors.username}</p>}
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Contraseña</label>
              <input type="password" value={form.password} onChange={set('password')} disabled={loading} className={inputClass} placeholder="••••••••" />
              {errors.password && <p className="text-xs text-red-500">{errors.password}</p>}
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Rol</label>
              <select
                value={form.role}
                onChange={(e) => {
                  const newRole = e.target.value
                  setForm((prev) => ({ ...prev, role: newRole, category_id: '' }))
                  setErrors((prev) => ({ ...prev, role: '', category_id: '' }))
                }}
                disabled={loading}
                className={inputClass}
              >
                <option value="">Selecciona un rol</option>
                {STAFF_ROLES.map((role) => (
                  <option key={role} value={role}>{ROLE_LABELS[role]}</option>
                ))}
              </select>
              {errors.role && <p className="text-xs text-red-500">{errors.role}</p>}
            </div>

            {form.role === 'advisor' && (
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">Sala Legal</label>
                <select value={form.category_id} onChange={set('category_id')} disabled={loading} className={inputClass}>
                  <option value="">Selecciona una sala</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
                {errors.category_id && <p className="text-xs text-red-500">{errors.category_id}</p>}
              </div>
            )}

            {apiError && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{apiError}</p>}
          </div>
          <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
            <button type="button" onClick={onClose} disabled={loading} className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60">Cancelar</button>
            <button type="submit" disabled={loading} className="rounded-md bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white hover:bg-[#4343D8] disabled:opacity-60">{loading ? 'Creando...' : 'Crear'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}

function EditUserModal({ user, isOpen, onClose, onUpdated }) {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [identificationNumber, setIdentificationNumber] = useState('')
  const [role, setRole] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [changingPassword, setChangingPassword] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [apiError, setApiError] = useState('')
  const [loading, setLoading] = useState(false)
  const [categories, setCategories] = useState([])

  useEffect(() => {
    if (user) {
      setFirstName(user.first_name ?? '')
      setLastName(user.last_name ?? '')
      setEmail(user.email ?? '')
      setPhoneNumber(user.phone_number ?? '')
      setIdentificationNumber(user.identification_number ?? '')
      setRole(user.role)
      setCategoryId(user.category_id ?? '')
      setIsActive(user.is_active)
      setChangingPassword(false)
      setNewPassword('')
      setApiError('')
    }
  }, [user])

  useEffect(() => {
    if (isOpen) getCategories().then(setCategories)
  }, [isOpen])

  if (!isOpen || !user) return null

  async function handleSubmit(e) {
    e.preventDefault()
    setApiError('')
    setLoading(true)
    try {
      const patch = {}
      if (firstName.trim() !== (user.first_name ?? '')) patch.first_name = firstName.trim()
      if (lastName.trim() !== (user.last_name ?? '')) patch.last_name = lastName.trim()
      if (email.trim() !== (user.email ?? '')) patch.email = email.trim()
      if (phoneNumber.trim() !== (user.phone_number ?? '')) patch.phone_number = phoneNumber.trim()
      if (identificationNumber.trim() !== (user.identification_number ?? '')) patch.identification_number = identificationNumber.trim()
      if (role !== user.role) patch.role = role
      if (isActive !== user.is_active) patch.is_active = isActive
      const currentCatId = user.category_id ?? ''
      if (String(categoryId) !== String(currentCatId)) patch.category_id = categoryId || null
      if (newPassword.trim()) patch.password = newPassword.trim()

      if (Object.keys(patch).length === 0) { onClose(); return }

      const updated = await updateUserAsAdmin(user.id, patch)
      onUpdated(updated)
      onClose()
    } catch (err) {
      setApiError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const inputClass = 'w-full rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800 transition focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="w-full max-w-md rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-800">Editar — {user.username}</h2>
          <button type="button" onClick={onClose} className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600">✕</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 px-6 py-5">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">Nombre</label>
                <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} disabled={loading} className={inputClass} placeholder="Nombre" />
              </div>
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">Apellido</label>
                <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} disabled={loading} className={inputClass} placeholder="Apellido" />
              </div>
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Cédula</label>
              <input type="text" value={identificationNumber} onChange={(e) => setIdentificationNumber(e.target.value)} disabled={loading} className={inputClass} placeholder="Número de identificación" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">Teléfono</label>
                <input type="text" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} disabled={loading} className={inputClass} placeholder="3001234567" />
              </div>
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">Correo</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} disabled={loading} className={inputClass} placeholder="correo@ejemplo.com" />
              </div>
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Rol</label>
              <select value={role} onChange={(e) => setRole(e.target.value)} disabled={loading} className={inputClass}>
                {STAFF_ROLES.map((staffRole) => (
                  <option key={staffRole} value={staffRole}>
                    {ROLE_LABELS[staffRole]}
                  </option>
                ))}
              </select>
            </div>
            {role === 'advisor' && (
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-700">Sala Legal</label>
                <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} disabled={loading} className={inputClass}>
                  <option value="">Sin sala asignada</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
            )}
            <div className="flex items-center gap-3">
              <input
                id="is_active"
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                disabled={loading}
                className="h-4 w-4 rounded border-slate-300 text-[#5454F2] focus:ring-[#5454F2]"
              />
              <label htmlFor="is_active" className="text-sm font-medium text-slate-700">Usuario activo</label>
            </div>

            {!changingPassword ? (
              <button
                type="button"
                onClick={() => setChangingPassword(true)}
                disabled={loading}
                className="flex items-center gap-1.5 text-sm font-medium text-[#5454F2] hover:text-[#4343D8] disabled:opacity-50"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                </svg>
                Cambiar contraseña
              </button>
            ) : (
              <div className="space-y-1.5 rounded-lg border border-slate-200 bg-slate-50 p-3">
                <div className="flex items-center justify-between">
                  <label className="block text-sm font-medium text-slate-700">Nueva contraseña</label>
                  <button
                    type="button"
                    onClick={() => { setChangingPassword(false); setNewPassword('') }}
                    disabled={loading}
                    className="text-xs text-slate-400 hover:text-slate-600 disabled:opacity-50"
                  >
                    Cancelar
                  </button>
                </div>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  disabled={loading}
                  className={inputClass}
                  placeholder="Mínimo 8 caracteres"
                  autoComplete="new-password"
                  autoFocus
                />
              </div>
            )}

            {apiError && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{apiError}</p>}
          </div>
          <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
            <button type="button" onClick={onClose} disabled={loading} className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60">Cancelar</button>
            <button type="submit" disabled={loading} className="rounded-md bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white hover:bg-[#4343D8] disabled:opacity-60">{loading ? 'Guardando...' : 'Guardar'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}

function Permissions() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [editTarget, setEditTarget] = useState(null)

  useEffect(() => {
    getUsers()
      .then((data) => setUsers(data.filter((user) => user.role !== 'beneficiary')))
      .catch(() => setError('No fue posible cargar los usuarios.'))
      .finally(() => setLoading(false))
  }, [])

  function handleCreated(newUser) {
    if (newUser.role === 'beneficiary') return
    setUsers((prev) => [...prev, newUser].sort((a, b) => a.username.localeCompare(b.username)))
  }

  function handleUpdated(updated) {
    setUsers((prev) => {
      if (updated.role === 'beneficiary') {
        return prev.filter((user) => user.id !== updated.id)
      }
      return prev.map((user) => (user.id === updated.id ? updated : user))
    })
  }

  return (
    <DashboardLayout>
      <section className="mx-auto w-full max-w-5xl space-y-6">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-bold text-slate-800">Permisos</h1>
          <button
            type="button"
            onClick={() => setIsCreateOpen(true)}
            className="inline-flex items-center justify-center rounded-lg bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7]"
          >
            Crear Usuario
          </button>
        </header>

        {loading && (
          <div className="flex min-h-64 items-center justify-center">
            <p className="text-sm font-medium text-slate-400">Cargando usuarios...</p>
          </div>
        )}

        {error && (
          <div className="flex min-h-64 items-center justify-center">
            <p className="text-sm font-medium text-red-500">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead className="border-b border-slate-200 bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Nombre</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Usuario</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Rol</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Sala</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Estado</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((user) => (
                  <tr key={user.id} className={`transition-colors hover:bg-slate-50 ${!user.is_active ? 'opacity-50' : ''}`}>
                    <td className="px-6 py-4 text-slate-800">
                      {(user.first_name || user.last_name)
                        ? <><span className="font-medium">{`${user.first_name} ${user.last_name}`.trim()}</span></>
                        : <span className="text-slate-400 italic">Sin nombre</span>}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-800">{user.username}</td>
                    <td className="px-6 py-4"><RoleBadge role={user.role} /></td>
                    <td className="px-6 py-4 text-sm text-slate-600">{user.category_name || '—'}</td>
                    <td className="px-6 py-4">
                      {user.is_active
                        ? <span className="inline-block rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">Activo</span>
                        : <span className="inline-block rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-600">Inactivo</span>
                      }
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        type="button"
                        onClick={() => setEditTarget(user)}
                        className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-100"
                      >
                        Editar
                      </button>
                    </td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-sm text-slate-400">No hay usuarios registrados.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <CreateUserModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onCreated={handleCreated}
      />

      <EditUserModal
        user={editTarget}
        isOpen={!!editTarget}
        onClose={() => setEditTarget(null)}
        onUpdated={handleUpdated}
      />
    </DashboardLayout>
  )
}

export default Permissions
