import { MyLibrary } from '@/components/feature/users/my-library';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My Library | ForkLore',
  description: 'View your purchased novels and chapters',
};

export default function LibraryPage() {
  return (
    <div className="container py-10 max-w-6xl mx-auto">
      <MyLibrary />
    </div>
  );
}
