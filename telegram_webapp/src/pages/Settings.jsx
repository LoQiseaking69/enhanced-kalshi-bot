import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Slider } from '../components/ui/slider';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { toast } from 'sonner';
import {
  Settings as SettingsIcon,
  Bell,
  Shield,
  DollarSign,
  Smartphone,
  User,
  LogOut,
  Info,
  AlertTriangle
} from 'lucide-react';

export default function Settings() {
  const [notifications, setNotifications] = useState({
    trades: true,
    alerts: true,
    dailyReport: false,
    marketUpdates: true
  });

  const [riskSettings, setRiskSettings] = useState({
    maxPositionSize: 10,
    stopLossEnabled: true,
    stopLossPercentage: 15,
    maxDailyTrades: 50
  });

  const [telegramSettings, setTelegramSettings] = useState({
    hapticFeedback: true,
    compactMode: false,
    darkTheme: true
  });

  const handleSaveSettings = () => {
    toast.success('Settings saved successfully');
  };

  const handleLogout = () => {
    toast.success('Logged out successfully');
  };

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Configure your trading preferences
        </p>
      </div>

      {/* Account Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <User className="h-5 w-5" />
            <span>Account</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div>
              <p className="font-medium">Trading Account</p>
              <p className="text-sm text-muted-foreground">Connected to Kalshi</p>
            </div>
            <Badge variant="default">Active</Badge>
          </div>

          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div>
              <p className="font-medium">Balance</p>
              <p className="text-sm text-muted-foreground">Available funds</p>
            </div>
            <p className="font-semibold">$8,320</p>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bell className="h-5 w-5" />
            <span>Notifications</span>
          </CardTitle>
          <CardDescription>
            Choose what notifications you want to receive
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Trade Notifications</Label>
              <p className="text-sm text-muted-foreground">Get notified when trades execute</p>
            </div>
            <Switch
              checked={notifications.trades}
              onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, trades: checked }))}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Price Alerts</Label>
              <p className="text-sm text-muted-foreground">Market price movement alerts</p>
            </div>
            <Switch
              checked={notifications.alerts}
              onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, alerts: checked }))}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Daily Reports</Label>
              <p className="text-sm text-muted-foreground">Daily performance summary</p>
            </div>
            <Switch
              checked={notifications.dailyReport}
              onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, dailyReport: checked }))}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Market Updates</Label>
              <p className="text-sm text-muted-foreground">New market opportunities</p>
            </div>
            <Switch
              checked={notifications.marketUpdates}
              onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, marketUpdates: checked }))}
            />
          </div>
        </CardContent>
      </Card>

      {/* Risk Management */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Risk Management</span>
          </CardTitle>
          <CardDescription>
            Configure trading risk parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Max Position Size (%)</Label>
            <Slider
              value={[riskSettings.maxPositionSize]}
              onValueChange={(value) => setRiskSettings(prev => ({ ...prev, maxPositionSize: value[0] }))}
              max={25}
              min={1}
              step={1}
              className="w-full"
            />
            <div className="text-sm text-muted-foreground">
              Current: {riskSettings.maxPositionSize}% of portfolio
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Stop Loss</Label>
              <p className="text-sm text-muted-foreground">Automatic loss protection</p>
            </div>
            <Switch
              checked={riskSettings.stopLossEnabled}
              onCheckedChange={(checked) => setRiskSettings(prev => ({ ...prev, stopLossEnabled: checked }))}
            />
          </div>

          {riskSettings.stopLossEnabled && (
            <div className="space-y-2">
              <Label>Stop Loss Percentage</Label>
              <Slider
                value={[riskSettings.stopLossPercentage]}
                onValueChange={(value) => setRiskSettings(prev => ({ ...prev, stopLossPercentage: value[0] }))}
                max={50}
                min={5}
                step={5}
                className="w-full"
              />
              <div className="text-sm text-muted-foreground">
                Current: {riskSettings.stopLossPercentage}% maximum loss
              </div>
            </div>
          )}

          <div className="space-y-2">
            <Label>Max Daily Trades</Label>
            <Input
              type="number"
              value={riskSettings.maxDailyTrades}
              onChange={(e) => setRiskSettings(prev => ({ ...prev, maxDailyTrades: parseInt(e.target.value) }))}
              min={1}
              max={200}
            />
          </div>
        </CardContent>
      </Card>

      {/* Telegram Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Smartphone className="h-5 w-5" />
            <span>Telegram Settings</span>
          </CardTitle>
          <CardDescription>
            Customize your Telegram experience
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Haptic Feedback</Label>
              <p className="text-sm text-muted-foreground">Vibration on interactions</p>
            </div>
            <Switch
              checked={telegramSettings.hapticFeedback}
              onCheckedChange={(checked) => setTelegramSettings(prev => ({ ...prev, hapticFeedback: checked }))}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Compact Mode</Label>
              <p className="text-sm text-muted-foreground">Smaller UI elements</p>
            </div>
            <Switch
              checked={telegramSettings.compactMode}
              onCheckedChange={(checked) => setTelegramSettings(prev => ({ ...prev, compactMode: checked }))}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Dark Theme</Label>
              <p className="text-sm text-muted-foreground">Use dark color scheme</p>
            </div>
            <Switch
              checked={telegramSettings.darkTheme}
              onCheckedChange={(checked) => setTelegramSettings(prev => ({ ...prev, darkTheme: checked }))}
            />
          </div>
        </CardContent>
      </Card>

      {/* About */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Info className="h-5 w-5" />
            <span>About</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm">App Version</span>
            <span className="text-sm font-medium">2.0.0</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Bot Version</span>
            <span className="text-sm font-medium">Enhanced v2.0</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Last Updated</span>
            <span className="text-sm font-medium">Today</span>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="space-y-3">
        <Button onClick={handleSaveSettings} className="w-full" size="lg">
          Save Settings
        </Button>
        
        <Button 
          variant="outline" 
          onClick={handleLogout} 
          className="w-full" 
          size="lg"
        >
          <LogOut className="h-4 w-4 mr-2" />
          Logout
        </Button>
      </div>

      {/* Warning */}
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Changes to risk settings will apply to new trades only. Existing positions are not affected.
        </AlertDescription>
      </Alert>
    </div>
  );
}

