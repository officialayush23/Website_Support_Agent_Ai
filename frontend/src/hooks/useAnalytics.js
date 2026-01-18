import { apiRequest } from '../lib/api';

// ✅ STRICT LIST: Only track events that build User Context & Recommendations
const RELEVANT_EVENTS = [
    'view_product',
    'click_product', 
    'search',
    'filter',
    'add_to_cart',
    'remove_from_cart',
    'checkout_started',
    'order_created',
    'payment_success',
    'complaint_created',
    'chat_message'
];

export function useAnalytics() {
  const trackEvent = async (eventType, metadata = {}) => {
    // 1. Filter out noise (e.g. theme toggles, scroll events)
    if (!RELEVANT_EVENTS.includes(eventType)) {
        return; 
    }

    try {
      // 2. Format payload exactly as UserEventCreate Pydantic model expects
      const payload = {
        event_type: eventType,
        product_id: metadata.product_id || null, // Must be UUID or null
        order_id: metadata.order_id || null,     // Must be UUID or null
        // 3. Move everything else into metadata JSONB
        metadata: {
            ...metadata,
            url: window.location.pathname,
            timestamp: new Date().toISOString()
        }
      };

      // Remove IDs from metadata to avoid duplication (cleaner DB)
      delete payload.metadata.product_id;
      delete payload.metadata.order_id;

      await apiRequest('/events/', { 
          method: 'POST', 
          body: JSON.stringify(payload) 
      });
        
    } catch (e) {
      // Silently fail for analytics to not break UX
      console.warn("Analytics Sync Failed:", e);
    }
  };

  return { trackEvent };
}