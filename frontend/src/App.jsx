import { useEffect } from 'react'
import { useStore } from './store'
import LlamaTab from './LlamaTab'
import HiveTab from './HiveTab'
import ChatsTab from './ChatsTab'
import CarnageTab from './CarnageTab'
import RoadmapTab from './RoadmapTab'

export default function App() {
  const { activeTab, setActiveTab, fetchAll, health } = useStore()

  useEffect(() => {
    fetchAll()
    const interval = setInterval(fetchAll, 30000)
    return () => clearInterval(interval)
  }, [fetchAll])

  const tabs = [
    { id: 'hive', label: 'Hive' },
    { id: 'chats', label: 'Chats' },
    { id: 'carnage', label: 'Carnage' },
    { id: 'roadmap', label: 'Roadmap' },
    { id: 'llama', label: 'llama.cpp' },
  ]

  const renderTab = () => {
    switch (activeTab) {
      case 'hive': return <HiveTab />
      case 'chats': return <ChatsTab />
      case 'carnage': return <CarnageTab />
      case 'roadmap': return <RoadmapTab />
      case 'llama': return <LlamaTab />
      default: return <HiveTab />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <h1 className="text-lg font-bold">Symbiote-OS — Venom</h1>
        <div className={`text-xs px-2 py-0.5 rounded ${
          health?.status === 'ok'
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        }`}>
          {health?.status === 'ok' ? '● Orchestrator online' : '● Orchestrator offline'}
        </div>
      </header>

      <nav className="bg-white border-b flex space-x-1 px-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="pb-20">{renderTab()}</main>
    </div>
  )
}
