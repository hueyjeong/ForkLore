import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { RankingHeader } from './ranking-header';

describe('RankingHeader', () => {
  it('renders title "인기 랭킹"', () => {
    render(<RankingHeader />);
    
    expect(screen.getByRole('heading', { name: '인기 랭킹' })).toBeInTheDocument();
  });

  it('renders subtitle', () => {
    render(<RankingHeader />);
    
    expect(screen.getByText('독자들이 사랑하는 작품')).toBeInTheDocument();
  });
});
