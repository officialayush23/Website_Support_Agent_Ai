import React, { useEffect, useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../lib/api'; // ✅ Added missing import
import {
    ShoppingBag,
    ShoppingCart,
    Package,
    MessageSquare,
    LogOut,
    Menu,
    X,
    LayoutDashboard,
    Search,
    MapPin
} from 'lucide-react';

export default function DemoLayout() {
    const navigate = useNavigate();
    const location = useLocation();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const { user, profile, signOut } = useAuth();
    const [userLocation, setUserLocation] = useState(null);

    const handleSignOut = async () => {
        await signOut();
        navigate('/login');
    };

    // --- Location Sync Logic ---
    useEffect(() => {
        const updateLocation = () => {
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(async (position) => {
                    const { latitude, longitude } = position.coords;
                    setUserLocation({ lat: latitude, lng: longitude });
                    try {
                        // ✅ FIXED: Changed to PATCH as per backend router
                        await apiRequest(`/users/location?lat=${latitude}&lng=${longitude}`, { method: 'PATCH' });
                        console.log("📍 Location synced with backend");
                    } catch (e) {
                        console.error("Location sync failed", e);
                    }
                }, (err) => {
                    console.warn("Geolocation permission denied", err);
                });
            }
        };

        // Sync immediately, then every 5 minutes
        updateLocation();
        const interval = setInterval(updateLocation, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    const isAdmin = profile?.role === 'admin';

    const navItems = [
        { name: 'Shop', path: '/demo', icon: ShoppingBag },
        { name: 'Cart', path: '/demo/cart', icon: ShoppingCart },
        { name: 'Orders', path: '/demo/orders', icon: Package },
        { name: 'Support Chat', path: '/demo/chat', icon: MessageSquare },
    ];

    if (isAdmin) {
        navItems.push({ name: 'Admin Console', path: '/demo/admin', icon: LayoutDashboard });
    }

    return (
        <div className="min-h-screen bg-gray-50 flex font-sans">
            {/* Sidebar */}
            <aside className="hidden md:flex w-64 flex-col bg-white border-r border-gray-200 fixed h-full z-20">
                <div className="h-16 flex items-center px-6 border-b border-gray-100">
                    <span className="text-2xl font-bold text-gray-900 tracking-tight" style={{ fontFamily: '"Charm", cursive' }}>
                        Weeb Store
                    </span>
                </div>

                <nav className="flex-1 p-4 space-y-1">
                    {navItems.map((item) => {
                        const isActive = item.path === '/demo'
                            ? location.pathname === '/demo'
                            : location.pathname.startsWith(item.path);
                        return (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}
                            >
                                <item.icon size={20} />
                                {item.name}
                            </NavLink>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-gray-100">
                    <NavLink to="/demo/profile" className="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer group">
                        <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs">
                            {user?.user_metadata?.full_name?.[0] || user?.email?.[0]?.toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                                {user?.user_metadata?.full_name || 'User'}
                            </p>
                            <p className="text-xs text-gray-500 truncate flex items-center gap-1">
                                {isAdmin ? <span className="text-blue-600 font-bold">Admin</span> : user?.email}
                            </p>
                        </div>
                    </NavLink>
                    <button onClick={handleSignOut} className="mt-2 w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                        <LogOut size={16} /> Sign Out
                    </button>
                </div>
            </aside>

            {/* Mobile Header */}
            <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-30 flex items-center justify-between px-4">
                <span className="text-xl font-bold text-gray-900" style={{ fontFamily: '"Charm", cursive' }}>Weeb</span>
                <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2 text-gray-600">
                    {isMobileMenuOpen ? <X /> : <Menu />}
                </button>
            </div>

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
                <div className="fixed inset-0 z-20 bg-white pt-20 px-4 md:hidden animate-in fade-in slide-in-from-top-10">
                    <nav className="space-y-2">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                onClick={() => setIsMobileMenuOpen(false)}
                                className={({ isActive }) => `flex items-center gap-3 px-4 py-4 rounded-lg text-base font-medium ${isActive ? 'bg-blue-50 text-blue-600' : 'text-gray-600'}`}
                            >
                                <item.icon size={20} />
                                {item.name}
                            </NavLink>
                        ))}
                        <button onClick={handleSignOut} className="w-full flex items-center gap-3 px-4 py-4 text-base font-medium text-red-600 border-t border-gray-100 mt-4">
                            <LogOut size={20} /> Sign Out
                        </button>
                    </nav>
                </div>
            )}

            {/* Content Area */}
            <main className="flex-1 md:ml-64 p-6 pt-20 md:pt-6 max-w-7xl mx-auto w-full transition-all">
                {/* Header Bar */}
                <div className="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center bg-white p-4 rounded-xl border border-gray-200 shadow-sm sticky top-4 z-30 gap-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                        <MapPin size={16} className={userLocation ? "text-green-500 animate-pulse" : "text-gray-400"} />
                        {userLocation ? "Location Synced" : "Locating..."}
                    </div>

                    {/* Global Search Placeholder (Functional search is in ProductList) */}
                    <div className="relative max-w-md w-full ml-auto hidden md:block">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-4 w-4" />
                        <input
                            type="text"
                            placeholder="Search store..."
                            className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                        />
                    </div>
                </div>
                <Outlet />
            </main>
        </div>
    );
}