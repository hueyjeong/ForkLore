import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { PlanType } from '@/types/subscription.types';
import { Check } from 'lucide-react';
import Link from 'next/link';

interface PricingCardProps {
  planType: PlanType;
  price: string;
  features: string[];
  isCurrentPlan?: boolean;
  onSubscribe?: () => void;
  isLoading?: boolean;
}

/**
 * Render a pricing card for a subscription plan.
 *
 * Displays plan title, description, price per month, feature list, and a footer button
 * that either indicates the current plan or links to the checkout for subscribing.
 *
 * @param planType - The plan identifier (PlanType), controls title, description, and styling
 * @param price - Price label to display (e.g., "$5")
 * @param features - Ordered list of feature descriptions to render
 * @param isCurrentPlan - If true, shows a disabled "Current Plan" button instead of a subscribe action
 * @param isLoading - If true, disables the Subscribe button while an action is pending
 * @returns The pricing card element
 */
export function PricingCard({
  planType,
  price,
  features,
  isCurrentPlan,
  isLoading,
}: PricingCardProps) {
  const isPremium = planType === PlanType.PREMIUM;

  return (
    <Card className={`flex flex-col relative ${isPremium ? 'border-primary shadow-lg' : ''}`}>
      {isPremium && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-primary text-primary-foreground text-xs font-bold rounded-full">
          RECOMMENDED
        </div>
      )}
      <CardHeader>
        <CardTitle className="text-2xl">{planType === PlanType.BASIC ? 'Basic' : 'Premium'}</CardTitle>
        <CardDescription>
          {planType === PlanType.BASIC
            ? 'Essential features for casual readers'
            : 'Unlock the full power of ForkLore'}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1">
        <div className="mb-6">
          <span className="text-4xl font-bold">{price}</span>
          <span className="text-muted-foreground">/month</span>
        </div>
        <ul className="space-y-2">
          {features.map((feature, index) => (
            <li key={index} className="flex items-center gap-2">
              <Check className="h-4 w-4 text-primary" />
              <span className="text-sm">{feature}</span>
            </li>
          ))}
        </ul>
      </CardContent>
      <CardFooter>
        {isCurrentPlan ? (
          <Button className="w-full" variant="outline" disabled>
            Current Plan
          </Button>
        ) : (
          <Button className="w-full" asChild variant={isPremium ? 'default' : 'outline'} disabled={isLoading} data-testid={`subscribe-${planType.toLowerCase()}`}>
            <Link href={`/subscriptions/checkout?plan=${planType}`}>
              Subscribe
            </Link>
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}