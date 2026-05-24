import { useCallback, useEffect, useRef, useState } from 'react'
import { downloadDocument, getDocumentsByCase, uploadDocument } from '../services/documentService'

const EMPTY_FORM = { name: '', description: '', expirationDate: '' }

function CaseDocumentsModal({ caseId, isOpen, onClose }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState(EMPTY_FORM)
  const [file, setFile] = useState(null)
  const [formErrors, setFormErrors] = useState({})
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')

  const [downloadingId, setDownloadingId] = useState(null)

  const fileInputRef = useRef(null)

  const loadDocuments = useCallback(async () => {
    if (!caseId) return
    setLoading(true)
    setError('')
    try {
      const data = await getDocumentsByCase(caseId)
      setDocuments(data)
    } catch (err) {
      setError(err.message || 'No fue posible cargar los documentos.')
    } finally {
      setLoading(false)
    }
  }, [caseId])

  useEffect(() => {
    if (!isOpen || !caseId) return
    loadDocuments()
  }, [isOpen, caseId, loadDocuments])

  useEffect(() => {
    if (!isOpen) return undefined
    function handleKeyDown(e) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  function setField(field) {
    return (e) => {
      setForm((prev) => ({ ...prev, [field]: e.target.value }))
      setFormErrors((prev) => ({ ...prev, [field]: '' }))
    }
  }

  function handleFileChange(e) {
    setFile(e.target.files[0] ?? null)
    setFormErrors((prev) => ({ ...prev, file: '' }))
  }

  function validate() {
    const errors = {}
    if (!form.name.trim()) errors.name = 'El nombre es requerido.'
    if (!file) errors.file = 'Selecciona un archivo.'
    return errors
  }

  async function handleUpload(e) {
    e.preventDefault()
    setUploadError('')

    const errors = validate()
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors)
      return
    }

    const formData = new FormData()
    formData.append('name', form.name.trim())
    formData.append('description', form.description.trim())
    formData.append('file', file)
    if (form.expirationDate) {
      formData.append('expiration_date', form.expirationDate)
    }

    setUploading(true)
    try {
      await uploadDocument(caseId, formData)
      setForm(EMPTY_FORM)
      setFile(null)
      setFormErrors({})
      if (fileInputRef.current) fileInputRef.current.value = ''
      setUploadError('')
    } catch (err) {
      setUploadError(err.message || 'No fue posible subir el documento.')
    } finally {
      setUploading(false)
      await loadDocuments()
    }
  }

  async function handleDownload(doc) {
    setDownloadingId(doc.id)
    try {
      await downloadDocument(doc.id, doc.name)
    } catch (err) {
      setError(err.message || 'No fue posible descargar el documento.')
    } finally {
      setDownloadingId(null)
    }
  }

  const inputClass =
    'w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 transition focus:border-[#5454F2] focus:outline-none focus:ring-1 focus:ring-[#5454F2] disabled:opacity-60'

  return (
    <div
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
      className={`fixed inset-0 z-[60] flex items-center justify-center bg-black/40 p-4 transition-opacity duration-300 ease-in-out ${
        isOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
      }`}
      aria-hidden={!isOpen}
    >
      <div
        className={`flex h-[75vh] w-full max-w-2xl flex-col rounded-xl bg-white shadow-xl transition-all duration-300 ease-in-out ${
          isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h3 className="text-lg font-bold text-slate-800">Documentos del Caso #{caseId}</h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
            aria-label="Cerrar documentos"
          >
            <span className="text-lg leading-none">×</span>
          </button>
        </div>

        {/* Upload section */}
        <form onSubmit={handleUpload} noValidate className="border-b border-slate-200 px-6 py-4">
          <p className="mb-3 text-sm font-semibold text-slate-700">Subir documento</p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">
                Nombre <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                placeholder="Ej. Contrato laboral"
                value={form.name}
                onChange={setField('name')}
                disabled={uploading}
                className={inputClass}
              />
              {formErrors.name && <p className="mt-1 text-xs text-red-500">{formErrors.name}</p>}
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">
                Descripción
              </label>
              <input
                type="text"
                placeholder="Breve descripción del documento"
                value={form.description}
                onChange={setField('description')}
                disabled={uploading}
                className={inputClass}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">
                Archivo <span className="text-red-500">*</span>
              </label>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  className="shrink-0 rounded border-0 bg-[#5454F2] px-3 py-1 text-xs font-semibold text-white transition hover:bg-[#4747d7] disabled:opacity-60"
                >
                  Seleccionar archivo
                </button>
                <span className="truncate text-sm text-slate-500">
                  {file ? file.name : 'Ningún archivo seleccionado'}
                </span>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileChange}
                disabled={uploading}
                className="sr-only"
              />
              {formErrors.file && <p className="mt-1 text-xs text-red-500">{formErrors.file}</p>}
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">
                Fecha de vencimiento <span className="text-slate-400">(opcional)</span>
              </label>
              <input
                type="date"
                value={form.expirationDate}
                onChange={setField('expirationDate')}
                disabled={uploading}
                className={inputClass}
              />
            </div>
          </div>

          {uploadError && (
            <p className="mt-2 rounded-md bg-red-50 px-3 py-2 text-xs text-red-600">{uploadError}</p>
          )}

          <div className="mt-3 flex justify-end">
            <button
              type="submit"
              disabled={uploading}
              className="inline-flex items-center justify-center rounded-lg bg-[#5454F2] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#4747d7] disabled:opacity-60"
            >
              {uploading ? 'Subiendo...' : 'Subir documento'}
            </button>
          </div>
        </form>

        {/* Documents list */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading && <p className="text-sm text-slate-500">Cargando documentos...</p>}

          {!loading && error && <p className="text-sm text-red-500">{error}</p>}

          {!loading && !error && documents.length === 0 && (
            <p className="text-sm text-slate-400">No hay documentos</p>
          )}

          {!loading && !error && documents.length > 0 && (
            <ul className="space-y-2">
              {documents.map((doc) => (
                <li
                  key={doc.id}
                  className="flex items-start justify-between gap-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-slate-800">{doc.name}</p>
                    {doc.description && (
                      <p className="mt-0.5 truncate text-xs text-slate-500">{doc.description}</p>
                    )}
                    <div className="mt-1 flex flex-wrap gap-x-4 gap-y-0.5">
                      <span className="text-xs text-slate-400">
                        Subido por <span className="font-medium text-slate-600">{doc.uploadedBy}</span>
                      </span>
                      <span className="text-xs text-slate-400">{doc.uploadedAt}</span>
                      {doc.expirationDate && (
                        <span className="text-xs text-slate-400">
                          Vence: <span className="font-medium text-slate-600">{doc.expirationDate}</span>
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDownload(doc)}
                    disabled={downloadingId === doc.id}
                    className="shrink-0 rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100 disabled:opacity-60"
                  >
                    {downloadingId === doc.id ? 'Descargando...' : 'Descargar'}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

export default CaseDocumentsModal
