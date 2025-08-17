import { render, screen } from '@testing-library/react'
import RepoForm from '../components/RepoForm'

test('renders input and button', () => {
  render(<RepoForm onIngested={() => {}} />)
  expect(screen.getByPlaceholderText(/github/i)).toBeInTheDocument()
  expect(screen.getByRole('button', { name: /ingest/i })).toBeInTheDocument()
})
