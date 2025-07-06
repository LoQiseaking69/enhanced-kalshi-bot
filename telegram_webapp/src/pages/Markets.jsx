import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Search,
  TrendingUp,
  TrendingDown,
  Clock,
  Users,
  DollarSign,
  Filter
} from 'lucide-react';

// Mock market data
const trendingMarkets = [
  {
    id: 1,
    title: 'Biden Approval Rating > 45%',
    category: 'Politics',
    yesPrice: 0.48,
    noPrice: 0.52,
    volume: 125000,
    change24h: 5.2,
    timeLeft: '15 days'
  },
  {
    id: 2,
    title: 'Fed Rate Cut in December 2025',
    category: 'Economics',
    yesPrice: 0.72,
    noPrice: 0.28,
    volume: 89000,
    change24h: -2.1,
    timeLeft: '8 months'
  },
  {
    id: 3,
    title: 'Tesla Stock > $300 by EOY',
    category: 'Stocks',
    yesPrice: 0.58,
    noPrice: 0.42,
    volume: 156000,
    change24h: 8.7,
    timeLeft: '6 months'
  }
];

const newMarkets = [
  {
    id: 4,
    title: 'AI Breakthrough Announced in 2025',
    category: 'Technology',
    yesPrice: 0.35,
    noPrice: 0.65,
    volume: 45000,
    change24h: 0,
    timeLeft: '11 months'
  },
  {
    id: 5,
    title: 'Inflation Below 3% in Q4 2025',
    category: 'Economics',
    yesPrice: 0.62,
    noPrice: 0.38,
    volume: 78000,
    change24h: 1.8,
    timeLeft: '9 months'
  }
];

const categories = ['All', 'Politics', 'Economics', 'Stocks', 'Technology', 'Sports'];

export default function Markets() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const MarketCard = ({ market }) => (
    <Card>
      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Header */}
          <div className="space-y-2">
            <div className="flex items-start justify-between">
              <h3 className="font-medium text-sm leading-tight flex-1">{market.title}</h3>
              <Badge variant="outline" className="text-xs ml-2">
                {market.category}
              </Badge>
            </div>
            <div className="flex items-center space-x-4 text-xs text-muted-foreground">
              <div className="flex items-center space-x-1">
                <DollarSign className="h-3 w-3" />
                <span>${market.volume.toLocaleString()}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Clock className="h-3 w-3" />
                <span>{market.timeLeft}</span>
              </div>
            </div>
          </div>

          {/* Prices */}
          <div className="grid grid-cols-2 gap-2">
            <Button variant="outline" className="h-12 flex-col space-y-1 p-2">
              <span className="text-xs text-muted-foreground">YES</span>
              <span className="font-semibold">${market.yesPrice.toFixed(2)}</span>
            </Button>
            <Button variant="outline" className="h-12 flex-col space-y-1 p-2">
              <span className="text-xs text-muted-foreground">NO</span>
              <span className="font-semibold">${market.noPrice.toFixed(2)}</span>
            </Button>
          </div>

          {/* 24h Change */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1">
              {market.change24h > 0 ? (
                <TrendingUp className="h-3 w-3 text-green-500" />
              ) : market.change24h < 0 ? (
                <TrendingDown className="h-3 w-3 text-red-500" />
              ) : null}
              <span className={`text-xs font-medium ${
                market.change24h > 0 ? 'text-green-500' : 
                market.change24h < 0 ? 'text-red-500' : 
                'text-muted-foreground'
              }`}>
                {market.change24h > 0 ? '+' : ''}{market.change24h}% 24h
              </span>
            </div>
            <Button size="sm" className="h-8">
              Trade
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Markets</h1>
        <p className="text-sm text-muted-foreground">
          Discover and trade prediction markets
        </p>
      </div>

      {/* Search and Filter */}
      <div className="space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search markets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Category Filter */}
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category)}
              className="whitespace-nowrap"
            >
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Market Tabs */}
      <Tabs defaultValue="trending" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="trending">Trending</TabsTrigger>
          <TabsTrigger value="new">New</TabsTrigger>
          <TabsTrigger value="ending">Ending Soon</TabsTrigger>
        </TabsList>

        <TabsContent value="trending" className="space-y-3 mt-4">
          {trendingMarkets.map((market) => (
            <MarketCard key={market.id} market={market} />
          ))}
        </TabsContent>

        <TabsContent value="new" className="space-y-3 mt-4">
          {newMarkets.map((market) => (
            <MarketCard key={market.id} market={market} />
          ))}
        </TabsContent>

        <TabsContent value="ending" className="space-y-3 mt-4">
          <div className="text-center py-8 text-muted-foreground">
            <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No markets ending soon</p>
            <p className="text-sm">Check back later for time-sensitive opportunities</p>
          </div>
        </TabsContent>
      </Tabs>

      {/* Quick Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Market Stats</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-1">
              <p className="text-muted-foreground">Active Markets</p>
              <p className="text-xl font-bold">1,247</p>
            </div>
            <div className="space-y-1">
              <p className="text-muted-foreground">24h Volume</p>
              <p className="text-xl font-bold">$2.4M</p>
            </div>
            <div className="space-y-1">
              <p className="text-muted-foreground">Top Category</p>
              <p className="font-semibold">Politics</p>
            </div>
            <div className="space-y-1">
              <p className="text-muted-foreground">Avg Spread</p>
              <p className="font-semibold">2.3%</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

