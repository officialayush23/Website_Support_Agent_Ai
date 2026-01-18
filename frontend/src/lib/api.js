import { supabase } from './supabase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint, options = {}) {
  let token = options.headers?.Authorization;

  if (!token) {
    const { data: { session } } = await supabase.auth.getSession();
    token = session?.access_token;
  }

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  get: (url) => apiRequest(url, { method: 'GET' }),
  post: (url, body) => apiRequest(url, { method: 'POST', body: JSON.stringify(body) }),
  patch: (url, body) => apiRequest(url, { method: 'PATCH', body: JSON.stringify(body) }),
  del: (url) => apiRequest(url, { method: 'DELETE' }),
};

export const analytics = {
  track: async (eventType, metadata = {}) => {
    try {
      const { productId, orderId, variantId, ...rest } = metadata;
      const payload = {
        event_type: eventType,
        product_id: productId || null,
        variant_id: variantId || null,
        order_id: orderId || null,
        metadata: rest
      };
      apiRequest('/events/', { method: 'POST', body: JSON.stringify(payload) })
        .catch(err => console.warn("Tracking failed", err));
    } catch (e) { console.warn("Analytics error", e); }
  }
};