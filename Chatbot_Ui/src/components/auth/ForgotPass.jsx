import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import AuthLayout from "../pages/AuthLayout";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { supabase } from "@/supabaseClient";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: "http://localhost:5173/reset-password",
      });

      if (error) throw error;

      toast.success("✅ Reset link sent!", {
        description:
          "Check your inbox — if you don't see it, check the spam folder.",
        duration: 4000,
      });
    } catch (err) {
      toast.error("❌ Failed to send reset link", {
        description: err.message || "Please try again later.",
        duration: 4000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Reset Password">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="email">Enter your registered email</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="mt-1"
          />
        </div>

        <Button type="submit" className="w-full mt-3" disabled={loading}>
          {loading ? "Sending..." : "Send Reset Link"}
        </Button>

        <p className="text-sm text-center text-gray-400">
          Back to{" "}
          <Link to="/login" className="text-gray-300 hover:underline">
            Login
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}

export default ForgotPassword;
