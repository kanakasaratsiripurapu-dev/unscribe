'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

interface Subscription {
  id: string;
  service_name: string;
  price: number;
  currency: string;
  billing_period: string;
  next_renewal_date: string | null;
  status: string;
  unsubscribe_link: string | null;
  subscription_tier: string | null;
  service_logo_url: string | null;
}

interface DashboardStats {
  total_subscriptions: number;
  estimated_monthly_spend: number;
  estimated_annual_spend: number;
  last_scan_at: string | null;
}

export default function Home() {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Check for user ID in localStorage or start auth flow
    const storedUserId = localStorage.getItem('user_id');
    if (storedUserId) {
      setUserId(storedUserId);
      fetchData(storedUserId);
    } else {
      // Start auth flow
      handleLogin();
    }
  }, []);

  const handleLogin = async () => {
    try {
      const { auth_url } = await apiClient.getAuthURL();
      // Store state for callback
      window.location.href = auth_url;
    } catch (err: any) {
      setError('Failed to initiate login: ' + err.message);
      setLoading(false);
    }
  };

  const fetchData = async (uid: string) => {
    try {
      setLoading(true);
      const [subsData, statsData] = await Promise.all([
        apiClient.getSubscriptions(uid),
        apiClient.getDashboardStats(uid).catch(() => null),
      ]);
      setSubscriptions(subsData);
      setStats(statsData);
    } catch (err: any) {
      setError('Failed to load data: ' + err.message);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartScan = async () => {
    if (!userId) return;
    try {
      setScanning(true);
      const result = await apiClient.startScan(userId);
      alert(`Scan started! Session ID: ${result.session_id}`);
      // Poll for status
      setTimeout(() => fetchData(userId), 5000);
    } catch (err: any) {
      alert('Failed to start scan: ' + err.message);
    } finally {
      setScanning(false);
    }
  };

  const handleLogout = () => {
    // Clear all authentication data
    localStorage.removeItem('user_id');
    localStorage.removeItem('access_token');
    apiClient.clearAccessToken();
    
    // Reset state
    setUserId(null);
    setSubscriptions([]);
    setStats(null);
    
    // Start new auth flow
    handleLogin();
  };

  const handleCancelSubscription = async (subscriptionId: string) => {
    if (!userId || !confirm('Are you sure you want to cancel this subscription?')) {
      return;
    }

    try {
      await apiClient.cancelSubscription(subscriptionId, userId);
      alert('Cancellation initiated successfully!');
      fetchData(userId);
    } catch (err: any) {
      alert('Failed to cancel subscription: ' + err.message);
    }
  };

  const filteredSubscriptions = subscriptions
    .filter(sub => {
      if (filter !== 'all' && sub.status !== filter) return false;
      if (searchTerm && !sub.service_name.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      return true;
    })
    .sort((a, b) => b.price - a.price);

  if (loading && !userId) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (error && !userId) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center bg-white p-8 rounded-lg shadow-lg max-w-md">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">SubScout</h1>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={handleLogin}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SubScout</h1>
              <p className="text-gray-600 mt-1">AI-Powered Subscription Management</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleStartScan}
                disabled={scanning}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
              >
                {scanning ? 'Scanning...' : 'Scan Email'}
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-semibold"
                title="Logout and use a different email"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
              <div className="text-sm font-medium text-gray-600">Total Subscriptions</div>
              <div className="text-4xl font-bold text-gray-900 mt-2">
                {stats.total_subscriptions}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
              <div className="text-sm font-medium text-gray-600">Monthly Spending</div>
              <div className="text-4xl font-bold text-green-600 mt-2">
                ${stats.estimated_monthly_spend.toFixed(2)}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
              <div className="text-sm font-medium text-gray-600">Annual Spending</div>
              <div className="text-4xl font-bold text-purple-600 mt-2">
                ${stats.estimated_annual_spend.toFixed(2)}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-orange-500">
              <div className="text-sm font-medium text-gray-600">Last Scan</div>
              <div className="text-lg font-semibold text-gray-900 mt-2">
                {stats.last_scan_at 
                  ? new Date(stats.last_scan_at).toLocaleDateString()
                  : 'Never'
                }
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search subscriptions..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <select
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="all">All Subscriptions</option>
              <option value="active">Active Only</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        {/* Subscription List */}
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading subscriptions...</p>
            </div>
          ) : filteredSubscriptions.length === 0 ? (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-16 w-16 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-gray-900">No subscriptions found</h3>
              <p className="mt-2 text-sm text-gray-500">
                Click "Scan Email" to discover your subscriptions from your Gmail inbox.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Service
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Billing
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Next Renewal
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredSubscriptions.map((subscription) => (
                    <tr key={subscription.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-12 w-12">
                            {subscription.service_logo_url ? (
                              <img
                                className="h-12 w-12 rounded-lg object-cover"
                                src={subscription.service_logo_url}
                                alt={subscription.service_name}
                              />
                            ) : (
                              <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                                <span className="text-white font-bold text-lg">
                                  {subscription.service_name.charAt(0).toUpperCase()}
                                </span>
                              </div>
                            )}
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-semibold text-gray-900">
                              {subscription.service_name}
                            </div>
                            {subscription.subscription_tier && (
                              <div className="text-xs text-gray-500">
                                {subscription.subscription_tier}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-lg font-bold text-gray-900">
                          ${subscription.price.toFixed(2)}
                        </div>
                        <div className="text-xs text-gray-500">
                          {subscription.currency}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 capitalize">
                          {subscription.billing_period}
                        </span>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {subscription.next_renewal_date 
                          ? new Date(subscription.next_renewal_date).toLocaleDateString()
                          : 'N/A'
                        }
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          subscription.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : subscription.status === 'cancelled'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {subscription.status}
                        </span>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {subscription.status === 'active' && (
                          <button
                            onClick={() => handleCancelSubscription(subscription.id)}
                            className="text-red-600 hover:text-red-900 font-semibold mr-4"
                          >
                            Cancel
                          </button>
                        )}
                        {subscription.unsubscribe_link && (
                          <a
                            href={subscription.unsubscribe_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-900 font-semibold"
                          >
                            Manage
                          </a>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

