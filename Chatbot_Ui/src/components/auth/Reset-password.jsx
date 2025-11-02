import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import AuthLayout from "../pages/AuthLayout";
import { toast } from "sonner";
import { supabase } from "@/supabaseClient";
import { useNavigate } from "react-router-dom";

function ResetPassword() {
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleReset = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error("Passwords do not match!");
      return;
    }

    try {
      setLoading(true);

      const { error } = await supabase.auth.updateUser({ password });

      if (error) throw error;

      toast.success("Password reset successful! You can now log in.");
      navigate("/login");
    } catch (err) {
      toast.error(err.message || "Failed to reset password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Set New Password 🔒">
      <form onSubmit={handleReset} className="space-y-4">
        <div>
          <Label htmlFor="password">New Password</Label>
          <Input
            id="password"
            type="password"
            placeholder="Enter new password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mt-1"
          />
        </div>

        <div>
          <Label htmlFor="confirmPassword">Confirm Password</Label>
          <Input
            id="confirmPassword"
            type="password"
            placeholder="Re-enter password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className="mt-1"
          />
        </div>

        <Button type="submit" className="w-full mt-3" disabled={loading}>
          {loading ? "Resetting..." : "Reset Password"}
        </Button>
      </form>
    </AuthLayout>
  );
}

export default ResetPassword;
