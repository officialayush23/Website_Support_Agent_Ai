import React, { useState } from 'react';
import { Package, MessageSquare, DollarSign, Truck, Tag, Store, Box, Users, ListOrdered } from 'lucide-react';

import AdminProductList from './AdminProductList';
import AdminSupport from './AdminSupport';
import AdminRefunds from './AdminRefunds';
import AdminDelivery from './AdminDelivery';
import AdminOffers from './AdminOffers';
import AdminStores from './AdminStores';
import AdminInventory from './AdminInventory';
import AdminHandoff from './AdminHandoff';
import AdminOrders from './AdminOrders';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('products');

  const tabs = [
    { id: 'products', label: 'Products', icon: Package },
    { id: 'inventory', label: 'Inventory', icon: Box }, 
    { id: 'stores', label: 'Stores', icon: Store }, 
    { id: 'orders', label: 'Orders', icon: ListOrdered },
    { id: 'delivery', label: 'Logistics', icon: Truck },
    { id: 'offers', label: 'Offers', icon: Tag }, 
    { id: 'support', label: 'Support', icon: MessageSquare },
    { id: 'handoff', label: 'Handoffs', icon: Users },
    { id: 'refunds', label: 'Refunds', icon: DollarSign },
  ];

  return (
    <div className="flex flex-col h-full space-y-6">
      <div className="flex gap-2 overflow-x-auto border-b border-gray-200 pb-2 no-scrollbar">
        {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
                <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap
                        ${isActive 
                            ? 'bg-black text-white shadow-md' 
                            : 'text-gray-500 hover:bg-gray-100 hover:text-black'
                        }`}
                >
                    <Icon size={16} />
                    {tab.label}
                </button>
            )
        })}
      </div>

      <div className="flex-1 animate-in fade-in duration-300">
        {activeTab === 'products' && <AdminProductList />}
        {activeTab === 'inventory' && <AdminInventory />}
        {activeTab === 'stores' && <AdminStores />}
        {activeTab === 'orders' && <AdminOrders />}
        {activeTab === 'delivery' && <AdminDelivery />}
        {activeTab === 'offers' && <AdminOffers />}
        {activeTab === 'support' && <AdminSupport />}
        {activeTab === 'handoff' && <AdminHandoff />}
        {activeTab === 'refunds' && <AdminRefunds />}
      </div>
    </div>
  );
}