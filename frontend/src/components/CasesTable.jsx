import StatusBadge from './StatusBadge'

const TABLE_HEADERS = [
  'ID',
  'Estado',
  'Categoría',
  'Beneficiario',
  'Fecha de creación',
  'Última actualización',
  'Usuarios asignados',
]

function CasesTable({ cases, onRowClick, emptyMessage = 'No hay casos para mostrar' }) {
  if (!cases.length) {
    return (
      <div className="flex min-h-64 items-center justify-center rounded-xl border border-slate-200 bg-white px-4">
        <p className="text-sm font-medium text-slate-400">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full table-auto text-left">
        <thead className="bg-slate-100">
          <tr>
            {TABLE_HEADERS.map((header) => (
              <th
                key={header}
                className="whitespace-nowrap px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-600"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {cases.map((item) => (
            <tr
              key={item.id}
              onClick={() => onRowClick?.(item)}
              className="cursor-pointer border-t border-slate-100 transition-colors hover:bg-slate-50"
            >
              <td className="whitespace-nowrap px-5 py-4 text-sm font-medium text-slate-700">#{item.id}</td>
              <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-700">
                <StatusBadge status={item.status} />
              </td>
              <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-700">{item.category}</td>
              <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-700">{item.beneficiaryName || '—'}</td>
              <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-700">{item.createdAt}</td>
              <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-700">{item.updatedAt}</td>
              <td className="min-w-56 px-5 py-4 text-sm text-slate-700">{item.assignedUsers}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default CasesTable