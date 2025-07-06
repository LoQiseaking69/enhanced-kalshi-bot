import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './components/theme-provider';
import { Toaster } from './components/ui/sonner';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import TradingControl from './pages/TradingControl';
import Strategies from './pages/Strategies';
import RiskManagement from './pages/RiskManagement';
import Portfolio from './pages/Portfolio';
import Markets from './pages/Markets';
import Settings from './pages/Settings';
import Logs from './pages/Logs';
import './App.css';

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [botStatus, setBotStatus] = useState({
    isRunning: false,
    isTradingEnabled: false,
    lastUpdate: null
  });

  // Simulate API calls for bot status
  useEffect(() => {
    const fetchBotStatus = async () => {
      try {
        // In a real implementation, this would call your backend API
        // For now, we'll simulate the status
        setBotStatus({
          isRunning: Math.random() > 0.3, // 70% chance of running
          isTradingEnabled: Math.random() > 0.5, // 50% chance of trading enabled
          lastUpdate: new Date().toISOString()
        });
      } catch (error) {
        console.error('Failed to fetch bot status:', error);
      }
    };

    fetchBotStatus();
    const interval = setInterval(fetchBotStatus, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <ThemeProvider defaultTheme="dark" storageKey="kalshi-admin-theme">
      <Router>
        <div className="flex h-screen bg-background text-foreground">
          <Sidebar 
            collapsed={sidebarCollapsed} 
            onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
            botStatus={botStatus}
          />
          
          <main className={`flex-1 overflow-hidden transition-all duration-300 ${
            sidebarCollapsed ? 'ml-16' : 'ml-64'
          }`}>
            <div className="h-full overflow-auto">
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard botStatus={botStatus} />} />
                <Route path="/trading" element={<TradingControl botStatus={botStatus} setBotStatus={setBotStatus} />} />
                <Route path="/strategies" element={<Strategies />} />
                <Route path="/risk" element={<RiskManagement />} />
                <Route path="/portfolio" element={<Portfolio />} />
                <Route path="/markets" element={<Markets />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/logs" element={<Logs />} />
              </Routes>
            </div>
          </main>
        </div>
        <Toaster />
      </Router>
    </ThemeProvider>
  );
}

export default App;

