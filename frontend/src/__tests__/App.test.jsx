import { render, screen } from '@testing-library/react'
import App from '../App'

test('renders headline', () => {
  render(<App />)
  expect(screen.getByText(/Semantic Code Query/i)).toBeInTheDocument()
})
