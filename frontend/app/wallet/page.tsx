'use client';

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getWalletBalance, getWalletTransactions } from '@/lib/api/wallet.api';
import { ChargeModal } from '@/components/feature/wallet/charge-modal';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';

export default function WalletPage() {
    const queryClient = useQueryClient();

    const { data: wallet, isLoading: isWalletLoading } = useQuery({
        queryKey: ['wallet'],
        queryFn: getWalletBalance,
    });

    const { data: transactions, isLoading: isTransactionsLoading } = useQuery({
        queryKey: ['wallet-transactions'],
        queryFn: getWalletTransactions,
    });

    const handleChargeSuccess = () => {
        queryClient.invalidateQueries({ queryKey: ['wallet'] });
        queryClient.invalidateQueries({ queryKey: ['wallet-transactions'] });
    };

    if (isWalletLoading) {
        return (
            <div className="container py-10 space-y-6">
                <Skeleton className="h-[200px] w-full" />
                <Skeleton className="h-[400px] w-full" />
            </div>
        );
    }

    return (
        <div className="container py-10 space-y-8">
            <h1 className="text-3xl font-bold">My Wallet</h1>
            
            <div className="grid gap-6 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Current Balance</CardTitle>
                        <CardDescription>Use coins to purchase premium chapters</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="text-4xl font-bold mb-4">{wallet?.balance || 0} Coins</div>
                        <ChargeModal onSuccess={handleChargeSuccess} />
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Spending Summary</CardTitle>
                         <CardDescription>Your recent activity</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-muted-foreground">
                            View your detailed transaction history below.
                        </p>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Transaction History</CardTitle>
                </CardHeader>
                <CardContent>
                    {isTransactionsLoading ? (
                        <div className="space-y-2">
                             <Skeleton className="h-12 w-full" />
                             <Skeleton className="h-12 w-full" />
                             <Skeleton className="h-12 w-full" />
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Date</TableHead>
                                    <TableHead>Type</TableHead>
                                    <TableHead>Description</TableHead>
                                    <TableHead className="text-right">Amount</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {transactions && transactions.length > 0 ? (
                                    transactions.map((tx) => (
                                        <TableRow key={tx.id}>
                                            <TableCell>{new Date(tx.createdAt).toLocaleDateString()}</TableCell>
                                            <TableCell className="capitalize">{tx.transaction_type.toLowerCase()}</TableCell>
                                            <TableCell>{tx.description}</TableCell>
                                            <TableCell className={`text-right font-medium ${tx.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                {tx.amount > 0 ? '+' : ''}{tx.amount}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={4} className="text-center py-4">
                                            No transactions found.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
