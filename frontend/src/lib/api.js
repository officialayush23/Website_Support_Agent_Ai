import { supabase } from './supabase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint, options = {}) {
  let token;

  // 1. Check if token is already provided in headers (Optimization)
  if (options.headers?.Authorization) {
    // Token is already in the headers passed to this function
    // We don't need to do anything, fetch will use it.
  } else {
    // 2. Otherwise, fetch current session token
    const { data: { session } } = await supabase.auth.getSession();
    token = session?.access_token;
  
    if (!token) {
      throw new Error("Unauthorized: No session token found");
    }
    
    // Add to headers
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    };
  }

  // 3. Set Content-Type default
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // 4. Make request
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

// ... analytics export remains the same
export const analytics = {
  track: async (eventType, payload = {}) => {
    try {
      await apiRequest('/events/', {
        method: 'POST',
        body: JSON.stringify({
          event_type: eventType,
          product_id: payload.productId || null,
          order_id: payload.orderId || null,
          metadata: payload.metadata || {}
        })
      });
    } catch (err) {
      console.error("[Analytics] Failed to track event:", err);
    }
  },
  
  getContext: async () => {
    return apiRequest('/events/context');
  }
};