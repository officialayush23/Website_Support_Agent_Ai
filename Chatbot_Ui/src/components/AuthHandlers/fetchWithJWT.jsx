import { supabase } from "../../supabaseclient";

export async function fetchWithAuth(endpoint, options = {}) {
    try {
        // Get the current session (may trigger refresh if expired)
        const { data, error } = await supabase.auth.getSession();

        if (error) {
            console.error("Supabase session error:", error.message);
            throw new Error("Authentication session error");
        }

        const token = data?.session?.access_token;
        console.log("🔐 Sending token:", token?.slice(0, 20) + "...");
        // Merge headers
        const headers = {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...options.headers,
        };

        const apiUrl = import.meta.env.VITE_API_URL;
        const fullUrl = `${apiUrl}${endpoint}`;

        const response = await fetch(fullUrl, {
            ...options,
            headers,
        });



        // Handle 401 unauthorized (e.g., expired or invalid token)
        if (response.status === 401) {
            console.warn("Unauthorized: refreshing session and retrying...");

            const { data: refreshedData, error: refreshError } = await supabase.auth.refreshSession();
            if (refreshError) {
                throw new Error("Session refresh failed");
            }

            const newToken = refreshedData?.session?.access_token;

            const retryResponse = await fetch(fullUrl, {
                ...options,
                headers: {
                    ...headers,
                    Authorization: `Bearer ${newToken}`,
                },
            });

            if (!retryResponse.ok) {
                const errText = await retryResponse.text();
                throw new Error(`Retry failed: ${errText}`);
            }

            return await retryResponse.json();
        }

        if (!response.ok) {
            const errText = await response.text();
            console.error("Fetch failed:", errText);
            throw new Error(errText || "API request failed");
        }

        return await response.json();
    } catch (err) {
        console.error("Error in fetchWithAuth:", err.message);
        throw err;
    }


}
