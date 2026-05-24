import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import bgImage from '../assets/images/login-bg.png'
import logo from '../assets/logo/logo-icesi-white.png'
import { registerBeneficiary } from '../services/userService'

const inputClass =
  'w-full rounded-md border border-[#CECFD4] bg-[#FFFFFF] px-4 py-2.5 text-sm text-[#000000] placeholder:text-[#CECFD4] transition duration-200 focus:border-[#5454F2] focus:outline-none'

const labelClass = 'block text-left text-sm font-medium text-[#000000]'

function Field({ id, label, type = 'text', placeholder, required = false }) {
  return (
    <div className="space-y-2">
      <label htmlFor={id} className={labelClass}>
        {label}{required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <input
        id={id}
        name={id}
        type={type}
        placeholder={placeholder}
        className={inputClass}
      />
    </div>
  )
}

function SelectField({ id, label, children, required = false }) {
  return (
    <div className="space-y-2">
      <label htmlFor={id} className={labelClass}>
        {label}{required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <select id={id} name={id} defaultValue="" className={inputClass}>
        <option value="" disabled>Selecciona una opción</option>
        {children}
      </select>
    </div>
  )
}

function SectionTitle({ children }) {
  return (
    <h2 className="text-sm font-semibold uppercase tracking-wide text-[#5454F2] border-b border-[#5454F2]/20 pb-1 pt-2">
      {children}
    </h2>
  )
}

function BeneficiaryRegister() {
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [extraFields, setExtraFields] = useState([])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    const formData = new FormData(event.currentTarget)
    const str = (key) => String(formData.get(key) || '').trim()

    const extra_info = {}
    for (const { key, value } of extraFields) {
      if (key.trim()) extra_info[key.trim()] = value
    }

    const payload = {
      first_name: str('first_name'),
      last_name: str('last_name'),
      email: str('email'),
      identification_number: str('identification_number'),
      document_type: str('document_type'),
      expedition_place: str('expedition_place'),
      landline_phone: str('landline_phone'),
      residence_address: str('residence_address'),
      neighborhood: str('neighborhood'),
      city: str('city'),
      department: str('department'),
      stratum: str('stratum'),
      phone_number: str('phone_number'),
      reception_medium: str('reception_medium'),
      how_they_found_out: str('how_they_found_out'),
      marital_status: str('marital_status'),
      education_level: str('education_level'),
      occupation: str('occupation'),
      return_date: str('return_date'),
      extra_info: JSON.stringify(extra_info),
    }

    if (!payload.first_name || !payload.last_name || !payload.email || !payload.identification_number) {
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

            <SectionTitle>Datos personales</SectionTitle>

            <div className="grid gap-5 sm:grid-cols-2">
              <Field id="first_name" label="Nombre" placeholder="Ingresa tu nombre" required />
              <Field id="last_name" label="Apellido" placeholder="Ingresa tu apellido" required />
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <SelectField id="document_type" label="Tipo de documento" required>
                <option value="CC">Cédula de ciudadanía</option>
                <option value="CE">Cédula de extranjería</option>
                <option value="TI">Tarjeta de identidad</option>
                <option value="PA">Pasaporte</option>
                <option value="NIT">NIT</option>
                <option value="OTRO">Otro</option>
              </SelectField>
              <Field id="identification_number" label="Número de identificación" placeholder="Ingresa tu número de identificación" required />
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <Field id="expedition_place" label="Lugar de expedición" placeholder="Ciudad de expedición del documento" />
              <SelectField id="marital_status" label="Estado civil">
                <option value="SOLTERO">Soltero/a</option>
                <option value="CASADO">Casado/a</option>
                <option value="UNION_LIBRE">Unión libre</option>
                <option value="DIVORCIADO">Divorciado/a</option>
                <option value="VIUDO">Viudo/a</option>
                <option value="SEPARADO">Separado/a</option>
              </SelectField>
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <SelectField id="education_level" label="Escolaridad">
                <option value="NINGUNO">Ninguno</option>
                <option value="PRIMARIA">Primaria</option>
                <option value="SECUNDARIA">Secundaria</option>
                <option value="TECNICO">Técnico</option>
                <option value="TECNOLOGO">Tecnólogo</option>
                <option value="UNIVERSITARIO">Universitario</option>
                <option value="POSGRADO">Posgrado</option>
              </SelectField>
              <Field id="occupation" label="Ocupación" placeholder="Ingresa tu ocupación" />
            </div>

            <SectionTitle>Información de contacto</SectionTitle>

            <div className="grid gap-5 sm:grid-cols-2">
              <Field id="email" label="Correo electrónico" type="email" placeholder="ejemplo@correo.com" required />
              <Field id="phone_number" label="Número de teléfono" placeholder="Ingresa tu número de teléfono" required />
            </div>

            <Field id="landline_phone" label="Teléfono fijo (si tiene)" placeholder="Ingresa tu teléfono fijo" />

            <SectionTitle>Ubicación</SectionTitle>

            <Field id="residence_address" label="Dirección de residencia" placeholder="Ingresa tu dirección de residencia" required />

            <div className="grid gap-5 sm:grid-cols-2">
              <Field id="neighborhood" label="Barrio" placeholder="Ingresa tu barrio" />
              <Field id="city" label="Ciudad" placeholder="Ingresa tu ciudad" />
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <Field id="department" label="Departamento" placeholder="Ingresa tu departamento" />
              <SelectField id="stratum" label="Estrato">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                <option value="6">6</option>
              </SelectField>
            </div>

            <SectionTitle>Información adicional</SectionTitle>

            <div className="grid gap-5 sm:grid-cols-2">
              <SelectField id="reception_medium" label="Medio de recepción">
                <option value="PRESENCIAL">Presencial</option>
                <option value="TELEFONICA">Telefónica</option>
                <option value="VIRTUAL">Virtual</option>
                <option value="OTRO">Otro</option>
              </SelectField>
              <Field id="how_they_found_out" label="Medio por el cual se enteró" placeholder="¿Cómo supo del consultorio?" />
            </div>

            <Field id="return_date" label="Fecha de regreso del usuario" type="date" />

            <SectionTitle>Campos adicionales</SectionTitle>

            <div className="space-y-3">
              {extraFields.map((entry, idx) => (
                <div key={idx} className="flex gap-2 items-center">
                  <input
                    type="text"
                    placeholder="Nombre del campo"
                    value={entry.key}
                    onChange={(e) => setExtraFields((prev) => prev.map((f, i) => i === idx ? { ...f, key: e.target.value } : f))}
                    className="flex-1 rounded-md border border-[#CECFD4] bg-[#FFFFFF] px-3 py-2 text-sm text-[#000000] placeholder:text-[#CECFD4] focus:border-[#5454F2] focus:outline-none"
                  />
                  <input
                    type="text"
                    placeholder="Valor"
                    value={entry.value}
                    onChange={(e) => setExtraFields((prev) => prev.map((f, i) => i === idx ? { ...f, value: e.target.value } : f))}
                    className="flex-1 rounded-md border border-[#CECFD4] bg-[#FFFFFF] px-3 py-2 text-sm text-[#000000] placeholder:text-[#CECFD4] focus:border-[#5454F2] focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setExtraFields((prev) => prev.filter((_, i) => i !== idx))}
                    className="rounded-md border border-[#CECFD4] px-2 py-2 text-sm text-slate-400 hover:border-red-300 hover:text-red-500 transition"
                    title="Eliminar campo"
                  >
                    ×
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={() => setExtraFields((prev) => [...prev, { key: '', value: '' }])}
                className="flex items-center gap-1 text-sm font-medium text-[#5454F2] hover:underline"
              >
                + Agregar campo
              </button>
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-[#5454F2] px-4 py-2.5 text-sm font-semibold text-[#FFFFFF] transition duration-200 hover:bg-[#4343D8] disabled:opacity-60"
            >
              {loading ? 'Registrando...' : 'Registrarme'}
            </button>

            <p className="text-center text-sm text-[#667085]">
              ¿Ya estás registrado?{' '}
              <Link to="/login" className="font-semibold text-[#5454F2] hover:text-[#4343D8]">
                Inicia sesión
              </Link>
            </p>
          </form>
        </section>
      </main>

      <footer className="fixed inset-x-0 bottom-0 z-20 border-t border-[#FFFFFF]/20 bg-[#5454F2]">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <img src={logo} alt="Icesi logo" className="h-20 w-auto" />

          <nav className="grid w-full grid-cols-2 gap-x-6 gap-y-2 text-sm text-[#FFFFFF] sm:w-auto sm:grid-cols-4 sm:gap-6">
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">Ir a ICESI</a>
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">Más información</a>
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">Soporte</a>
            <a href="#" className="text-center font-bold transition hover:text-[#CECFD4]">Ubicación</a>
          </nav>
        </div>
      </footer>
    </div>
  )
}

export default BeneficiaryRegister
