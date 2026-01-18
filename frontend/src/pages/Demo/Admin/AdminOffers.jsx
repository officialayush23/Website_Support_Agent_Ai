import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../../lib/api';
import { Tag, Plus, Trash2, Calendar } from 'lucide-react';
import { toast } from 'sonner';

export default function AdminOffers() {
    const [offers, setOffers] = useState([]);
    const [isCreating, setIsCreating] = useState(false);
    
    // Offer Form
    const [form, setForm] = useState({
        title: '',
        description: '',
        percentage_off: 10,
        min_cart_value: 0,
        starts_at: new Date().toISOString().split('T')[0],
        ends_at: new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0] // +7 days
    });

    useEffect(() => { loadOffers(); }, []);

    const loadOffers = async () => {
        try {
            const data = await apiRequest('/offers/admin');
            setOffers(data);
        } catch (e) { toast.error("Failed to load offers"); }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            await apiRequest('/offers/admin', {
                method: 'POST',
                body: JSON.stringify({
                    ...form,
                    starts_at: new Date(form.starts_at).toISOString(),
                    ends_at: new Date(form.ends_at).toISOString(),
                    rules: {} // Required by schema but can be empty for simple logic
                })
            });
            toast.success("Offer Created");
            setIsCreating(false);
            loadOffers();
        } catch (err) {
            toast.error("Creation failed");
        }
    };

    const handleDeactivate = async (id) => {
        if(!confirm("Deactivate this offer?")) return;
        try {
            await apiRequest(`/offers/admin/${id}`, { method: 'DELETE' });
            toast.success("Deactivated");
            loadOffers();
        } catch (e) { toast.error("Failed"); }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold dark:text-white">Offers & Discounts</h1>
                <button 
                    onClick={() => setIsCreating(true)}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                    <Plus size={18} /> New Offer
                </button>
            </div>

            {/* Creation Form */}
            {isCreating && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 animate-in slide-in-from-top-4">
                    <h3 className="font-bold text-lg mb-4 dark:text-white">Create New Campaign</h3>
                    <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                            <div>
                                <label className="text-sm font-medium dark:text-gray-300">Title</label>
                                <input required className="w-full p-2 border rounded dark:bg-gray-900 dark:border-gray-700 dark:text-white" value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="Summer Sale" />
                            </div>
                            <div>
                                <label className="text-sm font-medium dark:text-gray-300">Description</label>
                                <input className="w-full p-2 border rounded dark:bg-gray-900 dark:border-gray-700 dark:text-white" value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Flat 10% off on all items" />
                            </div>
                        </div>
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm font-medium dark:text-gray-300">Percentage Off (%)</label>
                                    <input type="number" required className="w-full p-2 border rounded dark:bg-gray-900 dark:border-gray-700 dark:text-white" value={form.percentage_off} onChange={e => setForm({...form, percentage_off: e.target.value})} />
                                </div>
                                <div>
                                    <label className="text-sm font-medium dark:text-gray-300">Min Cart Value (₹)</label>
                                    <input type="number" className="w-full p-2 border rounded dark:bg-gray-900 dark:border-gray-700 dark:text-white" value={form.min_cart_value} onChange={e => setForm({...form, min_cart_value: e.target.value})} />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm font-medium dark:text-gray-300">Starts</label>
                                    <input type="date" required className="w-full p-2 border rounded dark:bg-gray-900 dark:border-gray-700 dark:text-white" value={form.starts_at} onChange={e => setForm({...form, starts_at: e.target.value})} />
                                </div>
                                <div>
                                    <label className="text-sm font-medium dark:text-gray-300">Ends</label>
                                    <input type="date" required className="w-full p-2 border rounded dark:bg-gray-900 dark:border-gray-700 dark:text-white" value={form.ends_at} onChange={e => setForm({...form, ends_at: e.target.value})} />
                                </div>
                            </div>
                        </div>
                        <div className="md:col-span-2 flex justify-end gap-2">
                            <button type="button" onClick={() => setIsCreating(false)} className="px-4 py-2 text-gray-500">Cancel</button>
                            <button type="submit" className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">Publish Offer</button>
                        </div>
                    </form>
                </div>
            )}

            {/* List */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {offers.map(offer => (
                    <div key={offer.id} className="relative bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 flex justify-between items-start overflow-hidden">
                        {/* Decorative background */}
                        <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl"></div>
                        
                        <div>
                            <div className="flex items-center gap-2 mb-2">
                                <Tag size={18} className="text-blue-500" />
                                <h3 className="font-bold text-lg dark:text-white">{offer.title}</h3>
                                {!offer.is_active && <span className="bg-red-100 text-red-600 text-[10px] px-2 py-0.5 rounded-full">Inactive</span>}
                            </div>
                            <p className="text-gray-500 dark:text-gray-400 text-sm">{offer.description}</p>
                            
                            <div className="mt-4 flex gap-4 text-xs font-mono text-gray-500">
                                <div className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                                    {offer.percentage_off ? `${offer.percentage_off}% OFF` : `₹${offer.amount_off} OFF`}
                                </div>
                                <div className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded flex items-center gap-1">
                                    <Calendar size={12} /> {new Date(offer.ends_at).toLocaleDateString()}
                                </div>
                            </div>
                        </div>

                        <button 
                            onClick={() => handleDeactivate(offer.id)}
                            className="text-gray-400 hover:text-red-500 transition-colors p-2"
                        >
                            <Trash2 size={18} />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}