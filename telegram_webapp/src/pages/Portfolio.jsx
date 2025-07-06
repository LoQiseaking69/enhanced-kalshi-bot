import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Clock,
  MoreVertical
} from 'lucide-react';

// Mock data
const positions = [
  {
    id: 1,
    market: 'Biden Approval > 45%',
    side: 'YES',
    quantity: 100,
    avgPrice: 0.42,
    currentPrice: 0.48,
    pnl: 600,
    pnlPercent: 14.3,
    timeHeld: '2 days'
  },
  {
    id: 2,
    market: 'Fed Rate Cut Dec 2025',
    side: 'NO',
    quantity: 75,
    avgPrice: 0.78,
    currentPrice: 0.72,
    pnl: 450,
    pnlPercent: 7.7,
    timeHeld: '1 day'
  },
  {
    id: 3,
    market: 'Tesla Stock > $300',
    side: 'YES',
    quantity: 120,
    avgPrice: 0.65,
    currentPrice: 0.58,
    pnl: -840,
    pnlPercent: -10.8,
    timeHeld: '3 hours'
  }
];

const closedTrades = [
  {
    id: 1,
    market: 'Inflation < 3% Q4',
    side: 'YES',
    quantity: 90,
    entryPrice: 0.55,
    exitPrice: 0.62,
    pnl: 630,
    pnlPercent: 12.7,
    closedAt: '2 hours ago'
  },
  {
    id: 2,
    market: 'Oil Price > $80',
    side: 'NO',
    quantity: 60,
    entryPrice: 0.45,
    exitPrice: 0.38,
    pnl: 420,
    pnlPercent: 15.6,
    closedAt: '1 day ago'
  }
];

export default function Portfolio() {
  const [portfolioStats] = useState({
    totalValue: 12450,
    totalPnL: 1680,
    dailyPnL: 520,
    openPositions: 3,
    winRate: 78.5
  });

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Portfolio</h1>
        <p className="text-sm text-muted-foreground">
          Your trading positions and performance
        </p>
      </div>

      {/* Portfolio Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <DollarSign className="h-5 w-5" />
            <span>Portfolio Summary</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Total Value</p>
              <p className="text-xl font-bold">${portfolioStats.totalValue.toLocaleString()}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Total P&L</p>
              <p className="text-xl font-bold text-green-500">+${portfolioStats.totalPnL}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Daily P&L</p>
              <p className="text-lg font-semibold text-green-500">+${portfolioStats.dailyPnL}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Win Rate</p>
              <p className="text-lg font-semibold">{portfolioStats.winRate}%</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Positions Tabs */}
      <Tabs defaultValue="open" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="open">Open Positions ({positions.length})</TabsTrigger>
          <TabsTrigger value="closed">Closed Trades</TabsTrigger>
        </TabsList>

        <TabsContent value="open" className="space-y-3 mt-4">
          {positions.map((position) => (
            <Card key={position.id}>
              <CardContent className="p-4">
                <div className="space-y-3">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-sm leading-tight">{position.market}</h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge variant={position.side === 'YES' ? 'default' : 'secondary'} className="text-xs">
                          {position.side}
                        </Badge>
                        <span className="text-xs text-muted-foreground">{position.quantity} shares</span>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Prices */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Avg Price</p>
                      <p className="font-medium">${position.avgPrice.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Current</p>
                      <p className="font-medium">${position.currentPrice.toFixed(2)}</p>
                    </div>
                  </div>

                  {/* P&L */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {position.pnl > 0 ? (
                        <TrendingUp className="h-4 w-4 text-green-500" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-500" />
                      )}
                      <span className={`font-semibold ${position.pnl > 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {position.pnl > 0 ? '+' : ''}${position.pnl}
                      </span>
                      <span className={`text-sm ${position.pnl > 0 ? 'text-green-500' : 'text-red-500'}`}>
                        ({position.pnlPercent > 0 ? '+' : ''}{position.pnlPercent}%)
                      </span>
                    </div>
                    <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>{position.timeHeld}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="closed" className="space-y-3 mt-4">
          {closedTrades.map((trade) => (
            <Card key={trade.id}>
              <CardContent className="p-4">
                <div className="space-y-3">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-sm leading-tight">{trade.market}</h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge variant={trade.side === 'YES' ? 'default' : 'secondary'} className="text-xs">
                          {trade.side}
                        </Badge>
                        <span className="text-xs text-muted-foreground">{trade.quantity} shares</span>
                      </div>
                    </div>
                  </div>

                  {/* Prices */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Entry</p>
                      <p className="font-medium">${trade.entryPrice.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Exit</p>
                      <p className="font-medium">${trade.exitPrice.toFixed(2)}</p>
                    </div>
                  </div>

                  {/* P&L */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-green-500" />
                      <span className="font-semibold text-green-500">
                        +${trade.pnl}
                      </span>
                      <span className="text-sm text-green-500">
                        (+{trade.pnlPercent}%)
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground">{trade.closedAt}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-3">
        <Button variant="outline" className="h-12">
          Close All Positions
        </Button>
        <Button className="h-12">
          New Position
        </Button>
      </div>
    </div>
  );
}

