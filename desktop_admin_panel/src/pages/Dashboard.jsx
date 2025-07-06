import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  Users,
  Target,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react';

// Mock data for charts
const performanceData = [
  { date: '2025-06-25', pnl: 150, trades: 12, winRate: 75 },
  { date: '2025-06-26', pnl: 280, trades: 15, winRate: 80 },
  { date: '2025-06-27', pnl: -120, trades: 8, winRate: 62 },
  { date: '2025-06-28', pnl: 420, trades: 18, winRate: 83 },
  { date: '2025-06-29', pnl: 350, trades: 14, winRate: 78 },
  { date: '2025-06-30', pnl: 180, trades: 11, winRate: 72 },
  { date: '2025-07-01', pnl: 520, trades: 22, winRate: 86 },
];

const strategyPerformance = [
  { name: 'Sentiment Analysis', value: 65, color: '#8884d8' },
  { name: 'Statistical Arbitrage', value: 35, color: '#82ca9d' },
];

const recentTrades = [
  { id: 1, market: 'Biden Approval > 45%', action: 'BUY', price: 0.42, quantity: 100, pnl: 58, time: '10:30 AM' },
  { id: 2, market: 'Fed Rate Cut Dec 2025', action: 'SELL', price: 0.78, quantity: 75, pnl: -23, time: '10:15 AM' },
  { id: 3, market: 'Tesla Stock > $300', action: 'BUY', price: 0.65, quantity: 120, pnl: 89, time: '09:45 AM' },
  { id: 4, market: 'Inflation < 3% Q4', action: 'SELL', price: 0.55, quantity: 90, pnl: 34, time: '09:20 AM' },
];

const riskMetrics = [
  { name: 'Portfolio Exposure', value: 68, max: 80, status: 'good' },
  { name: 'Max Position Size', value: 12, max: 15, status: 'good' },
  { name: 'Correlation Risk', value: 45, max: 70, status: 'good' },
  { name: 'VaR (95%)', value: 3.2, max: 5.0, status: 'good' },
];

export default function Dashboard({ botStatus }) {
  const [stats, setStats] = useState({
    totalPnL: 1680,
    dailyPnL: 520,
    totalTrades: 156,
    winRate: 78.5,
    activePositions: 8,
    availableBalance: 8320
  });

  const [alerts, setAlerts] = useState([
    { id: 1, type: 'warning', message: 'High correlation detected between 3 positions', time: '5 min ago' },
    { id: 2, type: 'info', message: 'New market opportunity identified: Election 2024', time: '12 min ago' },
    { id: 3, type: 'success', message: 'Strategy "Sentiment Analysis" achieved 85% win rate today', time: '1 hour ago' },
  ]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here's what's happening with your trading bot.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={botStatus.isRunning ? "default" : "destructive"}>
            {botStatus.isRunning ? "Active" : "Inactive"}
          </Badge>
          <Button variant="outline" size="sm">
            <Activity className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total P&L</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">+${stats.totalPnL}</div>
            <p className="text-xs text-muted-foreground">
              +12.5% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily P&L</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">+${stats.dailyPnL}</div>
            <p className="text-xs text-muted-foreground">
              +8.2% from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.winRate}%</div>
            <p className="text-xs text-muted-foreground">
              +2.1% from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Positions</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activePositions}</div>
            <p className="text-xs text-muted-foreground">
              2 new positions today
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Analytics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Performance Overview</CardTitle>
            <CardDescription>
              Daily P&L and trading activity over the last 7 days
            </CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <Tabs defaultValue="pnl" className="w-full">
              <TabsList>
                <TabsTrigger value="pnl">P&L</TabsTrigger>
                <TabsTrigger value="trades">Trades</TabsTrigger>
                <TabsTrigger value="winrate">Win Rate</TabsTrigger>
              </TabsList>
              <TabsContent value="pnl" className="space-y-4">
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="pnl" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </TabsContent>
              <TabsContent value="trades" className="space-y-4">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="trades" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </TabsContent>
              <TabsContent value="winrate" className="space-y-4">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="winRate" stroke="#ffc658" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Strategy Allocation</CardTitle>
            <CardDescription>
              Current allocation across trading strategies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={strategyPerformance}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {strategyPerformance.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2 mt-4">
              {strategyPerformance.map((strategy, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: strategy.color }}
                    />
                    <span className="text-sm">{strategy.name}</span>
                  </div>
                  <span className="text-sm font-medium">{strategy.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity and Risk Metrics */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Trades</CardTitle>
            <CardDescription>
              Latest trading activity from your bot
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentTrades.map((trade) => (
                <div key={trade.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{trade.market}</p>
                    <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                      <Badge variant={trade.action === 'BUY' ? 'default' : 'secondary'} className="text-xs">
                        {trade.action}
                      </Badge>
                      <span>{trade.quantity} @ ${trade.price}</span>
                      <span>{trade.time}</span>
                    </div>
                  </div>
                  <div className={`text-sm font-medium ${trade.pnl > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {trade.pnl > 0 ? '+' : ''}${trade.pnl}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Risk Metrics</CardTitle>
            <CardDescription>
              Current portfolio risk assessment
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {riskMetrics.map((metric, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{metric.name}</span>
                    <span className="text-sm text-muted-foreground">
                      {metric.value}{typeof metric.value === 'number' && metric.value < 10 ? '%' : ''}
                    </span>
                  </div>
                  <Progress 
                    value={(metric.value / metric.max) * 100} 
                    className="h-2"
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alerts */}
      <Card>
        <CardHeader>
          <CardTitle>System Alerts</CardTitle>
          <CardDescription>
            Important notifications and system updates
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div key={alert.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                <div className="mt-0.5">
                  {alert.type === 'warning' && <AlertTriangle className="h-4 w-4 text-yellow-500" />}
                  {alert.type === 'info' && <Clock className="h-4 w-4 text-blue-500" />}
                  {alert.type === 'success' && <CheckCircle className="h-4 w-4 text-green-500" />}
                </div>
                <div className="flex-1 space-y-1">
                  <p className="text-sm">{alert.message}</p>
                  <p className="text-xs text-muted-foreground">{alert.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

