import Sidebar from '../components/Sidebar'

function DashboardLayout({ children }) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main
        className="flex-1 overflow-y-auto bg-gray-50 p-8"
        style={{ scrollbarGutter: 'stable' }}
      >
        {children}
      </main>
    </div>
  )
}

export default DashboardLayout
