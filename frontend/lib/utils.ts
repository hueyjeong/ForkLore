import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function parseViews(views: string | number): number {
  if (typeof views === 'number') return views;
  const num = parseFloat(views);
  if (views.includes('M')) return num * 1000000;
  if (views.includes('K')) return num * 1000;
  return num;
}
