import { render, screen } from '@testing-library/react'
import { BranchSearchResults } from './branch-search-results'

describe('BranchSearchResults', () => {
  it('renders empty state when no search query', () => {
    render(<BranchSearchResults searchQuery="" />)

    expect(screen.getByText('브랜치 검색')).toBeInTheDocument()
    expect(
      screen.getByText('검색어를 입력하면 브랜치를 찾을 수 있습니다.')
    ).toBeInTheDocument()
  })

  it('renders coming soon message when search query exists', () => {
    render(<BranchSearchResults searchQuery="test" />)

    expect(screen.getByText('브랜치 검색 준비 중')).toBeInTheDocument()
    expect(
      screen.getByText('브랜치 검색 기능은 곧 제공될 예정입니다.')
    ).toBeInTheDocument()
    expect(
      screen.getByText('현재는 소설 상세 페이지에서 브랜치를 확인할 수 있습니다.')
    ).toBeInTheDocument()
  })

  it('matches snapshot without search query', () => {
    const { asFragment } = render(<BranchSearchResults searchQuery="" />)
    expect(asFragment()).toMatchSnapshot()
  })

  it('matches snapshot with search query', () => {
    const { asFragment } = render(<BranchSearchResults searchQuery="fantasy" />)
    expect(asFragment()).toMatchSnapshot()
  })
})
