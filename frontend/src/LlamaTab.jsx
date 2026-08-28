import { useEffect, useState } from 'react'
import { useStore } from './store'

export default function LlamaTab() {
  const { llama, setLlama } = useStore()
  const [models, setModels] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchLlama = async () => {
      try {
        const res = await fetch('http://localhost:8080/v1/models')
        const data = await res.json()
        setModels(data)
        setLoading(false)
      } catch (err) {
        console.error(err)
        setLoading(false)
      }
    }
    fetchLlama()
    const interval = setInterval(fetchLlama, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="p-6">Loading Llama...</div>

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">llama.cpp — Local Models</h2>

      {/* llama.cpp Health from orchestrator proxy */}
      {llama?.status === 'ok' ? (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          ✓ llama.cpp is running (status: ok)
        </div>
      ) : (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          ✗ llama.cpp is not reachable
        </div>
      )}

      {/* Models from llama.cpp directly */}
      {models?.data && models.data.length === 0 ? (
        <p className="text-gray-500">No models loaded. Add a GGUF to ~/projects/symbiote-os/models/ and restart llama.cpp.</p>
      ) : (
        <div className="space-y-3">
          {models?.data?.map((model) => (
            <div key={model.id} className="p-3 border rounded-lg">
              <h3 className="font-semibold">{model.id}</h3>
              <p className="text-sm text-gray-600">Owned by: {model.owned_by}</p>
            </div>
          ))}
        </div>
      )}

      {/* Quick API test */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-2">API Test</h3>
        <button
          onClick={async () => {
            const res = await fetch('http://localhost:3030/api/llm/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                model: 'qwen2.5-3b-instruct-q4_0',
                messages: [{ role: 'user', content: 'Hello from Symbiote-OS!' }],
                max_tokens: 50
              })
            })
            const data = await res.json()
            const msg = data.choices?.[0]?.message?.content || 'No response'
            alert(msg)
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Test llama.cpp via Orchestrator Proxy
        </button>
      </div>
    </div>
  )
}
