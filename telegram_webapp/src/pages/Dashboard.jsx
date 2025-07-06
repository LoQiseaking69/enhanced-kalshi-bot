import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  Target,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Zap
} from 'lucide-react';

// Mock data
const performanceData = [
  { date: '25', pnl: 150 },
  { date: '26', pnl: 280 },
  { date: '27', pnl: -120 },
  { date: '28', pnl: 420 },
  { date: '29', pnl: 350 },
  { date: '30', pnl: 180 },
  { date: '01', pnl: 520 },
];

const strategyData = [
  { name: 'Sentiment', value: 65, color: '#3b82f6' },
  { name: 'Arbitrage', value: 35, color: '#10b981' },
];

const recentTrades = [
  { id: 1, market: 'Biden Approval > 45%', action: 'BUY', pnl: 58, time: '10:30' },
  { id: 2, market: 'Fed Rate Cut Dec', action: 'SELL', pnl: -23, time: '10:15' },
  { id: 3, market: 'Tesla > $300', action: 'BUY', pnl: 89, time: '09:45' },
];

export default function Dashboard({ botStatus }) {
  const [stats] = useState({
    totalPnL: 1680,
    dailyPnL: 520,
    winRate: 78.5,
    activePositions: 8
  });

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Trading bot overview
          </p>
        </div>
        <Badge variant={botStatus.isRunning ? "default" : "destructive"} className="flex items-center gap-1">
          <Activity className="h-3 w-3" />
          {botStatus.isRunning ? "Active" : "Inactive"}
        </Badge>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-3">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <DollarSign className="h-4 w-4 text-green-500" />
              <div>
                <p className="text-xs text-muted-foreground">Total P&L</p>
                <p className="text-lg font-bold text-green-500">+${stats.totalPnL}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-blue-500" />
              <div>
                <p className="text-xs text-muted-foreground">Daily P&L</p>
                <p className="text-lg font-bold text-green-500">+${stats.dailyPnL}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Target className="h-4 w-4 text-purple-500" />
              <div>
                <p className="text-xs text-muted-foreground">Win Rate</p>
                <p className="text-lg font-bold">{stats.winRate}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Activity className="h-4 w-4 text-orange-500" />
              <div>
                <p className="text-xs text-muted-foreground">Positions</p>
                <p className="text-lg font-bold">{stats.activePositions}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Chart */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">7-Day Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={performanceData}>
              <XAxis dataKey="date" axisLine={false} tickLine={false} />
              <YAxis hide />
              <Line 
                type="monotone" 
                dataKey="pnl" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Strategy Allocation */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Strategy Mix</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center mb-4">
            <ResponsiveContainer width="100%" height={120}>
              <PieChart>
                <Pie
                  data={strategyData}
                  cx="50%"
                  cy="50%"
                  innerRadius={30}
                  outerRadius={50}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {strategyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2">
            {strategyData.map((strategy, index) => (
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

      {/* Recent Trades */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Recent Trades</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentTrades.map((trade) => (
              <div key={trade.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium truncate">{trade.market}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <Badge variant={trade.action === 'BUY' ? 'default' : 'secondary'} className="text-xs">
                      {trade.action}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{trade.time}</span>
                  </div>
                </div>
                <div className={`text-sm font-medium ${trade.pnl > 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {trade.pnl > 0 ? '+' : ''}${trade.pnl}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-3">
        <Button className="h-12">
          <Zap className="h-4 w-4 mr-2" />
          Quick Trade
        </Button>
        <Button variant="outline" className="h-12">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh Data
        </Button>
      </div>
    </div>
  );
}

