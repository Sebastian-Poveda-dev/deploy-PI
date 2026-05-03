import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import bgImage from '../assets/images/login-bg.png'
import logo from '../assets/logo/logo-icesi-white.png'
import { registerBeneficiary } from '../services/userService'

function Field({ id, label, type = 'text', placeholder }) {
  return (
    <div className="space-y-2">
      <label htmlFor={id} className="block text-left text-sm font-medium text-[#000000]">
        {label}
      </label>
      <input
        id={id}
        name={id}
        type={type}
        placeholder={placeholder}
        className="w-full rounded-md border border-[#CECFD4] bg-[#FFFFFF] px-4 py-2.5 text-sm text-[#000000] placeholder:text-[#CECFD4] transition duration-200 focus:border-[#5454F2] focus:outline-none"
      />
    </div>
  )
}

function BeneficiaryRegister() {
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    const formData = new FormData(event.currentTarget)
    const payload = {
      username: String(formData.get('username') || '').trim(),
      first_name: String(formData.get('first_name') || '').trim(),
      last_name: String(formData.get('last_name') || '').trim(),
      email: String(formData.get('email') || '').trim(),
      identification_number: String(formData.get('identification_number') || '').trim(),
      residence_address: String(formData.get('residence_address') || '').trim(),
      phone_number: String(formData.get('phone_number') || '').trim(),
      password1: String(formData.get('password1') || ''),
      password2: String(formData.get('password2') || ''),
    }

    if (!payload.username || !payload.first_name || !payload.last_name || !payload.email || !payload.identification_number) {
      setError('Completa los campos obligatorios para registrarte.')
      return
    }

    setLoading(true)
    try {
      await registerBeneficiary(payload)
      navigate('/')
    } catch (err) {
      const backendErrors = err?.errors || {}
      const firstField = Object.keys(backendErrors)[0]
      const firstMessage = firstField ? backendErrors[firstField]?.[0]?.message : ''
      setError(firstMessage || 'No fue posible completar el registro.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#000000]">
      <img
        src={bgImage}
        alt="Meeting background"
        className="absolute inset-0 h-full w-full object-cover object-center"
      />
      <div className="absolute inset-0 bg-[#000000]/40" aria-hidden="true" />

      <main className="relative z-10 flex min-h-screen items-center justify-center px-4 py-10 pb-28 sm:px-6 lg:px-8">
        <section className="w-full max-w-2xl rounded-lg bg-[#FFFFFF] p-6 shadow-2xl sm:p-8">
          <h1 className="mb-2 text-center text-3xl font-bold tracking-tight text-[#5454F2]">
            Registro de Beneficiario
          </h1>
          <p className="mb-6 text-center text-sm text-[#667085]">
            Completa los siguientes datos para crear tu cuenta.
          </p>

          <form className="space-y-5" onSubmit={handleSubmit}>
            <Field id="username" label="Usuario" placeholder="Ingresa tu usuario" />

            <div className="grid gap-5 sm:grid-cols-2">
              <Field id="first_name" label="Nombre" placeholder="Ingresa tu nombre" />
              <Field id="last_name" label="Apellido" placeholder="Ingresa tu apellido" />
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <div className="space-y-2">
                <label
                  htmlFor="email"
                  className="block text-left text-sm font-medium text-[#000000]"
                >
                  Correo electronico
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="ejemplo@correo.com"
                  className="w-full rounded-md border border-[#CECFD4] bg-[#FFFFFF] px-4 py-2.5 text-sm text-[#000000] placeholder:text-[#CECFD4] transition duration-200 focus:border-[#5454F2] focus:outline-none"
                />
              </div>

              <Field
                id="phone_number"
                label="Numero de telefono"
                placeholder="Ingresa tu numero de telefono"
              />
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <Field
                id="identification_number"
                label="Numero de identificacion"
                placeholder="Ingresa tu numero de identificacion"
              />

              <div className="space-y-2">
                <label
                  htmlFor="gender"
                  className="block text-left text-sm font-medium text-[#000000]"
                >
                  Genero
                </label>
                <select
                  id="gender"
                  name="gender"
                  defaultValue=""
                  className="w-full rounded-md border border-[#CECFD4] bg-[#FFFFFF] px-4 py-2.5 text-sm text-[#000000] transition duration-200 focus:border-[#5454F2] focus:outline-none"
                >
                  <option value="" disabled>
                    Selecciona una opcion
                  </option>
                  <option value="female">Femenino</option>
                  <option value="male">Masculino</option>
                  <option value="other">Otro</option>
                  <option value="prefer_not_to_say">Prefiero no decirlo</option>
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <label
                htmlFor="residence_address"
                className="block text-left text-sm font-medium text-[#000000]"
              >
                Direccion de residencia
              </label>
              <input
                id="residence_address"
                name="residence_address"
                type="text"
                placeholder="Ingresa tu direccion de residencia"
                className="w-full rounded-md border border-[#CECFD4] bg-[#FFFFFF] px-4 py-2.5 text-sm text-[#000000] placeholder:text-[#CECFD4] transition duration-200 focus:border-[#5454F2] focus:outline-none"
              />
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <Field
                id="password1"
                label="Contrasena"
                type="password"
                placeholder="Crea una contrasena"
              />

              <div className="space-y-2">
                <label
                  htmlFor="confirm_password"
                  className="block text-left text-sm font-medium text-[#000000]"
                >
                  Confirmar contrasena
                </label>
                <input
                  id="password2"
                  name="password2"
                  type="password"
                  placeholder="Repite tu contrasena"
                  className="w-full rounded-md border border-[#CECFD4] bg-[#FFFFFF] px-4 py-2.5 text-sm text-[#000000] placeholder:text-[#CECFD4] transition duration-200 focus:border-[#5454F2] focus:outline-none"
                />
              </div>
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-[#FFFFFF] transition duration-200 hover:bg-[#4343D8]"
            >
              {loading ? 'Registrando...' : 'Registrarme'}
            </button>

            <p className="text-center text-sm text-[#667085]">
              Already have an account?{' '}
              <Link to="/login" className="font-semibold text-[#5454F2] hover:text-[#4343D8]">
                Log in
              </Link>
            </p>
          </form>
        </section>
      </main>

      <footer className="fixed inset-x-0 bottom-0 z-20 border-t border-[#FFFFFF]/20 bg-[#5454F2]">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <img src={logo} alt="Icesi logo" className="h-20 w-auto" />

          <nav className="grid w-full grid-cols-2 gap-x-6 gap-y-2 text-sm text-[#FFFFFF] sm:w-auto sm:grid-cols-4 sm:gap-6">
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">
              Ir a ICESI
            </a>
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">
              Mas Informacion
            </a>
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">
              Soporte
            </a>
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">
              Ubicacion
            </a>
          </nav>
        </div>
      </footer>
    </div>
  )
}

export default BeneficiaryRegister
