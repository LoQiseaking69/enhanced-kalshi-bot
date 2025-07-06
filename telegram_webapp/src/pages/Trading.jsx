import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { toast } from 'sonner';
import {
  Play,
  Pause,
  Square,
  Power,
  Activity,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Shield
} from 'lucide-react';

export default function Trading({ botStatus, setBotStatus }) {
  const [isLoading, setIsLoading] = useState(false);

  const handleStartBot = async () => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      setBotStatus(prev => ({ ...prev, isRunning: true, lastUpdate: new Date().toISOString() }));
      toast.success('Trading bot started');
    } catch (error) {
      toast.error('Failed to start bot');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopBot = async () => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setBotStatus(prev => ({ ...prev, isRunning: false, isTradingEnabled: false, lastUpdate: new Date().toISOString() }));
      toast.success('Trading bot stopped');
    } catch (error) {
      toast.error('Failed to stop bot');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleTrading = async () => {
    if (!botStatus.isRunning) {
      toast.error('Bot must be running first');
      return;
    }

    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      setBotStatus(prev => ({ 
        ...prev, 
        isTradingEnabled: !prev.isTradingEnabled, 
        lastUpdate: new Date().toISOString() 
      }));
      toast.success(`Trading ${!botStatus.isTradingEnabled ? 'enabled' : 'disabled'}`);
    } catch (error) {
      toast.error('Failed to toggle trading');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmergencyStop = async () => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setBotStatus(prev => ({ 
        ...prev, 
        isRunning: false, 
        isTradingEnabled: false, 
        lastUpdate: new Date().toISOString() 
      }));
      toast.error('Emergency stop activated');
    } catch (error) {
      toast.error('Failed to execute emergency stop');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Trading Control</h1>
          <p className="text-sm text-muted-foreground">
            Manage bot operations
          </p>
        </div>
        <div className="flex flex-col items-end space-y-1">
          <Badge variant={botStatus.isRunning ? "default" : "destructive"} className="flex items-center gap-1">
            <Activity className="h-3 w-3" />
            {botStatus.isRunning ? "Running" : "Stopped"}
          </Badge>
          {botStatus.isTradingEnabled && (
            <Badge variant="default" className="flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              Trading
            </Badge>
          )}
        </div>
      </div>

      {/* Bot Status Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Power className="h-5 w-5" />
            <span>Bot Status</span>
          </CardTitle>
          <CardDescription>
            Current bot operational status
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <p className="font-medium">Bot Engine</p>
              <p className="text-sm text-muted-foreground">
                {botStatus.isRunning ? "Running and monitoring markets" : "Stopped"}
              </p>
            </div>
            <Badge variant={botStatus.isRunning ? "default" : "secondary"}>
              {botStatus.isRunning ? "Active" : "Inactive"}
            </Badge>
          </div>

          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <p className="font-medium">Trading Mode</p>
              <p className="text-sm text-muted-foreground">
                {botStatus.isTradingEnabled ? "Actively trading" : "Monitoring only"}
              </p>
            </div>
            <Badge variant={botStatus.isTradingEnabled ? "default" : "secondary"}>
              {botStatus.isTradingEnabled ? "Trading" : "Monitoring"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Control Panel</CardTitle>
          <CardDescription>
            Start, stop, and control your trading bot
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Bot Controls */}
          <div className="space-y-3">
            <div className="flex space-x-2">
              <Button
                onClick={handleStartBot}
                disabled={botStatus.isRunning || isLoading}
                className="flex-1"
                size="lg"
              >
                <Play className="h-4 w-4 mr-2" />
                Start Bot
              </Button>
              <Button
                variant="outline"
                onClick={handleStopBot}
                disabled={!botStatus.isRunning || isLoading}
                className="flex-1"
                size="lg"
              >
                <Square className="h-4 w-4 mr-2" />
                Stop Bot
              </Button>
            </div>

            {/* Trading Toggle */}
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="space-y-1">
                <Label className="text-base font-medium">Enable Trading</Label>
                <p className="text-sm text-muted-foreground">
                  Allow bot to execute trades automatically
                </p>
              </div>
              <Switch
                checked={botStatus.isTradingEnabled}
                onCheckedChange={handleToggleTrading}
                disabled={!botStatus.isRunning || isLoading}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Emergency Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-red-600">
            <AlertTriangle className="h-5 w-5" />
            <span>Emergency Controls</span>
          </CardTitle>
          <CardDescription>
            Immediate stop controls for emergency situations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert className="mb-4">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Emergency stop will immediately halt all trading operations
            </AlertDescription>
          </Alert>
          
          <Button
            variant="destructive"
            onClick={handleEmergencyStop}
            disabled={isLoading}
            className="w-full"
            size="lg"
          >
            <AlertTriangle className="h-4 w-4 mr-2" />
            Emergency Stop
          </Button>
        </CardContent>
      </Card>

      {/* Quick Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Quick Settings</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div>
              <p className="font-medium">Sentiment Strategy</p>
              <p className="text-xs text-muted-foreground">AI-powered market analysis</p>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div>
              <p className="font-medium">Risk Management</p>
              <p className="text-xs text-muted-foreground">Automatic position sizing</p>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div>
              <p className="font-medium">Stop Loss</p>
              <p className="text-xs text-muted-foreground">15% maximum loss per trade</p>
            </div>
            <Switch defaultChecked />
          </div>
        </CardContent>
      </Card>

      {/* Status Info */}
      {botStatus.lastUpdate && (
        <div className="text-center text-xs text-muted-foreground">
          Last updated: {new Date(botStatus.lastUpdate).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}

