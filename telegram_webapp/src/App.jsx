import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './components/theme-provider';
import { Toaster } from './components/ui/sonner';
import BottomNav from './components/BottomNav';

// Import pages
import Dashboard from './pages/Dashboard';
import Trading from './pages/Trading';
import Portfolio from './pages/Portfolio';
import Markets from './pages/Markets';
import Settings from './pages/Settings';

function App() {
  const [botStatus, setBotStatus] = useState({
    isRunning: false,
    isTradingEnabled: false,
    lastUpdate: null
  });

  // Initialize Telegram Web App
  useEffect(() => {
    // Check if running in Telegram
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();
      
      // Set theme based on Telegram theme
      if (tg.colorScheme === 'dark') {
        document.documentElement.classList.add('dark');
      }
      
      // Handle back button
      tg.BackButton.onClick(() => {
        window.history.back();
      });
    }
  }, []);

  return (
    <ThemeProvider defaultTheme="dark" storageKey="kalshi-bot-theme">
      <Router>
        <div className="min-h-screen bg-background text-foreground pb-16">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route 
              path="/dashboard" 
              element={<Dashboard botStatus={botStatus} />} 
            />
            <Route 
              path="/trading" 
              element={<Trading botStatus={botStatus} setBotStatus={setBotStatus} />} 
            />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/markets" element={<Markets />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
          
          <BottomNav />
          <Toaster />
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;

