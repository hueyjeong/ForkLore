'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { chargeWallet } from '@/lib/api/wallet.api';
import { toast } from 'sonner';

interface ChargeModalProps {
  trigger?: React.ReactNode;
  onSuccess?: () => void;
}

const PRESET_AMOUNTS = [100, 500, 1000, 5000];

export function ChargeModal({ trigger, onSuccess }: ChargeModalProps) {
  const [open, setOpen] = useState(false);
  const [amount, setAmount] = useState<string>('100');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleCharge = async () => {
    const value = parseInt(amount);
    if (isNaN(value) || value <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    setIsLoading(true);
    try {
      await chargeWallet({ amount: value, description: 'User top-up' });
      toast.success(`Successfully charged ${value} coins`);
      setOpen(false);
      router.refresh();
      onSuccess?.();
    } catch (error) {
      toast.error('Failed to charge wallet');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || <Button>Charge Wallet</Button>}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Top Up Wallet</DialogTitle>
          <DialogDescription>
            Add coins to your wallet to unlock premium chapters and support authors.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 gap-2">
            {PRESET_AMOUNTS.map((preset) => (
              <Button
                key={preset}
                variant={amount === preset.toString() ? 'default' : 'outline'}
                onClick={() => setAmount(preset.toString())}
                size="sm"
              >
                {preset}
              </Button>
            ))}
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="amount" className="text-right">
              Amount
            </Label>
            <Input
              id="amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="col-span-3"
              min="1"
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" onClick={handleCharge} disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Pay Now'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
