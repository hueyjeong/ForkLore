'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { purchaseChapter } from '@/lib/api/interactions.api';
import { getWalletBalance } from '@/lib/api/wallet.api';
import { toast } from 'sonner';

interface PurchaseModalProps {
  chapterId: number;
  chapterTitle: string;
  price: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function PurchaseModal({
  chapterId,
  chapterTitle,
  price,
  isOpen,
  onClose,
  onSuccess,
}: PurchaseModalProps) {
  const queryClient = useQueryClient();
  const [isProcessing, setIsProcessing] = useState(false);

  // Fetch wallet balance
  const { data: wallet, isLoading: isBalanceLoading } = useQuery({
    queryKey: ['wallet'],
    queryFn: getWalletBalance,
    enabled: isOpen, // Only fetch when modal is open
  });

  const currentBalance = wallet?.balance ?? 0;
  const remainingBalance = currentBalance - price;
  const hasInsufficientBalance = remainingBalance < 0;

  // Purchase mutation
  const purchaseMutation = useMutation({
    mutationFn: (id: number) => purchaseChapter(id),
    onMutate: () => {
      setIsProcessing(true);
    },
    onSuccess: () => {
      toast.success('구매가 완료되었습니다.');
      // Invalidate wallet query to refresh balance
      queryClient.invalidateQueries({ queryKey: ['wallet'] });
      // Invalidate chapter queries if needed, or rely on page refresh/callback
      onSuccess?.();
      onClose();
    },
    onError: (error) => {
      console.error('Purchase failed:', error);
      toast.error('구매에 실패했습니다. 다시 시도해주세요.');
    },
    onSettled: () => {
      setIsProcessing(false);
    },
  });

  const handlePurchase = () => {
    if (hasInsufficientBalance) return;
    purchaseMutation.mutate(chapterId);
  };

  const formatNumber = (num: number) => num.toLocaleString();

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>회차 구매</DialogTitle>
          <DialogDescription>
            &quot;{chapterTitle}&quot; 구매
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">현재 잔액:</span>
            <span className="font-medium">
              {isBalanceLoading ? '로딩 중...' : `${formatNumber(currentBalance)} 코인`}
            </span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">가격:</span>
            <span className="font-medium">{formatNumber(price)} 코인</span>
          </div>
          
          <div className="border-t pt-4 flex justify-between items-center">
            <span className="text-muted-foreground">구매 후 잔액:</span>
            <span className={`font-medium ${hasInsufficientBalance ? 'text-destructive' : ''}`}>
               {isBalanceLoading 
                 ? '...' 
                 : hasInsufficientBalance 
                   ? '잔액 부족' 
                   : `${formatNumber(remainingBalance)} 코인`}
            </span>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={onClose} disabled={isProcessing}>
            취소
          </Button>
          <Button 
            onClick={handlePurchase} 
            disabled={isProcessing || isBalanceLoading || hasInsufficientBalance}
          >
            {isProcessing ? '처리 중...' : '구매하기'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
