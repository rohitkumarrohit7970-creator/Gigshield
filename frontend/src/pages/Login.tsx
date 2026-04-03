import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authApi } from '../services/api';
import { Shield, Phone, Lock, Eye, EyeOff, Sparkles } from 'lucide-react';
import Button from '../components/Button';
import Input from '../components/Input';

interface LoginProps {
  onLogin: (token: string, role: string) => void;
}

export default function Login({ onLogin }: LoginProps) {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const response = await authApi.login(phone, password);
      onLogin(response.data.access_token, response.data.role || 'worker');
      navigate(response.data.role === 'admin' ? '/admin' : '/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-20 left-20 w-72 h-72 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-blue-400/20 rounded-full blur-3xl" />
        </div>
        
        <div className="relative z-10 flex flex-col justify-center px-16">
          <div className="flex items-center space-x-3 mb-8">
            <div className="p-3 bg-white/20 backdrop-blur-sm rounded-2xl">
              <Shield className="h-10 w-10 text-white" />
            </div>
            <span className="text-4xl font-bold text-white">GigShield</span>
          </div>
          
          <h1 className="text-5xl font-bold text-white mb-6 leading-tight">
            Protect Your<br />Gig Income
          </h1>
          <p className="text-xl text-white/80 mb-10">
            Parametric insurance that pays you instantly when weather or disruptions affect your work.
          </p>
          
          <div className="space-y-4">
            <div className="flex items-center space-x-3 text-white/90">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <span className="text-lg">✓</span>
              </div>
              <span>Instant payouts based on real-time data</span>
            </div>
            <div className="flex items-center space-x-3 text-white/90">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <span className="text-lg">✓</span>
              </div>
              <span>No paperwork, no claims to file</span>
            </div>
            <div className="flex items-center space-x-3 text-white/90">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <span className="text-lg">✓</span>
              </div>
              <span>Coverage starts at just ₹99/week</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center justify-center space-x-3 mb-8">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
              <Shield className="h-8 w-8 text-white" />
            </div>
            <span className="text-2xl font-bold text-gray-800">GigShield</span>
          </div>

          <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-100">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-800">Welcome Back</h2>
              <p className="text-gray-500 mt-2">Sign in to access your dashboard</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 p-4 rounded-xl text-sm flex items-center">
                  <span className="mr-2">⚠️</span>
                  {error}
                </div>
              )}
              
              <Input
                label="Phone Number"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+919999999999"
                icon={<Phone className="h-5 w-5" />}
                required
              />

              <div className="relative">
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  icon={<Lock className="h-5 w-5" />}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-[38px] text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center text-gray-600">
                  <input type="checkbox" className="mr-2 rounded text-blue-600" />
                  Remember me
                </label>
                <a href="#" className="text-blue-600 hover:underline">Forgot password?</a>
              </div>

              <Button
                type="submit"
                loading={loading}
                className="w-full py-4"
                size="lg"
              >
                Sign In
              </Button>
            </form>

            <p className="text-center mt-6 text-gray-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-blue-600 font-semibold hover:underline">
                Register Now
              </Link>
            </p>
            
            <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
              <div className="text-sm text-gray-600 space-y-2">
                <div className="flex items-center mb-2">
                  <Sparkles className="h-4 w-4 text-blue-600 mr-2" />
                  <span className="font-semibold">Demo Credentials</span>
                </div>
                <div className="space-y-1 ml-6">
                  <p><strong>Worker:</strong> +919708159742 / password123</p>
                  <p><strong>Admin:</strong> +919999999999 / admin123</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}