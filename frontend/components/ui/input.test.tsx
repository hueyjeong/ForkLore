import { render, screen, fireEvent } from '@testing-library/react'
import { Input } from './input'
import React from 'react'
import { describe, it, expect, vi } from 'vitest'

describe('Input Component', () => {
  it('renders correctly', () => {
    render(<Input placeholder="test input" />)
    const input = screen.getByPlaceholderText('test input')
    expect(input).toBeInTheDocument()
  })

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLInputElement>()
    render(<Input ref={ref} />)
    expect(ref.current).toBeInstanceOf(HTMLInputElement)
  })

  it('handles onChange events', () => {
    const handleChange = vi.fn()
    render(<Input onChange={handleChange} />)
    const input = screen.getByRole('textbox') // Input has type="text" implicitly or explicit? Let's assume functionality
    fireEvent.change(input, { target: { value: 'hello' } })
    expect(handleChange).toHaveBeenCalledTimes(1)
  })
})
