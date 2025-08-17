import { useState } from 'react'
import { ingest } from '../api'

export default function RepoForm({ onIngested }) {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [res, setRes] = useState(null)
  const [err, setErr] = useState(null)

  const handleIngest = async () => {
    setLoading(true); setErr(null)
    try {
      const data = await ingest(url)
      setRes(data)
      // This line now successfully signals the App component to show the QueryPanel
      onIngested?.(true)
    } catch(e) {
      setErr(String(e))
    } finally { setLoading(false) }
  }

  return (
    <div className="card">
      <h3>1) Link a GitHub Repository (or local path)</h3>
      <div className="row">
        <input placeholder="https://github.com/owner/repo or /path/to/repo" value={url} onChange={e=>setUrl(e.target.value)} />
        <button onClick={handleIngest} disabled={loading || !url}>{loading ? 'Ingesting…' : 'Ingest'}</button>
      </div>
      {res && <p className="small">Indexed chunks: <strong>{res.chunks}</strong></p>}
      {err && <p className="small" style={{color:'#faa'}}>Error: {err}</p>}
    </div>
  )
}