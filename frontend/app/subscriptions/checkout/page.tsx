'use client';

import { Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { subscribe } from '@/lib/api/subscription.api';
import { PlanType } from '@/types/subscription.types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';

function CheckoutContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const plan = searchParams.get('plan') as PlanType;
  
  // Validation
  const isValidPlan = Object.values(PlanType).includes(plan);
  
  const { mutate, isPending } = useMutation({
    mutationFn: subscribe,
    onSuccess: () => {
      toast.success('Subscription successful!');
      router.push('/subscriptions');
    },
    onError: (error) => {
      toast.error('Subscription failed. Please try again.');
      console.error(error);
    }
  });

  const handleSubscribe = () => {
    mutate({ plan_type: plan });
  };

  if (!isValidPlan) {
      return (
          <div className="container py-10 text-center">
              <h1 className="text-2xl font-bold mb-4">Invalid Plan</h1>
              <Button onClick={() => router.push('/subscriptions')}>Go Back</Button>
          </div>
      );
  }

  const isPremium = plan === PlanType.PREMIUM;
  const price = isPremium ? '$9.99' : '$4.99';

  return (
    <div className="container py-10 max-w-md mx-auto">
        <Card>
            <CardHeader>
                <CardTitle>Checkout</CardTitle>
                <CardDescription>You are subscribing to the {plan} plan.</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="flex justify-between items-center text-lg font-bold mb-4">
                    <span>Total</span>
                    <span>{price}/month</span>
                </div>
                <div className="text-sm text-muted-foreground">
                    <p>Features included:</p>
                    <ul className="list-disc list-inside mt-2">
                        {isPremium ? (
                            <>
                                <li>Unlimited forks</li>
                                <li>AI writing assistant</li>
                                <li>Early access</li>
                            </>
                        ) : (
                            <>
                                <li>Ad-free reading</li>
                                <li>5 forks/month</li>
                            </>
                        )}
                    </ul>
                </div>
            </CardContent>
            <CardFooter>
                <Button className="w-full" onClick={handleSubscribe} disabled={isPending}>
                    {isPending ? 'Processing...' : `Pay ${price}`}
                </Button>
            </CardFooter>
        </Card>
    </div>
  );
}

export default function CheckoutPage() {
    return (
        <Suspense fallback={<div>Loading checkout...</div>}>
            <CheckoutContent />
        </Suspense>
    );
}
