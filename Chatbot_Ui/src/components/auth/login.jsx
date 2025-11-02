import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import AuthLayout from "./../pages/AuthLayout";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "@/supabaseClient";
import { Spinner } from "../ui/spinner";
import { toast } from "sonner";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      localStorage.setItem("supabase_session", JSON.stringify(data.session));

      toast.success("Login successful!");
      navigate("/chatbot"); // Redirect to chatbot
    } catch (err) {
      setError(err.message);
      toast.error(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Welcome Back 👋">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="email">Email</Label>
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

        <div>
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mt-1"
          />
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <div className="flex justify-between text-sm">
          <Link to="/forgot-password" className="text-blue-500 hover:underline">
            Forgot Password?
          </Link>
          <Link
            to="/signup"
            className="text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
          >
            Create Account
          </Link>
        </div>

        <Button type="submit" className="w-full mt-3" disabled={loading}>
          {loading ? (
            <span className="flex items-center gap-2">
              <Spinner className="w-4 h-4 animate-spin" />
              Logging in...
            </span>
          ) : "Login"}
        </Button>
      </form>
    </AuthLayout>
  );
}

export default Login;
