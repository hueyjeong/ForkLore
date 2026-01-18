import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatsRow } from './stats-row';

describe('StatsRow', () => {
  it('renders all stats with icons and titles', () => {
    render(
      <StatsRow views={100} episodeCount={10} recommendCount={5} />
    );

    expect(screen.getByText('100')).toBeDefined();
    expect(screen.getByText('10')).toBeDefined();
    expect(screen.getByText('5')).toBeDefined();
    
    expect(screen.getByTitle('조회수')).toBeDefined();
    expect(screen.getByTitle('회차수')).toBeDefined();
    expect(screen.getByTitle('추천수')).toBeDefined();
  });

  it('formats numbers correctly (K)', () => {
    render(
      <StatsRow views={42500} episodeCount={100} recommendCount={1000} />
    );

    expect(screen.getByText('42.5K')).toBeDefined();
    expect(screen.getByText('1K')).toBeDefined();
  });

  it('formats numbers correctly (M)', () => {
    render(
      <StatsRow views={1520000} episodeCount={100} recommendCount={1000000} />
    );

    expect(screen.getByText('1.52M')).toBeDefined();
    expect(screen.getByText('1M')).toBeDefined();
  });

  it('renders correctly with 0 values', () => {
    render(
      <StatsRow views={0} episodeCount={0} recommendCount={0} />
    );

    const zeros = screen.getAllByText('0');
    expect(zeros.length).toBeGreaterThanOrEqual(3);
  });
});
