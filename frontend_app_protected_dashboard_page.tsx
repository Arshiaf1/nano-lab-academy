'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import useAuthStore from '@/lib/store';

export default function DashboardPage() {
  const { user, checkAuth, token } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    checkAuth();
    setMounted(true);
  }, [checkAuth]);

  useEffect(() => {
    if (mounted && !token) {
      router.push('/auth/login');
    }
  }, [mounted, token, router]);

  if (!mounted || !user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

          <div className="grid grid-cols-3 gap-6 mb-8">
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700">User Email</h3>
              <p className="text-lg font-semibold text-gray-900">{user.email}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700">Full Name</h3>
              <p className="text-lg font-semibold text-gray-900">{user.full_name}</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700">Role</h3>
              <p className="text-lg font-semibold text-gray-900">{user.role}</p>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Welcome to Nano Lab Academy!</h2>
            <p className="text-gray-600 mb-4">
              You are now logged in. Explore the platform to start your learning journey.
            </p>
            <div className="flex gap-4">
              <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
                Start Learning
              </button>
              <button className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition">
                View Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
