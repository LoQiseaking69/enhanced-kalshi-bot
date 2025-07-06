import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '../lib/utils';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';
import {
  LayoutDashboard,
  Play,
  Pause,
  TrendingUp,
  Shield,
  Briefcase,
  BarChart3,
  Settings,
  FileText,
  ChevronLeft,
  ChevronRight,
  Bot,
  Activity,
  AlertTriangle
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Trading Control', href: '/trading', icon: Play },
  { name: 'Strategies', href: '/strategies', icon: TrendingUp },
  { name: 'Risk Management', href: '/risk', icon: Shield },
  { name: 'Portfolio', href: '/portfolio', icon: Briefcase },
  { name: 'Markets', href: '/markets', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Logs', href: '/logs', icon: FileText },
];

export default function Sidebar({ collapsed, onToggle, botStatus }) {
  const location = useLocation();

  const getStatusColor = () => {
    if (!botStatus.isRunning) return 'bg-red-500';
    if (!botStatus.isTradingEnabled) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusText = () => {
    if (!botStatus.isRunning) return 'Stopped';
    if (!botStatus.isTradingEnabled) return 'Monitoring';
    return 'Trading';
  };

  const getStatusIcon = () => {
    if (!botStatus.isRunning) return AlertTriangle;
    if (!botStatus.isTradingEnabled) return Pause;
    return Activity;
  };

  const StatusIcon = getStatusIcon();

  return (
    <TooltipProvider>
      <div className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-card border-r border-border transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}>
        {/* Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-border">
          {!collapsed && (
            <div className="flex items-center space-x-2">
              <Bot className="h-8 w-8 text-primary" />
              <span className="text-lg font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                Kalshi Bot
              </span>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="h-8 w-8 p-0"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>

        {/* Bot Status */}
        <div className="p-4 border-b border-border">
          {collapsed ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex justify-center">
                  <div className={cn("h-3 w-3 rounded-full", getStatusColor())} />
                </div>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Bot Status: {getStatusText()}</p>
              </TooltipContent>
            </Tooltip>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-muted-foreground">Bot Status</span>
                <Badge variant={botStatus.isRunning ? (botStatus.isTradingEnabled ? "default" : "secondary") : "destructive"}>
                  <StatusIcon className="h-3 w-3 mr-1" />
                  {getStatusText()}
                </Badge>
              </div>
              {botStatus.lastUpdate && (
                <p className="text-xs text-muted-foreground">
                  Last update: {new Date(botStatus.lastUpdate).toLocaleTimeString()}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;

            if (collapsed) {
              return (
                <Tooltip key={item.name}>
                  <TooltipTrigger asChild>
                    <Link to={item.href}>
                      <Button
                        variant={isActive ? "secondary" : "ghost"}
                        size="sm"
                        className="w-full h-10 p-0 justify-center"
                      >
                        <Icon className="h-5 w-5" />
                      </Button>
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right">
                    <p>{item.name}</p>
                  </TooltipContent>
                </Tooltip>
              );
            }

            return (
              <Link key={item.name} to={item.href}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  size="sm"
                  className="w-full justify-start h-10"
                >
                  <Icon className="h-5 w-5 mr-3" />
                  {item.name}
                </Button>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        {!collapsed && (
          <div className="p-4 border-t border-border">
            <div className="text-xs text-muted-foreground space-y-1">
              <p>Enhanced Kalshi Bot v2.0</p>
              <p>© 2025 Trading Systems</p>
            </div>
          </div>
        )}
      </div>
    </TooltipProvider>
  );
}

