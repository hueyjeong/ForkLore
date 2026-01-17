import { render, screen } from '@testing-library/react'
import { HashtagPills } from './hashtag-pills'

describe('HashtagPills', () => {
  it('renders all tags when tags count is less than or equal to default maxDisplay (8)', () => {
    const tags = ['판타지', '하렘', '일상']
    render(<HashtagPills tags={tags} />)
    
    tags.forEach(tag => {
      expect(screen.getByText(`#${tag}`)).toBeInTheDocument()
    })
    expect(screen.queryByText(/\+\d+ more/)).not.toBeInTheDocument()
  })

  it('renders up to maxDisplay tags and "+N more" for remaining tags', () => {
    const tags = Array.from({ length: 10 }, (_, i) => `태그${i + 1}`)
    render(<HashtagPills tags={tags} maxDisplay={8} />)
    
    // First 8 tags should be visible
    for (let i = 0; i < 8; i++) {
      expect(screen.getByText(`#${tags[i]}`)).toBeInTheDocument()
    }
    
    // Remaining 2 tags should not be visible
    for (let i = 8; i < 10; i++) {
      expect(screen.queryByText(`#${tags[i]}`)).not.toBeInTheDocument()
    }
    
    // "+2 more" should be visible
    expect(screen.getByText('+2 more')).toBeInTheDocument()
  })

  it('respects custom maxDisplay prop', () => {
    const tags = ['태그1', '태그2', '태그3', '태그4', '태그5']
    render(<HashtagPills tags={tags} maxDisplay={3} />)
    
    for (let i = 0; i < 3; i++) {
      expect(screen.getByText(`#${tags[i]}`)).toBeInTheDocument()
    }
    expect(screen.queryByText(`#${tags[3]}`)).not.toBeInTheDocument()
    expect(screen.getByText('+2 more')).toBeInTheDocument()
  })

  it('renders nothing when tags array is empty', () => {
    const { container } = render(<HashtagPills tags={[]} />)
    expect(container.firstChild).toBeNull()
  })
})
