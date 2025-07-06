import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

export default function Portfolio() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Portfolio</h1>
        <p className="text-muted-foreground">
          View and manage your trading positions
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Overview</CardTitle>
          <CardDescription>
            Current positions and portfolio performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p>Portfolio management features coming soon...</p>
        </CardContent>
      </Card>
    </div>
  );
}

