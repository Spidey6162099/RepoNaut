import CodeBlock from './CodeBlock'

export default function ResultItem({ item }) {
  return (
    <div className="card">
      <div className="row" style={{justifyContent:'space-between'}}>
        <div><strong>{item.file}</strong></div>
        {typeof item.score === 'number' && (
          <div className="small">score: {item.score.toFixed(3)}</div>
        )}
      </div>
      <div className="small">lines {item.start}–{item.end}</div>
      <CodeBlock text={item.content} />
    </div>
  )
}
