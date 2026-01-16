'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';
import { GitCommit, GitBranch, GitMerge, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BranchNode {
  id: string;
  label: string;
  type: 'start' | 'choice' | 'ending' | 'current';
  status: 'visited' | 'unvisited' | 'locked';
  depth: number;
}

// Mock Tree Data
const BRANCH_NODES: BranchNode[] = [
  { id: '1', label: 'Prologue: The Awakening', type: 'start', status: 'visited', depth: 0 },
  { id: '2', label: 'Ch 1: Midnight Run', type: 'choice', status: 'visited', depth: 1 },
  { id: '3a', label: 'Left: Trust Kael', type: 'choice', status: 'visited', depth: 2 },
  { id: '3b', label: 'Right: Blend In', type: 'choice', status: 'unvisited', depth: 2 },
  { id: '4a', label: 'Ch 2: The Alleyway', type: 'current', status: 'visited', depth: 3 },
  { id: '4b', label: 'Ch 2: Main Street Chase', type: 'choice', status: 'locked', depth: 3 },
];

export function BranchingVisualizer() {
  return (
    <div className="w-full space-y-4 py-8">
      <div className="flex items-center justify-between px-4">
        <h2 className="flex items-center text-xl font-bold font-serif">
          <GitBranch className="mr-2 h-5 w-5 text-primary" />
          Story Flow
        </h2>
        <Badge variant="outline">Current Path: The Rebel</Badge>
      </div>

      <ScrollArea className="w-full whitespace-nowrap px-4 pb-4">
        <div className="relative flex min-w-max items-center gap-8 py-8">
          {/* Connector Line */}
          <div className="absolute left-0 right-0 top-1/2 h-0.5 -translate-y-1/2 bg-muted" />

          {BRANCH_NODES.map((node, index) => (
            <div key={node.id} className="relative z-10 flex flex-col items-center">
              {/* Node Circle */}
              <div 
                className={cn(
                  "flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all",
                  node.status === 'visited' ? "border-primary bg-primary text-primary-foreground" :
                  node.status === 'locked' ? "border-muted bg-muted text-muted-foreground" :
                  "border-primary bg-background text-primary"
                )}
              >
                {node.type === 'start' ? <GitCommit className="h-4 w-4" /> :
                 node.type === 'ending' ? <CheckCircle2 className="h-4 w-4" /> :
                 node.type === 'current' ? <div className="h-2.5 w-2.5 rounded-full bg-white animate-pulse" /> :
                 <GitMerge className="h-4 w-4" />}
              </div>

              {/* Label Card */}
              <Card 
                className={cn(
                  "mt-4 w-32 border p-2 text-center text-xs transition-all hover:scale-105 cursor-pointer",
                  node.type === 'current' ? "border-primary shadow-md" : "border-border",
                  node.status === 'locked' && "opacity-50 grayscale"
                )}
              >
                <p className="font-semibold line-clamp-2">{node.label}</p>
                <span className="mt-1 block text-[10px] text-muted-foreground capitalize">
                  {node.status}
                </span>
              </Card>

              {/* Branch indicator for split nodes */}
              {node.depth === 2 && index === 2 && (
                 <div className="absolute -bottom-16 left-1/2 h-8 w-0.5 -translate-x-1/2 bg-muted-foreground/30 dashed" />
              )}
            </div>
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </div>
  );
}
