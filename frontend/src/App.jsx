import { useState } from 'react'
import RepoForm from './components/RepoForm'
import QueryPanel from './components/QueryPanel'

export default function App() {
  const [isIngested, setIsIngested] = useState(false)

  return (
    <div className="app">
      <h1>RepoNaut:Semantic Code Query</h1>
      <p className="small">Paste a public GitHub URL or local path, index it, then ask questions about how it works.</p>
      
      {/* Pass a function to RepoForm to update the state on success */}
      <RepoForm onIngested={() => setIsIngested(true)} />

      {/* Conditionally render QueryPanel only after ingestion is successful */}
      {isIngested && <QueryPanel />}
    </div>
  )
}