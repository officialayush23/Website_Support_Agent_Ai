import React from "react";
import { Button } from "@/components/ui/button";
import { supabase } from "@/supabaseClient";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

function LogoutButton({ className = "" }) {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;

      localStorage.removeItem("supabase_session");
      toast.success("Logged out successfully!");
      navigate("/login");
    } catch (err) {
      toast.error("Logout failed", {
        description: err.message,
      });
    }
  };

  return (
    <Button
      variant="destructive"
      onClick={handleLogout}
      className={className}
    >
      Logout
    </Button>
  );
}

export default LogoutButton;
