import { render, screen } from '@testing-library/react'
import { AuthorSearchResults } from './author-search-results'

describe('AuthorSearchResults', () => {
  it('renders empty state when no search query', () => {
    render(<AuthorSearchResults searchQuery="" />)

    expect(screen.getByText('작가 검색')).toBeInTheDocument()
    expect(
      screen.getByText('검색어를 입력하면 작가를 찾을 수 있습니다.')
    ).toBeInTheDocument()
  })

  it('renders coming soon message when search query exists', () => {
    render(<AuthorSearchResults searchQuery="test" />)

    expect(screen.getByText('작가 검색 준비 중')).toBeInTheDocument()
    expect(
      screen.getByText('작가 검색 기능은 곧 제공될 예정입니다.')
    ).toBeInTheDocument()
    expect(
      screen.getByText('현재는 소설 목록에서 작가 정보를 확인할 수 있습니다.')
    ).toBeInTheDocument()
  })

  it('matches snapshot without search query', () => {
    const { asFragment } = render(<AuthorSearchResults searchQuery="" />)
    expect(asFragment()).toMatchSnapshot()
  })

  it('matches snapshot with search query', () => {
    const { asFragment } = render(<AuthorSearchResults searchQuery="author" />)
    expect(asFragment()).toMatchSnapshot()
  })
})
