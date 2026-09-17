import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { authService } from '../services/authService';

export function LoginPage() {
  const [email, setEmail] = useState('child@learning.com');
  const [password, setPassword] = useState('child123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await authService.login(email, password);
      if (res.role === 'admin') navigate('/admin/dashboard');
      else if (res.role === 'parent') navigate('/parent/dashboard');
      else navigate('/child/dashboard');
    } catch (err) {
      setError('Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const setQuickRole = (rEmail, rPwd) => {
    setEmail(rEmail);
    setPassword(rPwd);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center items-center p-6">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-[#2563EB] rounded-2xl flex items-center justify-center text-white font-bold text-2xl mx-auto shadow-md">
            A
          </div>
          <h1 className="text-2xl font-bold text-[#0F172A]">Sign in to AdaptLearn</h1>
          <p className="text-sm text-slate-500">Select your role or enter credentials</p>
        </div>

        <Card className="shadow-md">
          <CardContent className="pt-6">
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
                {error}
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
                <input 
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full h-11 px-3 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
                <input 
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-11 px-3 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <Button type="submit" variant="primary" className="w-full h-11" disabled={loading}>
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <div className="mt-6 pt-6 border-t border-slate-100 text-center">
              <p className="text-xs font-semibold text-slate-500 mb-3">Quick Demo Login Shortcuts:</p>
              <div className="grid grid-cols-3 gap-2">
                <button 
                  type="button" 
                  onClick={() => setQuickRole('child@learning.com', 'child123')}
                  className="px-2 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-xs font-medium hover:bg-emerald-100"
                >
                  Child Role
                </button>
                <button 
                  type="button" 
                  onClick={() => setQuickRole('parent@learning.com', 'parent123')}
                  className="px-2 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded text-xs font-medium hover:bg-blue-100"
                >
                  Parent Role
                </button>
                <button 
                  type="button" 
                  onClick={() => setQuickRole('admin@learning.com', 'admin123')}
                  className="px-2 py-1.5 bg-purple-50 text-purple-700 border border-purple-200 rounded text-xs font-medium hover:bg-purple-100"
                >
                  Admin Role
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
