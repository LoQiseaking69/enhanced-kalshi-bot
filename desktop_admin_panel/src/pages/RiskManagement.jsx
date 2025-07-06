import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

export default function RiskManagement() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Risk Management</h1>
        <p className="text-muted-foreground">
          Monitor and control portfolio risk metrics
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Risk Management Dashboard</CardTitle>
          <CardDescription>
            Comprehensive risk monitoring and control system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p>Risk management features coming soon...</p>
        </CardContent>
      </Card>
    </div>
  );
}

