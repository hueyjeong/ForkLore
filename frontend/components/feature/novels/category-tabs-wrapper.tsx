'use client';

import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { useCallback } from 'react';
import { CategoryTabs } from './category-tabs';

export function CategoryTabsWrapper() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const currentCategory = searchParams.get('category') || '전체';

  const handleCategoryChange = useCallback(
    (category: string) => {
      const params = new URLSearchParams(searchParams.toString());
      
      if (category === '전체') {
        params.delete('category');
      } else {
        params.set('category', category);
      }

      const queryString = params.toString();
      router.push(queryString ? `${pathname}?${queryString}` : pathname);
    },
    [router, pathname, searchParams]
  );

  return (
    <CategoryTabs 
      activeCategory={currentCategory} 
      onCategoryChange={handleCategoryChange} 
    />
  );
}
