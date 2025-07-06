import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

export default function Markets() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Markets</h1>
        <p className="text-muted-foreground">
          Browse and analyze available prediction markets
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Market Explorer</CardTitle>
          <CardDescription>
            Discover trading opportunities across all markets
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p>Market analysis features coming soon...</p>
        </CardContent>
      </Card>
    </div>
  );
}

