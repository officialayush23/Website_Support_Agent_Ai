// import React, { createContext, useContext, useEffect, useState } from 'react';
// import { supabase } from '../lib/supabase';

// const AuthContext = createContext({});

// export const AuthProvider = ({ children }) => {
//   const [user, setUser] = useState(null);
//   const [session, setSession] = useState(null);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     // 1. Check active session
//     supabase.auth.getSession().then(({ data: { session } }) => {
//       setSession(session);
//       setUser(session?.user ?? null);
//       setLoading(false);
//     });

//     // 2. Listen for changes (login, logout, refresh)
//     const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
//       setSession(session);
//       setUser(session?.user ?? null);
//       setLoading(false);
//     });

//     return () => subscription.unsubscribe();
//   }, []);

//   const signOut = async () => {
//     await supabase.auth.signOut();
//   };

//   return (
//     <AuthContext.Provider value={{ user, session, loading, signOut }}>
//       {!loading && children}
//     </AuthContext.Provider>
//   );
// };

// export const useAuth = () => useContext(AuthContext);

import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { apiRequest } from '../lib/api';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch Profile from FastAPI
  // We accept 'accessToken' as an argument to ensure we use the fresh token immediately
  const fetchProfile = async (accessToken = null) => {
    try {
      // DEBUG: Print token for testing
      if (accessToken) {
        console.log("🔐 [Auth] Sending Token to Backend:", accessToken);
      }

      // We pass the token in headers to override apiRequest's internal lookup
      // This ensures we use the exact token we just got from Supabase
      const headers = accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
      
      const data = await apiRequest('/users/me', { headers });
      
      console.log("✅ [Auth] Profile Loaded:", data);
      setProfile(data);
    } catch (err) {
      console.error("❌ [Auth] Failed to fetch profile:", err);
      setProfile(null);
    }
  };

  useEffect(() => {
    // 1. Initial Session Check
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser(session.user);
        // Pass the token explicitly
        fetchProfile(session.access_token);
      }
      setLoading(false);
    });

    // 2. Listen for Auth Changes (Login, Logout, Token Refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        setUser(session.user);
        // Pass the fresh token from the event
        fetchProfile(session.access_token);
      } else {
        setUser(null);
        setProfile(null);
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signOut = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setProfile(null);
  };

  return (
    <AuthContext.Provider value={{ user, profile, loading, signOut, fetchProfile }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);