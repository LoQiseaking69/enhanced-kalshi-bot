import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

export default function Settings() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Configure application and trading preferences
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Application Settings</CardTitle>
          <CardDescription>
            Customize your trading bot configuration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p>Settings configuration coming soon...</p>
        </CardContent>
      </Card>
    </div>
  );
}

