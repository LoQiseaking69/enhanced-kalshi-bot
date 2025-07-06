import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { Slider } from '../components/ui/slider';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Progress } from '../components/ui/progress';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { toast } from 'sonner';
import {
  TrendingUp,
  Brain,
  BarChart3,
  Settings,
  Play,
  Pause,
  Target,
  DollarSign,
  Activity,
  AlertTriangle,
  CheckCircle,
  Zap
} from 'lucide-react';

// Mock data for strategy performance
const sentimentPerformance = [
  { date: '2025-06-25', pnl: 120, trades: 8, winRate: 75, confidence: 0.82 },
  { date: '2025-06-26', pnl: 180, trades: 12, winRate: 83, confidence: 0.78 },
  { date: '2025-06-27', pnl: -80, trades: 6, winRate: 50, confidence: 0.65 },
  { date: '2025-06-28', pnl: 250, trades: 15, winRate: 87, confidence: 0.85 },
  { date: '2025-06-29', pnl: 190, trades: 11, winRate: 82, confidence: 0.79 },
  { date: '2025-06-30', pnl: 140, trades: 9, winRate: 78, confidence: 0.76 },
  { date: '2025-07-01', pnl: 320, trades: 18, winRate: 89, confidence: 0.88 },
];

const arbitragePerformance = [
  { date: '2025-06-25', pnl: 30, trades: 4, winRate: 100, correlation: 0.85 },
  { date: '2025-06-26', pnl: 100, trades: 3, winRate: 100, correlation: 0.92 },
  { date: '2025-06-27', pnl: -40, trades: 2, winRate: 50, correlation: 0.68 },
  { date: '2025-06-28', pnl: 170, trades: 3, winRate: 100, correlation: 0.89 },
  { date: '2025-06-29', pnl: 160, trades: 3, winRate: 100, correlation: 0.91 },
  { date: '2025-06-30', pnl: 40, trades: 2, winRate: 100, correlation: 0.78 },
  { date: '2025-07-01', pnl: 200, trades: 4, winRate: 100, correlation: 0.94 },
];

