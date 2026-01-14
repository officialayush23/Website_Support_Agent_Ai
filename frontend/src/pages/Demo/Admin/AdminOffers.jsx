import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../../lib/api';
import { toast } from 'sonner';
import { Tag, Calendar, Plus, Trash2, Percent } from 'lucide-react';

export default function AdminOffers() {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  
  // Form State
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_date: '',
    end_date: '',
    discount_percent: 10 // Storing this in 'rules' for simplicity
  });

  useEffect(() => {
    fetchOffers();
  }, []);

  const fetchOffers = async () => {
    try {
      const data = await apiRequest('/offers/');
      setOffers(data);
    } catch (err) {
      toast.error("Failed to fetch offers");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        title: formData.title,
        description: formData.description,
        starts_at: new Date(formData.start_date).toISOString(),
        ends_at: new Date(formData.end_date).toISOString(),
        priority: 1,
        stackable: false,
        rules: { 
            discount_type: "percentage", 
            value: parseInt(formData.discount_percent) 
        }
      };

      await apiRequest('/offers/admin', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      toast.success("Offer created successfully");
      setShowModal(false);
      fetchOffers();
      setFormData({ title: '', description: '', start_date: '', end_date: '', discount_percent: 10 });
    } catch (err) {
      toast.error("Failed: " + err.message);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Active Offers</h1>
        <button onClick={() => setShowModal(true)} className="bg-gray-900 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-gray-800">
          <Plus size={18} /> Create Offer
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {offers.map((offer) => (
            <div key={offer.id} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Percent size={100} />
                </div>
                <div className="relative z-10">
                    <h3 className="text-lg font-bold text-gray-900">{offer.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">{offer.description}</p>
                    
                    <div className="mt-4 flex items-center gap-2 text-xs font-medium text-gray-600 bg-gray-50 p-2 rounded-lg w-fit">
                        <Calendar size={14} />
                        {new Date(offer.starts_at).toLocaleDateString()} — {new Date(offer.ends_at).toLocaleDateString()}
                    </div>

                    <div className="mt-4 flex items-center gap-2">
                        <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-bold">
                            {offer.rules?.value || 0}% OFF
                        </span>
                        {offer.is_active ? (
                            <span className="text-blue-600 text-xs flex items-center gap-1"><Tag size={12}/> Active</span>
                        ) : (
                            <span className="text-gray-400 text-xs">Inactive</span>
                        )}
                    </div>
                </div>
            </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 animate-in zoom-in-95">
                <h2 className="text-xl font-bold mb-4">New Campaign</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase">Title</label>
                        <input required className="w-full border rounded-lg p-2 mt-1" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} placeholder="Summer Sale" />
                    </div>
                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase">Description</label>
                        <input className="w-full border rounded-lg p-2 mt-1" value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} placeholder="Get 20% off on all dresses" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase">Discount %</label>
                            <input type="number" required className="w-full border rounded-lg p-2 mt-1" value={formData.discount_percent} onChange={e => setFormData({...formData, discount_percent: e.target.value})} />
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase">Start Date</label>
                            <input type="datetime-local" required className="w-full border rounded-lg p-2 mt-1" value={formData.start_date} onChange={e => setFormData({...formData, start_date: e.target.value})} />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase">End Date</label>
                            <input type="datetime-local" required className="w-full border rounded-lg p-2 mt-1" value={formData.end_date} onChange={e => setFormData({...formData, end_date: e.target.value})} />
                        </div>
                    </div>
                    <div className="flex justify-end gap-2 mt-6">
                        <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-gray-600">Cancel</button>
                        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Create</button>
                    </div>
                </form>
            </div>
        </div>
      )}
    </div>
  );
}