'use client';

import { useQuery } from '@tanstack/react-query';
import { getSubscriptionStatus } from '@/lib/api/subscription.api';
import { PricingCard } from '@/components/feature/subscription/pricing-card';
import { PlanType, SubscriptionStatus } from '@/types/subscription.types';
import { Skeleton } from '@/components/ui/skeleton';

export default function SubscriptionsPage() {
  const { data: subscription, isLoading } = useQuery({
    queryKey: ['subscription'],
    queryFn: getSubscriptionStatus,
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="container py-10">
        <h1 className="text-4xl font-bold mb-8 text-center">Choose Your Plan</h1>
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <Skeleton className="h-[400px] w-full" />
          <Skeleton className="h-[400px] w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="container py-10">
      <h1 className="text-4xl font-bold mb-8 text-center">Choose Your Plan</h1>
      <p className="text-center text-muted-foreground mb-12 max-w-2xl mx-auto">
        Unlock the full potential of ForkLore. Create more branches, get AI assistance, and support your favorite authors.
      </p>

      <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        <PricingCard
          planType={PlanType.BASIC}
          price="$4.99"
          features={[
            'Ad-free reading',
            'Create up to 5 forks per month',
            'Support authors',
            'Basic reading stats',
          ]}
          isCurrentPlan={subscription?.plan_type === PlanType.BASIC && subscription?.status === 'ACTIVE'}
        />
        <PricingCard
          planType={PlanType.PREMIUM}
          price="$9.99"
          features={[
            'Everything in Basic',
            'Unlimited forks',
            'AI writing assistant',
            'Early access to new features',
            'Priority support',
          ]}
          isCurrentPlan={subscription?.plan_type === PlanType.PREMIUM && subscription?.status === 'ACTIVE'}
        />
      </div>
      
      {subscription?.status === 'ACTIVE' && (
        <div className="mt-12 text-center">
            <p className="text-muted-foreground">
                You are currently subscribed to the {subscription.plan_type} plan.
                <br />
                Expires on: {new Date(subscription.expires_at).toLocaleDateString()}
            </p>
        </div>
      )}
    </div>
  );
}
