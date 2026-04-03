import { useState, useEffect } from 'react';
import { workerApi, claimsApi } from '../services/api';
import type { Worker, Policy, Claim, EarningsHistory, DisruptionEvent } from '../types';
import { Shield, DollarSign, Clock, FileText, AlertTriangle, CheckCircle, XCircle, Calendar, Activity } from 'lucide-react';
import Header from '../components/Header';
import StatsCard from '../components/StatsCard';
import Card, { CardHeader } from '../components/Card';
import Button from '../components/Button';
import Modal from '../components/Modal';

interface WorkerDashboardProps {
  onLogout: () => void;
}

export default function WorkerDashboard({ onLogout }: WorkerDashboardProps) {
  const [worker, setWorker] = useState<Worker | null>(null);
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [earnings, setEarnings] = useState<EarningsHistory | null>(null);
  const [activeDisruptions, setActiveDisruptions] = useState<DisruptionEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showClaimModal, setShowClaimModal] = useState(false);
  const [selectedDisruption, setSelectedDisruption] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [workerRes, policyRes, claimsRes, earningsRes, disruptionsRes] = await Promise.all([
        workerApi.getMe(),
        workerApi.getMyPolicy(),
        workerApi.getMyClaims(),
        workerApi.getMyEarnings(),
        workerApi.getActiveDisruptions(),
      ]);
      setWorker(workerRes.data);
      setPolicy(policyRes.data);
      setClaims(claimsRes.data);
      setEarnings(earningsRes.data);
      setActiveDisruptions(disruptionsRes.data);
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClaimSubmit = async () => {
    if (!selectedDisruption) return;
    try {
      await claimsApi.create({ disruption_event_id: selectedDisruption });
      setShowClaimModal(false);
      setSelectedDisruption(null);
      loadData();
    } catch (err) {
      console.error('Error submitting claim:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-700 border-green-200';
      case 'pending': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'rejected': return 'bg-red-100 text-red-700 border-red-200';
      case 'under_review': return 'bg-blue-100 text-blue-700 border-blue-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'severe': return '🔴';
      case 'moderate': return '🟡';
      default: return '🟢';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto mb-4" />
          <p className="text-gray-500">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header userName={worker?.name} userRole="worker" onLogout={onLogout} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Welcome back, {worker?.name?.split(' ')[0]}! 👋</h1>
          <p className="text-gray-500 mt-1">Here's your income protection overview</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Avg Daily Income"
            value={`₹${earnings?.avg_daily.toFixed(0) || 0}`}
            subtitle="Based on last 30 days"
            icon={<DollarSign className="h-6 w-6" />}
            color="green"
          />
          <StatsCard
            title="Weekly Premium"
            value={`₹${policy?.weekly_premium || 0}`}
            subtitle={`${policy?.coverage_hours || 0} hrs coverage`}
            icon={<Shield className="h-6 w-6" />}
            color="blue"
          />
          <StatsCard
            title="Active Claims"
            value={claims.filter(c => c.status === 'pending' || c.status === 'under_review').length}
            subtitle="Under review"
            icon={<FileText className="h-6 w-6" />}
            color="orange"
          />
          <StatsCard
            title="Total Protected"
            value={`₹${((policy?.weekly_premium || 0) * 4 * 3).toFixed(0)}`}
            subtitle="Last 3 months"
            icon={<Activity className="h-6 w-6" />}
            color="purple"
          />
        </div>

        {activeDisruptions.length > 0 && (
          <Card className="mb-8 bg-gradient-to-r from-red-50 to-orange-50 border-red-200">
            <CardHeader 
              title="⚠️ Active Disruptions in Your Area" 
              subtitle="You may be eligible for automatic claims"
            />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
              {activeDisruptions.map((d) => (
                <div key={d.id} className="bg-white rounded-xl p-4 border border-red-100">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-2xl">{getSeverityIcon(d.severity)}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${d.severity === 'severe' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>
                      {d.severity}
                    </span>
                  </div>
                  <p className="font-medium text-gray-800 capitalize">{d.trigger_type.replace('_', ' ')}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    <Calendar className="h-3 w-3 inline mr-1" />
                    {new Date(d.start_time).toLocaleDateString()}
                  </p>
                  <Button size="sm" className="mt-3 w-full" onClick={() => { setSelectedDisruption(d.id); setShowClaimModal(true); }}>
                    Check Eligibility
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader 
                title="My Policy" 
                subtitle="Your current coverage details"
                action={
                  policy ? (
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${policy.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                      {policy.status}
                    </span>
                  ) : null
                }
              />
              {policy ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mt-4">
                  <div className="text-center p-4 bg-gray-50 rounded-xl">
                    <Shield className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">Coverage Status</p>
                    <p className="font-semibold text-gray-800 capitalize">{policy.status}</p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-xl">
                    <Calendar className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">Start Date</p>
                    <p className="font-semibold text-gray-800">{new Date(policy.coverage_start_date).toLocaleDateString()}</p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-xl">
                    <Clock className="h-8 w-8 text-orange-600 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">Hours/Day</p>
                    <p className="font-semibold text-gray-800">{policy.coverage_hours} hrs</p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Shield className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 mb-4">No active policy found</p>
                  <Button>Get Coverage Now</Button>
                </div>
              )}
            </Card>

            <Card className="mt-6">
              <CardHeader title="Claim History" subtitle="Your recent claims" />
              {claims.length > 0 ? (
                <div className="space-y-3 mt-4">
                  {claims.slice(0, 5).map((claim) => (
                    <div key={claim.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                      <div className="flex items-center space-x-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          claim.status === 'approved' ? 'bg-green-100' :
                          claim.status === 'pending' ? 'bg-yellow-100' : 'bg-red-100'
                        }`}>
                          {claim.status === 'approved' ? <CheckCircle className="h-5 w-5 text-green-600" /> :
                           claim.status === 'pending' ? <Clock className="h-5 w-5 text-yellow-600" /> :
                           <XCircle className="h-5 w-5 text-red-600" />}
                        </div>
                        <div>
                          <p className="font-medium text-gray-800">Claim #{claim.id}</p>
                          <p className="text-sm text-gray-500">{new Date(claim.created_at).toLocaleDateString()}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-800">₹{claim.amount.toFixed(2)}</p>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(claim.status)}`}>
                          {claim.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                  <p>No claims yet</p>
                </div>
              )}
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
              <div className="text-center py-4">
                <Shield className="h-12 w-12 mx-auto mb-3" />
                <h3 className="text-xl font-bold mb-2">Your Protection Score</h3>
                <p className="text-4xl font-bold mb-2">92%</p>
                <p className="text-blue-100 text-sm">Excellent coverage</p>
              </div>
            </Card>

            <Card>
              <CardHeader title="Earnings Overview" subtitle="Last 30 days" />
              <div className="mt-4 space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Avg Daily</span>
                  <span className="font-semibold text-gray-800">₹{earnings?.avg_daily.toFixed(0) || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Avg Hourly</span>
                  <span className="font-semibold text-gray-800">₹{earnings?.avg_hourly.toFixed(0) || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Days</span>
                  <span className="font-semibold text-gray-800">{earnings?.total_days || 0}</span>
                </div>
                <div className="pt-4 border-t">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Total Earnings</span>
                    <span className="font-bold text-green-600">₹{earnings?.total_earnings.toFixed(0) || 0}</span>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <CardHeader title="Quick Tips" subtitle="Maximize your coverage" />
              <ul className="mt-4 space-y-3 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  Keep your delivery platform ID updated
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  Claims are auto-triggered during disruptions
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  Payouts arrive within 24 hours of approval
                </li>
              </ul>
            </Card>
          </div>
        </div>
      </main>

      <Modal isOpen={showClaimModal} onClose={() => setShowClaimModal(false)} title="Claim Eligibility Check" size="md">
        <div className="text-center py-4">
          <AlertTriangle className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">
            A disruption event was detected in your area. Let us check if you're eligible for a claim.
          </p>
          {selectedDisruption && (
            <p className="text-sm text-gray-500 mb-6">
              Event ID: #{selectedDisruption}
            </p>
          )}
          <div className="flex space-x-4">
            <Button variant="outline" className="flex-1" onClick={() => setShowClaimModal(false)}>
              Cancel
            </Button>
            <Button className="flex-1" onClick={handleClaimSubmit}>
              Check & Submit
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}