import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/Login'
import BeneficiaryRegister from './components/BeneficiaryRegister'
import Dashboard from './pages/Dashboard'
import Cases from './pages/Cases'
import Permissions from './pages/Permissions'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<BeneficiaryRegister />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/dashboard/cases" element={<Cases />} />
        <Route path="/dashboard/permissions" element={<Permissions />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
