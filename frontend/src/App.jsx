import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/Login'
import BeneficiaryRegister from './components/BeneficiaryRegister'
import BeneficiaryTracking from './pages/BeneficiaryTracking'
import Dashboard from './pages/Dashboard'
import Cases from './pages/Cases'
import Permissions from './pages/Permissions'
import Chats from './pages/Chats'
import Metrics from './pages/Metrics'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<BeneficiaryTracking />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<BeneficiaryRegister />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/dashboard/cases" element={<Cases />} />
        <Route path="/dashboard/chats" element={<Chats />} />
        <Route path="/dashboard/permissions" element={<Permissions />} />
        <Route path="/dashboard/metrics" element={<Metrics />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
