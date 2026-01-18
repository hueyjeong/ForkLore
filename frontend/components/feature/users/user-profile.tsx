'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getMyProfile } from '@/lib/api/auth.api';
import { getWalletBalance } from '@/lib/api/wallet.api';
import { UserResponse } from '@/types/auth.types';
import { Wallet } from '@/types/wallet.types';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Loader2, User, Wallet as WalletIcon, Mail, Shield } from 'lucide-react';
import { toast } from 'sonner';

export function UserProfile() {
  const [profile, setProfile] = useState<UserResponse | null>(null);
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [profileData, walletData] = await Promise.all([
          getMyProfile(),
          getWalletBalance()
        ]);
        setProfile(profileData);
        setWallet(walletData);
      } catch (error) {
        toast.error('Failed to load profile data');
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-60 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!profile) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header Section */}
      <div className="flex flex-col items-center space-y-4 md:flex-row md:space-x-8 md:space-y-0">
        <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring" }}
        >
            <Avatar className="h-32 w-32 border-4 border-background shadow-xl">
            <AvatarImage src={profile.profileImageUrl} alt={profile.nickname} />
            <AvatarFallback className="text-4xl">{profile.nickname[0]}</AvatarFallback>
            </Avatar>
        </motion.div>
        
        <div className="text-center md:text-left space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">{profile.nickname}</h1>
            <div className="flex items-center justify-center md:justify-start gap-2 text-muted-foreground">
                <Mail className="w-4 h-4" />
                <span>{profile.email}</span>
            </div>
            <Badge variant="secondary" className="mt-2">
                <Shield className="w-3 h-3 mr-1" />
                {profile.role}
            </Badge>
        </div>
      </div>

      <Separator className="my-8" />

      {/* Stats / Wallet Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="overflow-hidden border-l-4 border-l-primary">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Wallet Balance</CardTitle>
                <WalletIcon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{wallet?.balance.toLocaleString()} C</div>
                <p className="text-xs text-muted-foreground">Available coins</p>
            </CardContent>
        </Card>
        
        {/* Placeholder for other stats */}
        <Card className="opacity-50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Read Chapters</CardTitle>
                <User className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">-</div>
                <p className="text-xs text-muted-foreground">Coming soon</p>
            </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
