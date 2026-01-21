import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@/tests/utils/test-utils';
import { NovelCard } from './novel-card';

vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, className, whileHover, ...props }: any) => (
      <div className={className} {...props}>{children}</div>
    ),
  },
}));

describe('NovelCard', () => {
  const mockProps = {
    id: '1',
    title: 'The Chronicles of ForkLore',
    author: 'Test Author',
    coverUrl: 'https://example.com/cover.jpg',
    genre: 'FANTASY',
    rating: 4.5,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render novel card with all props', () => {
    render(<NovelCard {...mockProps} />);

    expect(screen.getByText(mockProps.title)).toBeInTheDocument();
    expect(screen.getByText(mockProps.author)).toBeInTheDocument();
    expect(screen.getByText(mockProps.genre)).toBeInTheDocument();
    expect(screen.getByText(mockProps.rating.toFixed(1))).toBeInTheDocument();
  });

  it('should render link with correct href', () => {
    render(<NovelCard {...mockProps} />);

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', `/novels/${mockProps.id}`);
  });

  it('should render image with correct alt and src', () => {
    render(<NovelCard {...mockProps} />);

    const image = screen.getByAltText(mockProps.title);
    expect(image).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <NovelCard {...mockProps} className="custom-class" />
    );

    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('custom-class');
  });

  it('should be wrapped with React.memo (check displayName)', () => {
    const memoizedComponent = NovelCard as React.MemoExoticComponent<any>;
    expect(memoizedComponent.$$typeof).toBe(Symbol.for('react.memo'));
  });

  it('should re-render when title prop changes', () => {
    const renderSpy = vi.fn();
    const NovelCardWithSpy = vi.fn((props: any) => {
      renderSpy(props);
      return <NovelCard {...props} />;
    });

    const { rerender } = render(<NovelCardWithSpy {...mockProps} />);
    const initialRenderCount = renderSpy.mock.calls.length;

    rerender(<NovelCardWithSpy {...mockProps} title="Different Title" />);

    expect(renderSpy.mock.calls.length).toBe(initialRenderCount + 1);
  });

  it('should re-render when rating prop changes', () => {
    const renderSpy = vi.fn();
    const NovelCardWithSpy = vi.fn((props: any) => {
      renderSpy(props);
      return <NovelCard {...props} />;
    });

    const { rerender } = render(<NovelCardWithSpy {...mockProps} />);
    const initialRenderCount = renderSpy.mock.calls.length;

    rerender(<NovelCardWithSpy {...mockProps} rating={5.0} />);

    expect(renderSpy.mock.calls.length).toBe(initialRenderCount + 1);
  });

  it('should display rating with one decimal place', () => {
    render(<NovelCard {...mockProps} rating={4.56789} />);

    expect(screen.getByText('4.6')).toBeInTheDocument();
  });
});
