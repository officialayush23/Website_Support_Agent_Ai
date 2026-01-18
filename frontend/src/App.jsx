import React from 'react';
import { BrowserRouter as Router, Routes, Route, Outlet, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

// --- Pages ---
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import DemoLayout from './pages/Demo/DemoLayout';
import ProductList from './pages/Demo/ProductList';

import { Toaster } from 'sonner';
import AdminDashboard from './pages/Demo/Admin/AdminDashboard';
import Profile from './pages/Demo/Profile';
import Orders from './pages/Demo/Order';
import Cart from './pages/Demo/Cart';
import Checkout from './pages/Demo/Checkout';
import OrderDetail from './pages/Demo/OrderDetail';
import ChatInterface from './pages/Demo/chat';
import { ThemeProvider } from './context/ThemeContext';

// --- Route Guards ---

const ProtectedRoute = () => {
  const { user, loading } = useAuth();

  if (loading) return <div className="p-10 text-center">Loading...</div>;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

const AdminRoute = () => {
  const { profile, loading } = useAuth();

  if (loading) return <div className="p-10 text-center">Loading...</div>;

  // Check the role from the backend profile
  if (profile?.role !== 'admin') {
    return <Navigate to="/demo" replace />;
  }
  return <Outlet />;
};

// --- Main App Component ---

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
      <Toaster position="top-right" />
      <Router>
        <Routes>
          {/* 1. Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          

          {/* 2. Protected App Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/demo" element={<DemoLayout />}>
              
              {/* Shop Home (Product List) */}
              <Route index element={<ProductList />} />
              <Route path="profile" element={<Profile />} />
              <Route path="orders" element={<Orders />} />
              <Route path="cart" element={<Cart />} />
              <Route path="checkout" element={<Checkout />} />
             
              <Route path="chat" element={<ChatInterface />} />
               <Route path="orders/:orderId" element={<OrderDetail />} />
              
              {/* Product List (explicit path) */}
              <Route path="products" element={<ProductList />} />

              {/* Cart (Placeholder for now) */}
              <Route path="cart" element={<div className="p-10 text-center text-gray-500">Cart Page (Coming Soon)</div>} />

              {/* Orders (Placeholder for now) */}
              <Route path="orders" element={<div className="p-10 text-center text-gray-500">Orders Page (Coming Soon)</div>} />

              {/* Chat (Coming Next) */}
              <Route path="chat" element={<div className="p-10 text-center text-gray-500">Chat Interface (Coming Next)</div>} />

              {/* 3. Admin Protected Routes */}
              <Route element={<AdminRoute />}>
                <Route path="admin" element={<AdminDashboard />} />
              </Route>

            </Route>
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;