import { useState } from 'react'
import { ask } from '../api'
import ResultItem from './ResultItem'

export default function QueryPanel() {
  const [q, setQ] = useState('How does the auth flow work?')
  
  // NEW: Create separate state for the best match and other matches
  const [bestItem, setBestItem] = useState(null);
  const [otherItems, setOtherItems] = useState([]);

  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)

  const handleAsk = async () => {
    setLoading(true)
    setBestItem(null); // Clear previous results
    setOtherItems([]);
    try {
      const res = await ask(q, 6)
      
      // NEW: Split the results array
      setBestItem(res.matches?.[0] || null);
      setOtherItems(res.matches?.slice(1) || []);

      setAnswer(res.answer || '')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h3>2) Ask a Question</h3>
      <textarea rows={3} value={q} onChange={e=>setQ(e.target.value)} />
      <div className="row" style={{justifyContent:'space-between'}}>
        <div className="small">Top‑K: 6</div>
        <button onClick={handleAsk} disabled={loading}>{loading ? 'Searching…' : 'Ask'}</button>
      </div>

      {answer && (
        <div className="card" style={{marginTop:12}}>
          <h3>💡 Answer</h3>
          <div className="small" style={{whiteSpace:'pre-line'}}>{answer}</div>
        </div>
      )}

      {/* NEW: Render the best item separately and prominently */}
      {bestItem && (
        <div style={{marginTop:12}}>
          <h4>🏆 Top Match</h4>
          <ResultItem item={bestItem} />
        </div>
      )}

      {/* NEW: Render the rest of the items in a grid below */}
      {otherItems.length > 0 && <h4 style={{marginTop:12}}>Other Results</h4>}
      <div className="grid" style={{marginTop:12}}>
        {otherItems.map((it, idx) => <ResultItem key={idx} item={it} />)}
      </div>
    </div>
  )
}