export default function Strategies() {
  const [strategies, setStrategies] = useState([
    {
      id: 'sentiment',
      name: 'Advanced Sentiment Analysis',
      description: 'Uses multiple NLP models to analyze market sentiment from news, social media, and financial reports',
      enabled: true,
      allocation: 60,
      performance: {
        totalPnL: 1120,
        winRate: 81.5,
        totalTrades: 79,
        avgConfidence: 0.79,
        sharpeRatio: 1.42
      },
      settings: {
        minConfidence: 0.7,
        sentimentThreshold: 0.6,
        momentumWindow: 6,
        volumeThreshold: 1.5,
        maxCorrelation: 0.8
      }
    },
    {
      id: 'arbitrage',
      name: 'Statistical Arbitrage',
      description: 'Identifies pricing inefficiencies between correlated markets using statistical analysis',
      enabled: true,
      allocation: 40,
      performance: {
        totalPnL: 660,
        winRate: 92.3,
        totalTrades: 26,
        avgCorrelation: 0.86,
        sharpeRatio: 2.18
      },
      settings: {
        minCorrelation: 0.7,
        zscoreThreshold: 2.0,
        lookbackDays: 30,
        minDataPoints: 20,
        maxPositionCorrelation: 0.8
      }
    }
  ]);

  const [selectedStrategy, setSelectedStrategy] = useState('sentiment');

  const handleToggleStrategy = (strategyId) => {
    setStrategies(prev => prev.map(strategy => 
      strategy.id === strategyId 
        ? { ...strategy, enabled: !strategy.enabled }
        : strategy
    ));
    
    const strategy = strategies.find(s => s.id === strategyId);
    toast.success(`${strategy.name} ${strategy.enabled ? 'disabled' : 'enabled'}`);
  };

  const handleAllocationChange = (strategyId, newAllocation) => {
    setStrategies(prev => {
      const otherStrategy = prev.find(s => s.id !== strategyId);
      const remainingAllocation = 100 - newAllocation;
      
      return prev.map(strategy => 
        strategy.id === strategyId 
          ? { ...strategy, allocation: newAllocation }
          : { ...strategy, allocation: remainingAllocation }
      );
    });
  };

  const handleSettingChange = (strategyId, setting, value) => {
    setStrategies(prev => prev.map(strategy => 
      strategy.id === strategyId 
        ? { 
            ...strategy, 
            settings: { ...strategy.settings, [setting]: value }
          }
        : strategy
    ));
  };

  const saveSettings = () => {
    toast.success('Strategy settings saved successfully');
  };

  const currentStrategy = strategies.find(s => s.id === selectedStrategy);
  const performanceData = selectedStrategy === 'sentiment' ? sentimentPerformance : arbitragePerformance;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Trading Strategies</h1>
          <p className="text-muted-foreground">
            Configure and monitor your automated trading strategies
          </p>
        </div>
        <Button onClick={saveSettings}>
          <CheckCircle className="h-4 w-4 mr-2" />
          Save All Settings
        </Button>
      </div>

      {/* Strategy Overview */}
      <div className="grid gap-4 md:grid-cols-2">
        {strategies.map((strategy) => (
          <Card key={strategy.id} className={strategy.enabled ? 'border-primary' : 'border-muted'}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {strategy.id === 'sentiment' ? (
                    <Brain className="h-5 w-5 text-primary" />
                  ) : (
                    <BarChart3 className="h-5 w-5 text-primary" />
                  )}
                  <CardTitle className="text-lg">{strategy.name}</CardTitle>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={strategy.enabled ? "default" : "secondary"}>
                    {strategy.enabled ? "Active" : "Inactive"}
                  </Badge>
                  <Switch
                    checked={strategy.enabled}
                    onCheckedChange={() => handleToggleStrategy(strategy.id)}
                  />
                </div>
              </div>
              <CardDescription>{strategy.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Allocation */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Allocation</Label>
                    <span className="text-sm font-medium">{strategy.allocation}%</span>
                  </div>
                  <Slider
                    value={[strategy.allocation]}
                    onValueChange={(value) => handleAllocationChange(strategy.id, value[0])}
                    max={100}
                    min={0}
                    step={5}
                    disabled={!strategy.enabled}
                    className="w-full"
                  />
                </div>

                {/* Performance Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Total P&L</p>
                    <p className="text-lg font-bold text-green-600">+${strategy.performance.totalPnL}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Win Rate</p>
                    <p className="text-lg font-bold">{strategy.performance.winRate}%</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Total Trades</p>
                    <p className="text-lg font-bold">{strategy.performance.totalTrades}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
                    <p className="text-lg font-bold">{strategy.performance.sharpeRatio}</p>
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedStrategy(strategy.id)}
                  className="w-full"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Configure Strategy
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detailed Strategy Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            {selectedStrategy === 'sentiment' ? (
              <Brain className="h-5 w-5" />
            ) : (
              <BarChart3 className="h-5 w-5" />
            )}
            <span>{currentStrategy?.name} - Detailed Configuration</span>
          </CardTitle>
          <CardDescription>
            Fine-tune parameters and monitor performance for this strategy
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="performance" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="performance">Performance</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
              <TabsTrigger value="signals">Recent Signals</TabsTrigger>
            </TabsList>

            <TabsContent value="performance" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <DollarSign className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm text-muted-foreground">Total P&L</p>
                        <p className="text-xl font-bold text-green-600">+${currentStrategy?.performance.totalPnL}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <Target className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm text-muted-foreground">Win Rate</p>
                        <p className="text-xl font-bold">{currentStrategy?.performance.winRate}%</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <Activity className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm text-muted-foreground">Total Trades</p>
                        <p className="text-xl font-bold">{currentStrategy?.performance.totalTrades}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
                        <p className="text-xl font-bold">{currentStrategy?.performance.sharpeRatio}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Daily P&L</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={performanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="pnl" fill="#8884d8" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Win Rate Trend</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <LineChart data={performanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="winRate" stroke="#82ca9d" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="settings" className="space-y-4">
              {selectedStrategy === 'sentiment' ? (
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>Minimum Confidence Threshold</Label>
                      <Slider
                        value={[currentStrategy?.settings.minConfidence * 100]}
                        onValueChange={(value) => handleSettingChange('sentiment', 'minConfidence', value[0] / 100)}
                        max={100}
                        min={50}
                        step={5}
                        className="w-full"
                      />
                      <div className="text-sm text-muted-foreground">
                        Current: {(currentStrategy?.settings.minConfidence * 100).toFixed(0)}%
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Sentiment Threshold</Label>
                      <Slider
                        value={[currentStrategy?.settings.sentimentThreshold * 100]}
                        onValueChange={(value) => handleSettingChange('sentiment', 'sentimentThreshold', value[0] / 100)}
                        max={100}
                        min={50}
                        step={5}
                        className="w-full"
                      />
                      <div className="text-sm text-muted-foreground">
                        Current: {(currentStrategy?.settings.sentimentThreshold * 100).toFixed(0)}%
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Momentum Window (hours)</Label>
                      <Input
                        type="number"
                        value={currentStrategy?.settings.momentumWindow}
                        onChange={(e) => handleSettingChange('sentiment', 'momentumWindow', parseInt(e.target.value))}
                        min={1}
                        max={24}
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>Volume Threshold Multiplier</Label>
                      <Slider
                        value={[currentStrategy?.settings.volumeThreshold * 10]}
                        onValueChange={(value) => handleSettingChange('sentiment', 'volumeThreshold', value[0] / 10)}
                        max={30}
                        min={10}
                        step={1}
                        className="w-full"
                      />
                      <div className="text-sm text-muted-foreground">
                        Current: {currentStrategy?.settings.volumeThreshold.toFixed(1)}x
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Max Position Correlation</Label>
                      <Slider
                        value={[currentStrategy?.settings.maxCorrelation * 100]}
                        onValueChange={(value) => handleSettingChange('sentiment', 'maxCorrelation', value[0] / 100)}
                        max={100}
                        min={50}
                        step={5}
                        className="w-full"
                      />
                      <div className="text-sm text-muted-foreground">
                        Current: {(currentStrategy?.settings.maxCorrelation * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>Minimum Correlation</Label>
                      <Slider
                        value={[currentStrategy?.settings.minCorrelation * 100]}
                        onValueChange={(value) => handleSettingChange('arbitrage', 'minCorrelation', value[0] / 100)}
                        max={100}
                        min={50}
                        step={5}
                        className="w-full"
                      />
                      <div className="text-sm text-muted-foreground">
                        Current: {(currentStrategy?.settings.minCorrelation * 100).toFixed(0)}%
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Z-Score Entry Threshold</Label>
                      <Slider
                        value={[currentStrategy?.settings.zscoreThreshold * 10]}
                        onValueChange={(value) => handleSettingChange('arbitrage', 'zscoreThreshold', value[0] / 10)}
                        max={40}
                        min={15}
                        step={1}
                        className="w-full"
                      />
                      <div className="text-sm text-muted-foreground">
                        Current: {currentStrategy?.settings.zscoreThreshold.toFixed(1)}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Lookback Days</Label>
                      <Input
                        type="number"
                        value={currentStrategy?.settings.lookbackDays}
                        onChange={(e) => handleSettingChange('arbitrage', 'lookbackDays', parseInt(e.target.value))}
                        min={7}
                        max={90}
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>Minimum Data Points</Label>
                      <Input
                        type="number"
                        value={currentStrategy?.settings.minDataPoints}
                        onChange={(e) => handleSettingChange('arbitrage', 'minDataPoints', parseInt(e.target.value))}
                        min={10}
                        max={100}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Max Position Correlation</Label>
                      <Slider
                        value={[currentStrategy?.settings.maxPositionCorrelation * 100]}
                        onValueChange={(value) => handleSettingChange('arbitrage', 'maxPositionCorrelation', value[0] / 100)}
                        max={100}
                        min={50}
                        step={5}
                        className="w-full"
                      />
                      <div className="text-sm text-muted-foreground">
                        Current: {(currentStrategy?.settings.maxPositionCorrelation * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="signals" className="space-y-4">
              <div className="space-y-4">
                {/* Recent signals would be displayed here */}
                <div className="text-center py-8 text-muted-foreground">
                  <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Recent trading signals will appear here</p>
                  <p className="text-sm">Connect to your trading bot to see live signal data</p>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}

