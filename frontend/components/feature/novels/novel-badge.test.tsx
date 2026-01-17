import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { NovelBadge } from './novel-badge'

describe('NovelBadge', () => {
  it('renders PLUS badge when isPremium is true', () => {
    render(<NovelBadge isPremium={true} />)
    const plusBadge = screen.getByText('PLUS')
    expect(plusBadge).toBeInTheDocument()
    // Check if it has the correct background color class or style
    // Since it's using shadcn/ui Badge, it might use custom classes
  })

  it('renders 독점 badge when isExclusive is true', () => {
    render(<NovelBadge isExclusive={true} />)
    const exclusiveBadge = screen.getByText('독점')
    expect(exclusiveBadge).toBeInTheDocument()
  })

  it('renders both badges when both are true', () => {
    render(<NovelBadge isPremium={true} isExclusive={true} />)
    expect(screen.getByText('PLUS')).toBeInTheDocument()
    expect(screen.getByText('독점')).toBeInTheDocument()
  })

  it('renders nothing when both are false', () => {
    const { container } = render(<NovelBadge isPremium={false} isExclusive={false} />)
    expect(container.firstChild).toBeNull()
  })
})
