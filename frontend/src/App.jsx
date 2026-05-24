import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { initCsrf } from './services/apiClient'
import Login from './components/Login'
import BeneficiaryRegister from './components/BeneficiaryRegister'
import BeneficiaryTracking from './pages/BeneficiaryTracking'
import Dashboard from './pages/Dashboard'
import Cases from './pages/Cases'
import Permissions from './pages/Permissions'
import Chats from './pages/Chats'
import Metrics from './pages/Metrics'
import Beneficiaries from './pages/Beneficiaries'

const PUBLIC_URL_PATTERNS = ['/users/me/', '/users/login/', '/users/register/', '/cases/track/']

function SessionExpiryHandler() {
  const navigate = useNavigate()

  useEffect(() => {
    const originalFetch = window.fetch

    window.fetch = async (...args) => {
      const url = typeof args[0] === 'string' ? args[0] : args[0]?.url ?? ''
      const response = await originalFetch(...args)

      if (
        response.status === 401 &&
        !PUBLIC_URL_PATTERNS.some((pattern) => url.includes(pattern))
      ) {
        navigate('/login', { replace: true })
      }

      return response
    }

    return () => {
      window.fetch = originalFetch
    }
  }, [navigate])

  return null
}

function App() {
  useEffect(() => {
    initCsrf()
  }, [])

  return (
    <BrowserRouter>
      <SessionExpiryHandler />
      <Routes>
        <Route path="/" element={<BeneficiaryTracking />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<BeneficiaryRegister />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/dashboard/cases" element={<Cases />} />
        <Route path="/dashboard/chats" element={<Chats />} />
        <Route path="/dashboard/permissions" element={<Permissions />} />
        <Route path="/dashboard/metrics" element={<Metrics />} />
        <Route path="/dashboard/beneficiaries" element={<Beneficiaries />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
