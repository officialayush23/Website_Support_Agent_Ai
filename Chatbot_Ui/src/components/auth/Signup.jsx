import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import AuthLayout from "../pages/AuthLayout";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "@/supabaseClient"; // ✅ import Supabase client
import { Spinner } from "../ui/spinner";

function Signup() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // ✅ Supabase sign-up
      const { data, error } = await supabase.auth.signUp({
        email: form.email,
        password: form.password,
        options: {
          data: { name: form.name },
        },
      });

      if (error) throw error;

      alert("Signup successful! Check your email for confirmation.");
      navigate("/login"); // redirect after signup
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Create Account">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Full Name</Label>
          <Input
            id="name"
            name="name"
            placeholder="John Doe"
            value={form.name}
            onChange={handleChange}
            required
            className="mt-1"
          />
        </div>

        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="you@example.com"
            value={form.email}
            onChange={handleChange}
            required
            className="mt-1"
          />
        </div>

        <div>
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            name="password"
            type="password"
            placeholder="••••••••"
            value={form.password}
            onChange={handleChange}
            required
            className="mt-1"
          />
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <Button type="submit" className="w-full mt-3" disabled={loading}>
          {loading ? (
            <span className="flex items-center gap-2">
              <Spinner className="w-4 h-4 animate-spin" />
              Signing Up...
            </span>
          ) : "Sign Up"}
        </Button>

        <p className="text-sm text-center text-gray-400">
          Already have an account?{" "}
          <Link to="/login" className="text-gray-200 hover:underline">
            Login
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}

export default Signup;
