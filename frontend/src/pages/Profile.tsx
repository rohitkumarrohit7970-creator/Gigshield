import { useState, useEffect } from 'react';
import { workerApi } from '../services/api';
import type { Worker, Policy } from '../types';
import { Shield, User, Phone, Building2, CreditCard, Save } from 'lucide-react';
import Header from '../components/Header';
import Card, { CardHeader } from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';

interface ProfileProps {
  onLogout: () => void;
}

export default function Profile({ onLogout }: ProfileProps) {
  const [worker, setWorker] = useState<Worker | null>(null);
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    upi_id: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [workerRes, policyRes] = await Promise.all([
        workerApi.getMe(),
        workerApi.getMyPolicy().catch(() => ({ data: null })),
      ]);
      setWorker(workerRes.data);
      setPolicy(policyRes.data);
      setFormData({
        name: workerRes.data.name || '',
        upi_id: workerRes.data.upi_id || '',
      });
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setSuccess(false);
    try {
      await workerApi.updateProfile({
        name: formData.name,
        upi_id: formData.upi_id,
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Error saving profile:', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto mb-4" />
          <p className="text-gray-500">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header userName={worker?.name} userRole="worker" onLogout={onLogout} />

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">My Profile</h1>
          <p className="text-gray-500 mt-1">Manage your personal information and payment settings</p>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader 
              title="Personal Information" 
              subtitle="Update your details"
              icon={<User className="h-5 w-5" />}
            />
            <div className="space-y-4 mt-4">
              <Input
                label="Full Name"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Your full name"
                icon={<User className="h-5 w-5" />}
              />
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Phone Number"
                  type="tel"
                  value={worker?.phone || ''}
                  disabled
                  icon={<Phone className="h-5 w-5" />}
                />
                <Input
                  label="Delivery Platform"
                  type="text"
                  value={worker?.delivery_platform || ''}
                  disabled
                  icon={<Building2 className="h-5 w-5" />}
                />
              </div>
              
              <Input
                label="Platform Partner ID"
                type="text"
                value={worker?.platform_id || ''}
                disabled
                icon={<Building2 className="h-5 w-5" />}
              />
            </div>
          </Card>

          <Card>
            <CardHeader 
              title="Payment Settings" 
              subtitle="For claim payouts"
              icon={<CreditCard className="h-5 w-5" />}
            />
            <div className="space-y-4 mt-4">
              <Input
                label="UPI ID"
                type="text"
                value={formData.upi_id}
                onChange={(e) => setFormData({ ...formData, upi_id: e.target.value })}
                placeholder="yourname@upi"
                icon={<CreditCard className="h-5 w-5" />}
              />
              <p className="text-sm text-gray-500">
                Enter your UPI ID to receive instant claim payouts directly to your account.
              </p>
            </div>
          </Card>

          <Card>
            <CardHeader 
              title="My Policy" 
              subtitle="Current coverage"
              icon={<Shield className="h-5 w-5" />}
            />
            {policy ? (
              <div className="mt-4 space-y-3">
                <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                  <div>
                    <p className="text-sm text-gray-500">Status</p>
                    <p className={`font-semibold capitalize ${policy.status === 'active' ? 'text-green-600' : 'text-gray-600'}`}>
                      {policy.status}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Weekly Premium</p>
                    <p className="font-semibold text-gray-800">₹{policy.weekly_premium}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-50 rounded-xl">
                    <p className="text-sm text-gray-500">Coverage Hours/Day</p>
                    <p className="font-semibold text-gray-800">{policy.coverage_hours} hours</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-xl">
                    <p className="text-sm text-gray-500">Start Date</p>
                    <p className="font-semibold text-gray-800">{new Date(policy.coverage_start_date).toLocaleDateString()}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-4 text-center py-8">
                <Shield className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 mb-4">No active policy</p>
                <Button onClick={() => window.location.href = '/dashboard'}>
                  Get Coverage
                </Button>
              </div>
            )}
          </Card>

          {success && (
            <div className="bg-green-50 border border-green-200 text-green-600 p-4 rounded-xl flex items-center">
              <Save className="h-5 w-5 mr-2" />
              Profile updated successfully!
            </div>
          )}

          <Button
            onClick={handleSave}
            loading={saving}
            className="w-full"
            size="lg"
          >
            Save Changes
          </Button>
        </div>
      </main>
    </div>
  );
}