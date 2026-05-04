import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import bgImage from '../assets/images/login-bg.png'
import logo from '../assets/logo/logo-icesi-white.png'
import { buildApiUrl } from '../services/apiClient'

function InputField({
  id,
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  disabled = false,
  autoComplete,
}) {
  return (
    <div className="space-y-2">
      <label htmlFor={id} className="block text-left text-sm font-medium text-[#000000]">
        {label}
      </label>
      <input
        id={id}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        autoComplete={autoComplete}
        required
        className="w-full rounded-md border border-[#CECFD4] bg-[#FFFFFF] px-4 py-2.5 text-sm text-[#000000] placeholder:text-[#CECFD4] transition duration-200 focus:border-[#5454F2] focus:outline-none disabled:cursor-not-allowed disabled:opacity-70"
      />
    </div>
  )
}

function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (isLoading) {
      return
    }

    setIsLoading(true)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const response = await fetch(buildApiUrl('/users/login/'), {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        },
        body: new URLSearchParams({
          username: username.trim(),
          password,
        }),
      })

      let data = null

      try {
        data = await response.json()
      } catch {
        data = null
      }

      if (response.ok && data?.authenticated) {
        navigate(data?.role === 'beneficiary' ? '/dashboard/cases' : '/dashboard')
        return
      }

      if (response.status === 401) {
        setErrorMessage('Usuario o clave incorrectos.')
        return
      }

      setErrorMessage('No fue posible iniciar sesion. Intenta de nuevo.')
    } catch {
      setErrorMessage('No fue posible conectar con el servidor.')
    } finally {
      setIsLoading(false)
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
        <section className="w-full max-w-md rounded-lg bg-[#FFFFFF] p-6 shadow-2xl sm:p-8">
          <h1 className="mb-6 text-center text-3xl font-bold tracking-tight text-[#5454F2]">
            Inicio de Sesion
          </h1>

          <form className="space-y-5" onSubmit={handleSubmit}>
            <InputField
              id="username"
              label="Usuario"
              placeholder="Ingresa tu usuario"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              disabled={isLoading}
              autoComplete="username"
            />

            <InputField
              id="password"
              label="Contrasena"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              disabled={isLoading}
              autoComplete="current-password"
            />

            {errorMessage ? (
              <p className="text-sm text-[#D92D20]" role="alert">
                {errorMessage}
              </p>
            ) : null}

            {successMessage ? (
              <p className="text-sm text-[#067647]" role="status">
                {successMessage}
              </p>
            ) : null}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-md bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-[#FFFFFF] transition duration-200 hover:bg-[#4343D8] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isLoading ? 'Ingresando...' : 'Ingresar'}
            </button>
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

export default Login
