import React, { useState } from 'react';
import { Package, MessageSquare, DollarSign, Truck, Tag, Store, Box, Users } from 'lucide-react';

// Import sub-pages
import AdminProductList from './AdminProductList';
import AdminSupport from './AdminSupport';
import AdminRefunds from './AdminRefunds';
import AdminDelivery from './AdminDelivery';
import AdminOffers from './AdminOffers';
import AdminStores from './AdminStores';
import AdminInventory from './AdminInventory';
import AdminHandoff from './AdminHandoff';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('products');

  const tabs = [
    { id: 'products', label: 'Products', icon: Package },
    { id: 'inventory', label: 'Inventory', icon: Box }, 
    { id: 'offers', label: 'Offers', icon: Tag }, 
    { id: 'stores', label: 'Stores', icon: Store }, 
    { id: 'support', label: 'Support', icon: MessageSquare },
    { id: 'refunds', label: 'Refunds', icon: DollarSign },
    { id: 'delivery', label: 'Delivery', icon: Truck },
    { id: 'handoff', label: 'AI Handoffs', icon: Users },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Scrollable Tab Bar */}
      <div className="flex gap-2 overflow-x-auto border-b border-gray-200 pb-2 mb-6 no-scrollbar">
        {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
                <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap
                        ${isActive 
                            ? 'bg-gray-900 text-white shadow-md' 
                            : 'text-gray-500 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                >
                    <Icon size={16} />
                    {tab.label}
                </button>
            )
        })}
      </div>

      {/* Render Content */}
      <div className="flex-1 animate-in fade-in duration-300">
        {activeTab === 'products' && <AdminProductList />}
        {activeTab === 'inventory' && <AdminInventory />}
        {activeTab === 'offers' && <AdminOffers />}
        {activeTab === 'stores' && <AdminStores />}
        {activeTab === 'support' && <AdminSupport />}
        {activeTab === 'refunds' && <AdminRefunds />}
        {activeTab === 'delivery' && <AdminDelivery />}
        {activeTab === 'handoff' && <AdminHandoff />}
      </div>
    </div>
  );
}