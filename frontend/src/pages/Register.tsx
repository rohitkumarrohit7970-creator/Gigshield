import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authApi, workerApi } from '../services/api';
import type { City, Zone, PremiumCalculation } from '../types';
import { Shield, Phone, User, Lock, Building2, CheckCircle, Sparkles, ArrowRight } from 'lucide-react';
import Button from '../components/Button';
import Input from '../components/Input';
import Select from '../components/Select';
import Card from '../components/Card';

export default function Register() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    phone: '',
    name: '',
    delivery_platform: 'Zomato',
    platform_id: '',
    city_id: 0,
    primary_zone_id: 0,
    password: '',
    confirmPassword: '',
  });
  const [cities, setCities] = useState<City[]>([]);
  const [zones, setZones] = useState<Zone[]>([]);
  const [premium, setPremium] = useState<PremiumCalculation | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    workerApi.getCities().then((res) => setCities(res.data));
  }, []);

  useEffect(() => {
    if (formData.city_id) {
      workerApi.getCityZones(formData.city_id).then((res) => setZones(res.data));
    }
  }, [formData.city_id]);

  useEffect(() => {
    if (formData.city_id && formData.primary_zone_id && formData.city_id > 0) {
      authApi
        .calculatePremium({
          city_id: formData.city_id,
          zone_id: formData.primary_zone_id,
          avg_daily_income: 800,
          coverage_hours: 8,
        })
        .then((res) => setPremium(res.data))
        .catch(console.error);
    }
  }, [formData.city_id, formData.primary_zone_id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await authApi.register({
        phone: formData.phone,
        name: formData.name,
        delivery_platform: formData.delivery_platform,
        platform_id: formData.platform_id,
        city_id: formData.city_id,
        primary_zone_id: formData.primary_zone_id,
        password: formData.password,
      });
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const isStep1Valid = formData.name && formData.phone && formData.password && formData.confirmPassword;
  const isStep2Valid = formData.delivery_platform && formData.platform_id && formData.city_id && formData.primary_zone_id;

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-800 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-20 right-20 w-72 h-72 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute bottom-20 left-20 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl" />
        </div>
        
        <div className="relative z-10 flex flex-col justify-center px-16">
          <div className="flex items-center space-x-3 mb-8">
            <div className="p-3 bg-white/20 backdrop-blur-sm rounded-2xl">
              <Shield className="h-10 w-10 text-white" />
            </div>
            <span className="text-4xl font-bold text-white">GigShield</span>
          </div>
          
          <h1 className="text-5xl font-bold text-white mb-6 leading-tight">
            Get Protected<br />In Minutes
          </h1>
          <p className="text-xl text-white/80 mb-10">
            Join thousands of gig workers who trust GigShield to protect their income.
          </p>
          
          <div className="space-y-4">
            {[
              'Real-time weather & disruption monitoring',
              'Automatic claim triggering - no paperwork',
              'Instant payouts to your UPI account',
              '24/7 customer support',
            ].map((item, index) => (
              <div key={index} className="flex items-center space-x-3 text-white/90">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <CheckCircle className="h-4 w-4" />
                </div>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-lg">
          <div className="lg:hidden flex items-center justify-center space-x-3 mb-6">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
              <Shield className="h-8 w-8 text-white" />
            </div>
            <span className="text-2xl font-bold text-gray-800">GigShield</span>
          </div>

          <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-100">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center space-x-2">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>1</div>
                <div className={`w-16 h-1 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`} />
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>2</div>
              </div>
              <div className="text-sm text-gray-500">
                Step {step} of 2
              </div>
            </div>

            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">
                {step === 1 ? 'Create Your Account' : 'Setup Your Coverage'}
              </h2>
              <p className="text-gray-500 mt-2">
                {step === 1 ? 'Enter your basic details to get started' : 'Choose your city and platform'}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 p-4 rounded-xl text-sm flex items-center">
                  <span className="mr-2">⚠️</span>
                  {error}
                </div>
              )}

              {step === 1 ? (
                <div className="space-y-5">
                  <Input
                    label="Full Name"
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Enter your full name"
                    icon={<User className="h-5 w-5" />}
                    required
                  />
                  
                  <Input
                    label="Phone Number"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+919999999999"
                    icon={<Phone className="h-5 w-5" />}
                    required
                  />
                  
                  <Input
                    label="Password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="Create a strong password"
                    icon={<Lock className="h-5 w-5" />}
                    required
                  />
                  
                  <Input
                    label="Confirm Password"
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    placeholder="Confirm your password"
                    icon={<Lock className="h-5 w-5" />}
                    required
                  />

                  <Button
                    type="button"
                    onClick={() => isStep1Valid && setStep(2)}
                    disabled={!isStep1Valid}
                    className="w-full"
                    size="lg"
                  >
                    Continue <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </div>
              ) : (
                <div className="space-y-5">
                  <Select
                    label="Delivery Platform"
                    value={formData.delivery_platform}
                    onChange={(e) => setFormData({ ...formData, delivery_platform: e.target.value })}
                    options={[
                      { value: 'Zomato', label: 'Zomato' },
                      { value: 'Swiggy', label: 'Swiggy' },
                    ]}
                  />
                  
                  <Input
                    label="Platform ID"
                    type="text"
                    value={formData.platform_id}
                    onChange={(e) => setFormData({ ...formData, platform_id: e.target.value })}
                    placeholder="Your Zomato/Swiggy partner ID"
                    icon={<Building2 className="h-5 w-5" />}
                    required
                  />
                  
                  <Select
                    label="City"
                    value={formData.city_id}
                    onChange={(e) => setFormData({ ...formData, city_id: Number(e.target.value), primary_zone_id: 0 })}
                    options={[{ value: 0, label: 'Select City' }, ...cities.map(c => ({ value: c.id, label: c.name }))]}
                  />
                  
                  <Select
                    label="Zone"
                    value={formData.primary_zone_id}
                    onChange={(e) => setFormData({ ...formData, primary_zone_id: Number(e.target.value) })}
                    options={[{ value: 0, label: 'Select Zone' }, ...zones.map(z => ({ value: z.id, label: z.name }))]}
                    disabled={!formData.city_id}
                  />

                  {premium && (
                    <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Estimated Weekly Premium</p>
                          <p className="text-3xl font-bold text-green-600">₹{premium.weekly_premium}</p>
                        </div>
                        <div className="text-right text-sm text-gray-500">
                          <p>City Risk: {premium.city_risk_factor}x</p>
                          <p>Zone Risk: {premium.zone_risk_factor}x</p>
                        </div>
                      </div>
                    </Card>
                  )}

                  <div className="flex space-x-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setStep(1)}
                      className="flex-1"
                      size="lg"
                    >
                      Back
                    </Button>
                    <Button
                      type="submit"
                      loading={loading}
                      disabled={!isStep2Valid}
                      className="flex-1"
                      size="lg"
                    >
                      Register
                    </Button>
                  </div>
                </div>
              )}
            </form>

            <p className="text-center mt-6 text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 font-semibold hover:underline">
                Sign In
              </Link>
            </p>
            
            <div className="mt-4 p-3 bg-amber-50 rounded-xl border border-amber-200">
              <div className="flex items-center text-sm text-amber-700">
                <Sparkles className="h-4 w-4 mr-2" />
                <span>New users get 50% off first month!</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}