import React, { createContext, useContext, useEffect, useState } from "react";
import { supabase } from "../../supabaseclient"; // ✅ Import shared client

const SupabaseContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const { data: authListener } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    supabase.auth.getSession().then(({ data }) => {
      setUser(data.session?.user ?? null);
      setLoading(false);
    });

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  const signUp = async (email, password) => {
    const { data, error } = await supabase.auth.signUp({ email, password });
    if (error) throw error;
    return data;
  };

  const signIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    localStorage.setItem("access_token", data.session.access_token); // ✅ store token for fetchWithAuth
    return data;
  };

  const resetPassword = async (email) => {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email);
    if (error) throw error;
    return data;
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    localStorage.removeItem("access_token");
    setUser(null);
  };

  return (
    <SupabaseContext.Provider value={{ supabase, user, signUp, signIn, signOut, resetPassword, loading }}>
      {children}
    </SupabaseContext.Provider>
  );
};

export const useAuth = () => useContext(SupabaseContext);
