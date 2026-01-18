import React, { useEffect, useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiRequest } from '../../lib/api';
import { useTheme } from '../../context/ThemeContext';
import { useAnalytics } from '../../hooks/useAnalytics'; 
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
    MapPin,
    Moon, 
    Sun
} from 'lucide-react';

export default function DemoLayout() {
    const navigate = useNavigate();
    const location = useLocation();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const { user, profile, signOut } = useAuth();
    const [userLocation, setUserLocation] = useState(null);
    
    const { theme, setTheme } = useTheme();
    // Analytics hook initialized (used automatically by child components or specific actions)
    const { trackEvent } = useAnalytics(); 

    const handleSignOut = async () => {
        await signOut();
        navigate('/login');
    };

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        // Note: 'toggle_theme' is ignored by useAnalytics filter now
    };

    // --- Location Sync Logic ---
    useEffect(() => {
        const updateLocation = () => {
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(async (position) => {
                    const { latitude, longitude } = position.coords;
                    setUserLocation({ lat: latitude, lng: longitude });
                    try {
                        await apiRequest(`/users/location?lat=${latitude}&lng=${longitude}`, { method: 'PATCH' });
                        console.log("Location synced");
                    } catch (e) {
                        console.error("Location sync failed", e);
                    }
                }, (err) => {
                    console.warn("Geolocation permission denied", err);
                });
            }
        };

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
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex font-sans transition-colors duration-300">
            {/* Sidebar */}
            <aside className="hidden md:flex w-64 flex-col bg-white dark:bg-gray-950 border-r border-gray-200 dark:border-gray-800 fixed h-full z-20">
                <div className="h-16 flex items-center px-6 border-b border-gray-100 dark:border-gray-800">
                    <span className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight" style={{ fontFamily: '"Charm", cursive' }}>
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
                                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-900 hover:text-gray-900 dark:hover:text-white'}`}
                            >
                                <item.icon size={20} />
                                {item.name}
                            </NavLink>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-gray-100 dark:border-gray-800 space-y-2">
                    {/* Theme Toggle */}
                    <button 
                        onClick={toggleTheme}
                        className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-900 rounded-lg transition-colors"
                    >
                        {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                        {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
                    </button>

                    <NavLink to="/demo/profile" className="flex items-center gap-3 px-4 py-3 bg-gray-50 dark:bg-gray-900 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer group">
                        <div className="h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-xs">
                            {user?.user_metadata?.full_name?.[0] || user?.email?.[0]?.toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                {user?.user_metadata?.full_name || 'User'}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 truncate flex items-center gap-1">
                                {isAdmin ? <span className="text-blue-600 dark:text-blue-400 font-bold">Admin</span> : user?.email}
                            </p>
                        </div>
                    </NavLink>
                    <button onClick={handleSignOut} className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/10 rounded-lg transition-colors">
                        <LogOut size={16} /> Sign Out
                    </button>
                </div>
            </aside>

            {/* Mobile Header */}
            <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800 z-30 flex items-center justify-between px-4">
                <span className="text-xl font-bold text-gray-900 dark:text-white" style={{ fontFamily: '"Charm", cursive' }}>Weeb</span>
                <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2 text-gray-600 dark:text-gray-300">
                    {isMobileMenuOpen ? <X /> : <Menu />}
                </button>
            </div>

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
                <div className="fixed inset-0 z-20 bg-white dark:bg-gray-950 pt-20 px-4 md:hidden animate-in fade-in slide-in-from-top-10">
                    <nav className="space-y-2">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                onClick={() => setIsMobileMenuOpen(false)}
                                className={({ isActive }) => `flex items-center gap-3 px-4 py-4 rounded-lg text-base font-medium ${isActive ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-300'}`}
                            >
                                <item.icon size={20} />
                                {item.name}
                            </NavLink>
                        ))}
                        <button 
                            onClick={toggleTheme}
                            className="w-full flex items-center gap-3 px-4 py-4 text-base font-medium text-gray-600 dark:text-gray-300 border-t border-gray-100 dark:border-gray-800 mt-4"
                        >
                            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                            {theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                        </button>
                        <button onClick={handleSignOut} className="w-full flex items-center gap-3 px-4 py-4 text-base font-medium text-red-600 border-t border-gray-100 dark:border-gray-800 mt-2">
                            <LogOut size={20} /> Sign Out
                        </button>
                    </nav>
                </div>
            )}

            {/* Content Area */}
            <main className="flex-1 md:ml-64 p-6 pt-20 md:pt-6 max-w-7xl mx-auto w-full transition-all">
                {/* Header Bar */}
                <div className="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center bg-white dark:bg-gray-950 p-4 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm sticky top-4 z-30 gap-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <MapPin size={16} className={userLocation ? "text-green-500 animate-pulse" : "text-gray-400 dark:text-gray-600"} />
                        {userLocation ? "Location Synced" : "Locating..."}
                    </div>

                    <div className="relative max-w-md w-full ml-auto hidden md:block">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-4 w-4" />
                        <input
                            type="text"
                            placeholder="Search store..."
                            className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all placeholder:text-gray-400 dark:placeholder:text-gray-600"
                        />
                    </div>
                </div>
                <Outlet />
            </main>
        </div>
    );
}