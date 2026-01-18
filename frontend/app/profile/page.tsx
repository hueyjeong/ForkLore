import { UserProfile } from '@/components/feature/users/user-profile';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My Profile | ForkLore',
  description: 'Manage your profile and settings',
};

export default function ProfilePage() {
  return (
    <div className="container py-10 max-w-4xl mx-auto">
      <UserProfile />
    </div>
  );
}
