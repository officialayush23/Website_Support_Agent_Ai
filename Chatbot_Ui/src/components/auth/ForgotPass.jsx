import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import AuthLayout from "../pages/AuthLayout";
import { Link } from "react-router-dom";
import { toast } from "sonner";


function ForgotPassword() {
    const [email, setEmail] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Password reset for:", email);
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

                <Button onClick={() =>
                    toast.success("Event has been created", {
                        description: "If you do not find the email, please check your spam folder.",
                     
                    })
                } type="submit" className="w-full mt-3">
                    Send Reset Link
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
