import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { Slider } from '../components/ui/slider';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Alert, AlertDescription } from '../components/ui/alert';
import { toast } from 'sonner';
import {
  Play,
  Pause,
  Square,
  Settings,
  Zap,
  Shield,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Power,
  Activity
} from 'lucide-react';

export default function TradingControl({ botStatus, setBotStatus }) {
  const [isLoading, setIsLoading] = useState(false);
  const [tradingSettings, setTradingSettings] = useState({
    maxPositionSize: 10,
    riskLevel: 'medium',
    tradingInterval: 300,
    enableSentimentStrategy: true,
    enableArbitrageStrategy: true,
    minConfidence: 0.7,
    maxDailyTrades: 50,
    stopLossEnabled: true,
    stopLossPercentage: 15
  });

  const [emergencySettings, setEmergencySettings] = useState({
    emergencyStopEnabled: false,
    maxDailyLoss: 500,
    maxDrawdown: 20
  });

  const handleStartBot = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      setBotStatus(prev => ({ ...prev, isRunning: true, lastUpdate: new Date().toISOString() }));
      toast.success('Trading bot started successfully');
    } catch (error) {
      toast.error('Failed to start trading bot');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopBot = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      setBotStatus(prev => ({ ...prev, isRunning: false, isTradingEnabled: false, lastUpdate: new Date().toISOString() }));
      toast.success('Trading bot stopped successfully');
    } catch (error) {
      toast.error('Failed to stop trading bot');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleTrading = async () => {
    if (!botStatus.isRunning) {
      toast.error('Bot must be running to enable trading');
      return;
    }

    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
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
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setBotStatus(prev => ({ 
        ...prev, 
        isRunning: false, 
        isTradingEnabled: false, 
        lastUpdate: new Date().toISOString() 
      }));
      toast.error('Emergency stop activated - All trading halted');
    } catch (error) {
      toast.error('Failed to execute emergency stop');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Trading Control</h1>
          <p className="text-muted-foreground">
            Manage your trading bot operations and settings
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={botStatus.isRunning ? "default" : "destructive"}>
            <Activity className="h-3 w-3 mr-1" />
            {botStatus.isRunning ? "Running" : "Stopped"}
          </Badge>
          {botStatus.isTradingEnabled && (
            <Badge variant="default">
              <TrendingUp className="h-3 w-3 mr-1" />
              Trading Active
            </Badge>
          )}
        </div>
      </div>

      {/* Bot Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Power className="h-5 w-5" />
            <span>Bot Control Panel</span>
          </CardTitle>
          <CardDescription>
            Start, stop, and control your trading bot operations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            {/* Main Controls */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-base font-medium">Bot Status</Label>
                <div className="flex items-center space-x-4">
                  <Button
                    onClick={handleStartBot}
                    disabled={botStatus.isRunning || isLoading}
                    className="flex items-center space-x-2"
                  >
                    <Play className="h-4 w-4" />
                    <span>Start Bot</span>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleStopBot}
                    disabled={!botStatus.isRunning || isLoading}
                    className="flex items-center space-x-2"
                  >
                    <Square className="h-4 w-4" />
                    <span>Stop Bot</span>
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label className="text-base font-medium">Trading Control</Label>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={botStatus.isTradingEnabled}
                      onCheckedChange={handleToggleTrading}
                      disabled={!botStatus.isRunning || isLoading}
                    />
                    <Label>Enable Trading</Label>
                  </div>
                  <Badge variant={botStatus.isTradingEnabled ? "default" : "secondary"}>
                    {botStatus.isTradingEnabled ? "Active" : "Monitoring Only"}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Emergency Controls */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-base font-medium text-red-600">Emergency Controls</Label>
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    Emergency stop will immediately halt all trading and close positions
                  </AlertDescription>
                </Alert>
                <Button
                  variant="destructive"
                  onClick={handleEmergencyStop}
                  disabled={isLoading}
                  className="w-full"
                >
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Emergency Stop
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Trading Settings</span>
          </CardTitle>
          <CardDescription>
            Configure trading parameters and risk management
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="general" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="strategies">Strategies</TabsTrigger>
              <TabsTrigger value="risk">Risk Management</TabsTrigger>
              <TabsTrigger value="emergency">Emergency</TabsTrigger>
            </TabsList>

            <TabsContent value="general" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Max Position Size (%)</Label>
                  <Slider
                    value={[tradingSettings.maxPositionSize]}
                    onValueChange={(value) => setTradingSettings(prev => ({ ...prev, maxPositionSize: value[0] }))}
                    max={25}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                  <div className="text-sm text-muted-foreground">
                    Current: {tradingSettings.maxPositionSize}%
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Trading Interval (seconds)</Label>
                  <Input
                    type="number"
                    value={tradingSettings.tradingInterval}
                    onChange={(e) => setTradingSettings(prev => ({ ...prev, tradingInterval: parseInt(e.target.value) }))}
                    min={60}
                    max={3600}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Minimum Confidence</Label>
                  <Slider
                    value={[tradingSettings.minConfidence * 100]}
                    onValueChange={(value) => setTradingSettings(prev => ({ ...prev, minConfidence: value[0] / 100 }))}
                    max={100}
                    min={50}
                    step={5}
                    className="w-full"
                  />
                  <div className="text-sm text-muted-foreground">
                    Current: {(tradingSettings.minConfidence * 100).toFixed(0)}%
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Max Daily Trades</Label>
                  <Input
                    type="number"
                    value={tradingSettings.maxDailyTrades}
                    onChange={(e) => setTradingSettings(prev => ({ ...prev, maxDailyTrades: parseInt(e.target.value) }))}
                    min={1}
                    max={200}
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="strategies" className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-1">
                    <h4 className="font-medium">Sentiment Analysis Strategy</h4>
                    <p className="text-sm text-muted-foreground">
                      Uses advanced NLP to analyze market sentiment from news and social media
                    </p>
                  </div>
                  <Switch
                    checked={tradingSettings.enableSentimentStrategy}
                    onCheckedChange={(checked) => setTradingSettings(prev => ({ ...prev, enableSentimentStrategy: checked }))}
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-1">
                    <h4 className="font-medium">Statistical Arbitrage Strategy</h4>
                    <p className="text-sm text-muted-foreground">
                      Identifies pricing inefficiencies between correlated markets
                    </p>
                  </div>
                  <Switch
                    checked={tradingSettings.enableArbitrageStrategy}
                    onCheckedChange={(checked) => setTradingSettings(prev => ({ ...prev, enableArbitrageStrategy: checked }))}
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="risk" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={tradingSettings.stopLossEnabled}
                      onCheckedChange={(checked) => setTradingSettings(prev => ({ ...prev, stopLossEnabled: checked }))}
                    />
                    <Label>Enable Stop Loss</Label>
                  </div>

                  {tradingSettings.stopLossEnabled && (
                    <div className="space-y-2">
                      <Label>Stop Loss Percentage</Label>
                      <Slider
                        value={[tradingSettings.stopLossPercentage]}
                        onValueChange={(value) => setTradingSettings(prev => ({ ...prev, stopLossPercentage: value[0] }))}
                        max={50}
                        min={5}
                        step={5}
                        className="w-full"
                      />
                      <div className="text-sm text-muted-foreground">
                        Current: {tradingSettings.stopLossPercentage}%
                      </div>
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  <Alert>
                    <Shield className="h-4 w-4" />
                    <AlertDescription>
                      Risk management settings help protect your capital from significant losses
                    </AlertDescription>
                  </Alert>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="emergency" className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={emergencySettings.emergencyStopEnabled}
                    onCheckedChange={(checked) => setEmergencySettings(prev => ({ ...prev, emergencyStopEnabled: checked }))}
                  />
                  <Label>Enable Automatic Emergency Stop</Label>
                </div>

                {emergencySettings.emergencyStopEnabled && (
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Max Daily Loss ($)</Label>
                      <Input
                        type="number"
                        value={emergencySettings.maxDailyLoss}
                        onChange={(e) => setEmergencySettings(prev => ({ ...prev, maxDailyLoss: parseInt(e.target.value) }))}
                        min={100}
                        max={5000}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Max Drawdown (%)</Label>
                      <Input
                        type="number"
                        value={emergencySettings.maxDrawdown}
                        onChange={(e) => setEmergencySettings(prev => ({ ...prev, maxDrawdown: parseInt(e.target.value) }))}
                        min={5}
                        max={50}
                      />
                    </div>
                  </div>
                )}

                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    Emergency settings will automatically stop trading when limits are reached
                  </AlertDescription>
                </Alert>
              </div>
            </TabsContent>
          </Tabs>

          <div className="flex justify-end mt-6">
            <Button onClick={handleSaveSettings} disabled={isLoading}>
              <CheckCircle className="h-4 w-4 mr-2" />
              Save Settings
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

