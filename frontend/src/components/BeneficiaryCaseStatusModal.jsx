import { useEffect } from 'react'
import StatusBadge from './StatusBadge'

function BeneficiaryCaseStatusModal({ caseData, isOpen, onClose }) {
  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  return (
    <div
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
      className={`fixed inset-0 z-[60] flex items-center justify-center bg-black/40 p-4 transition-opacity duration-300 ease-in-out ${
        isOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
      }`}
      aria-hidden={!isOpen}
    >
      <div
        className={`w-full max-w-md rounded-xl bg-white shadow-xl transition-all duration-300 ease-in-out ${
          isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-800">Estado de tu caso</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
            aria-label="Cerrar estado del caso"
          >
            <span className="text-lg leading-none">x</span>
          </button>
        </div>

        <div className="space-y-5 px-6 py-6">
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-5 py-6 text-center">
            <p className="text-sm font-medium text-slate-500">Estado actual</p>
            <div className="mt-4 flex justify-center">
              {caseData?.status ? <StatusBadge status={caseData.status} /> : null}
            </div>
          </div>

          <p className="text-center text-sm text-slate-500">
            Esta consulta es solo de lectura. No puedes modificar la informacion del caso.
          </p>
        </div>
      </div>
    </div>
  )
}

export default BeneficiaryCaseStatusModal
