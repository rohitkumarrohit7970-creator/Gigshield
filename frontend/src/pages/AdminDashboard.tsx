import { useState, useEffect } from 'react';
import { adminApi, claimsApi, workerApi } from '../services/api';
import type { Stats, Claim, City, DisruptionEvent } from '../types';
import { Shield, Users, FileText, DollarSign, AlertTriangle, CheckCircle, XCircle, BarChart3, Activity, Settings, Eye, Zap, Clock } from 'lucide-react';
import Header from '../components/Header';
import StatsCard from '../components/StatsCard';
import Card, { CardHeader } from '../components/Card';
import Button from '../components/Button';
import Modal from '../components/Modal';

interface AdminDashboardProps {
  onLogout: () => void;
}

export default function AdminDashboard({ onLogout }: AdminDashboardProps) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [pendingClaims, setPendingClaims] = useState<Claim[]>([]);
  const [allClaims, setAllClaims] = useState<Claim[]>([]);
  const [cities, setCities] = useState<City[]>([]);
  const [activeDisruptions, setActiveDisruptions] = useState<DisruptionEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);
  const [showClaimModal, setShowClaimModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, pendingRes, claimsRes, citiesRes, disruptionsRes] = await Promise.all([
        adminApi.getStats(),
        adminApi.getPendingClaims(),
        claimsApi.getAll(),
        workerApi.getCities(),
        adminApi.getActiveDisruptions(),
      ]);
      setStats(statsRes.data);
      setPendingClaims(pendingRes.data);
      setAllClaims(claimsRes.data);
      setCities(citiesRes.data);
      setActiveDisruptions(disruptionsRes.data);
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (claimId: number) => {
    try {
      await claimsApi.approve(claimId, 'Auto-approved by admin');
      loadData();
    } catch (err) {
      console.error('Error approving claim:', err);
    }
  };

  const handleReject = async (claimId: number) => {
    const notes = prompt('Enter rejection reason:');
    if (!notes) return;
    try {
      await claimsApi.reject(claimId, notes);
      loadData();
    } catch (err) {
      console.error('Error rejecting claim:', err);
    }
  };

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      if (cities.length > 0) {
        const zonesRes = await workerApi.getCityZones(cities[0].id);
        if (zonesRes.data.length > 0) {
          await adminApi.simulateDisruption(zonesRes.data[0].id, 'heavy_rainfall');
          alert('Disruption simulated! Claims should be generated.');
          loadData();
        }
      }
    } catch (err) {
      console.error('Error simulating:', err);
    } finally {
      setSimulating(false);
    }
  };

  const viewClaimDetails = (claim: Claim) => {
    setSelectedClaim(claim);
    setShowClaimModal(true);
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

  const getConfidenceColor = (confidence: string | null) => {
    switch (confidence) {
      case 'high': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-600 border-t-transparent mx-auto mb-4" />
          <p className="text-gray-500">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header userName="Admin" userRole="admin" onLogout={onLogout} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Admin Dashboard</h1>
            <p className="text-gray-500 mt-1">Monitor and manage all operations</p>
          </div>
          <div className="flex space-x-3">
            <Button variant="outline" icon={<BarChart3 className="h-4 w-4" />}>
              Reports
            </Button>
            <Button variant="outline" icon={<Settings className="h-4 w-4" />}>
              Settings
            </Button>
            <Button 
              variant="secondary" 
              icon={<Zap className={`h-4 w-4 ${simulating ? 'animate-pulse' : ''}`} />}
              onClick={handleSimulate}
              loading={simulating}
            >
              Simulate Disruption
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Workers"
            value={stats?.total_workers || 0}
            subtitle="Registered users"
            icon={<Users className="h-6 w-6" />}
            color="blue"
          />
          <StatsCard
            title="Active Policies"
            value={stats?.active_policies || 0}
            subtitle="Currently active"
            icon={<Shield className="h-6 w-6" />}
            color="green"
          />
          <StatsCard
            title="Pending Claims"
            value={stats?.pending_claims || 0}
            subtitle="Awaiting review"
            icon={<AlertTriangle className="h-6 w-6" />}
            color="orange"
          />
          <StatsCard
            title="Total Payouts"
            value={`₹${(stats?.total_payouts || 0).toLocaleString()}`}
            subtitle="All time"
            icon={<DollarSign className="h-6 w-6" />}
            color="purple"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="text-center">
            <p className="text-sm text-gray-500">Total Claims</p>
            <p className="text-4xl font-bold text-gray-800">{stats?.total_claims || 0}</p>
          </Card>
          <Card className="text-center">
            <p className="text-sm text-gray-500">Approved</p>
            <p className="text-4xl font-bold text-green-600">{stats?.approved_claims || 0}</p>
          </Card>
          <Card className="text-center">
            <p className="text-sm text-gray-500">Loss Ratio</p>
            <p className="text-4xl font-bold text-blue-600">{((stats?.loss_ratio || 0) * 100).toFixed(1)}%</p>
          </Card>
        </div>

        {activeDisruptions.length > 0 && (
          <Card className="mb-8 bg-gradient-to-r from-red-50 to-orange-50 border-red-200">
            <CardHeader 
              title="🔴 Active Disruptions" 
              subtitle={`${activeDisruptions.length} ongoing events`}
            />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
              {activeDisruptions.map((d) => (
                <div key={d.id} className="bg-white rounded-xl p-4 border border-red-100">
                  <div className="flex items-center justify-between mb-2">
                    <Activity className="h-5 w-5 text-red-500" />
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      d.severity === 'severe' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {d.severity}
                    </span>
                  </div>
                  <p className="font-medium text-gray-800 capitalize">{d.trigger_type.replace('_', ' ')}</p>
                  <p className="text-sm text-gray-500 mt-1">Started: {new Date(d.start_time).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader 
              title="Pending Claims Review" 
              subtitle={`${pendingClaims.length} claims awaiting action`}
              action={
                pendingClaims.length > 0 && (
                  <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                    Urgent
                  </span>
                )
              }
            />
            {pendingClaims.length > 0 ? (
              <div className="space-y-3 mt-4">
                {pendingClaims.map((claim) => (
                  <div key={claim.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
                        <Clock className="h-5 w-5 text-yellow-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">Claim #{claim.id}</p>
                        <p className="text-sm text-gray-500">Fraud Score: {claim.fraud_score?.toFixed(2) || 'N/A'}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="font-semibold text-gray-800">₹{claim.amount.toFixed(2)}</span>
                      <Button size="sm" variant="ghost" onClick={() => viewClaimDetails(claim)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                      <button
                        onClick={() => handleApprove(claim.id)}
                        className="p-2 text-green-600 hover:bg-green-50 rounded-full transition-colors"
                        title="Approve"
                      >
                        <CheckCircle className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleReject(claim.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-full transition-colors"
                        title="Reject"
                      >
                        <XCircle className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-300" />
                <p>All caught up! No pending claims.</p>
              </div>
            )}
          </Card>

          <Card>
            <CardHeader 
              title="Recent Claims" 
              subtitle="All claim activity"
              action={
                <Button size="sm" variant="ghost">View All</Button>
              }
            />
            {allClaims.length > 0 ? (
              <div className="space-y-3 mt-4 max-h-96 overflow-y-auto">
                {allClaims.slice(0, 10).map((claim) => (
                  <div key={claim.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        claim.status === 'approved' ? 'bg-green-100' :
                        claim.status === 'pending' ? 'bg-yellow-100' :
                        claim.status === 'rejected' ? 'bg-red-100' : 'bg-gray-100'
                      }`}>
                        {claim.status === 'approved' ? <CheckCircle className="h-4 w-4 text-green-600" /> :
                         claim.status === 'pending' ? <Clock className="h-4 w-4 text-yellow-600" /> :
                         claim.status === 'rejected' ? <XCircle className="h-4 w-4 text-red-600" /> :
                         <FileText className="h-4 w-4 text-gray-600" />}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-800">#{claim.id}</p>
                        <p className="text-xs text-gray-500">{new Date(claim.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-800">₹{claim.amount.toFixed(2)}</p>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(claim.status)}`}>
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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <Card>
            <CardHeader title="Top Cities by Workers" subtitle="Worker distribution" />
            <div className="mt-4 space-y-3">
              {cities.slice(0, 5).map((city, index) => (
                <div key={city.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-sm">
                      {index + 1}
                    </div>
                    <span className="text-gray-700">{city.name}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-600 rounded-full" style={{ width: `${Math.random() * 80 + 20}%` }} />
                    </div>
                    <span className="text-sm text-gray-500">Tier {city.tier}</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <CardHeader title="System Health" subtitle="Platform status" />
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-gray-700">API Services</span>
                </div>
                <span className="text-green-600 font-medium">Operational</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-gray-700">Disruption Monitor</span>
                </div>
                <span className="text-green-600 font-medium">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-gray-700">ML Models</span>
                </div>
                <span className="text-green-600 font-medium">Healthy</span>
              </div>
            </div>
          </Card>
        </div>
      </main>

      <Modal isOpen={showClaimModal} onClose={() => setShowClaimModal(false)} title={`Claim #${selectedClaim?.id} Details`} size="lg">
        {selectedClaim && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded-xl">
                <p className="text-sm text-gray-500">Amount</p>
                <p className="text-2xl font-bold text-gray-800">₹{selectedClaim.amount.toFixed(2)}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-xl">
                <p className="text-sm text-gray-500">Status</p>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedClaim.status)}`}>
                  {selectedClaim.status}
                </span>
              </div>
            </div>
            
            <div className="p-4 bg-gray-50 rounded-xl">
              <p className="text-sm text-gray-500 mb-2">Fraud Analysis</p>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-lg font-semibold text-gray-800">Score: {selectedClaim.fraud_score?.toFixed(2) || 'N/A'}</p>
                  <p className={`text-sm font-medium ${getConfidenceColor(selectedClaim.fraud_confidence).split(' ')[0]}`}>
                    Confidence: {selectedClaim.fraud_confidence || 'Pending'}
                  </p>
                </div>
                <div className={`px-4 py-2 rounded-xl ${getConfidenceColor(selectedClaim.fraud_confidence)}`}>
                  {selectedClaim.fraud_score !== null && selectedClaim.fraud_score < 0.3 ? '✅ Low Risk' :
                   selectedClaim.fraud_score !== null && selectedClaim.fraud_score < 0.7 ? '⚠️ Medium Risk' : '❌ High Risk'}
                </div>
              </div>
            </div>

            <div className="flex space-x-4">
              <Button className="flex-1" onClick={() => { handleApprove(selectedClaim.id); setShowClaimModal(false); }}>
                Approve Claim
              </Button>
              <Button variant="danger" className="flex-1" onClick={() => { setShowClaimModal(false); handleReject(selectedClaim.id); }}>
                Reject Claim
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}