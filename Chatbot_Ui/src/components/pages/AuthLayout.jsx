import React from "react";

function AuthLayout({ title, children }) {
    return (
        <div className="flex h-screen items-center justify-center">
            <div className="top-5 absolute">
                <h1 className="text-5xl">Daksha.ai</h1>
            </div>
            <div className="w-full max-w-md p-8 space-y-6 rounded-2xl shadow-xl border border-gray-800">
                <h2 className="text-center text-2xl font-semibold ">
                    {title}
                </h2>
                {children}
            </div>
        </div>
    );
}

export default AuthLayout;
