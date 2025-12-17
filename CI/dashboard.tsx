import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Subscription, DashboardSummary } from '@/types';

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [summaryData, subsData] = await Promise.all([
        apiClient.getDashboardSummary(),
        apiClient.getSubscriptions({ status: 'active' })
      ]);
      
      setSummary(summaryData);
      setSubscriptions(subsData.subscriptions);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async (subscriptionId: string) => {
    if (!confirm('Are you sure you want to cancel this subscription?')) {
      return;
    }

    try {
      await apiClient.cancelSubscription(subscriptionId);
      // Refresh data
      fetchDashboardData();
    } catch (error) {
      console.error('Error canceling subscription:', error);
      alert('Failed to cancel subscription. Please try again.');
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Subscription Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage all your subscriptions in one place</p>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Total Subscriptions</div>
              <div className="text-3xl font-bold text-gray-900 mt-2">
                {summary.total_subscriptions}
              </div>
              <div className="text-xs text-green-600 mt-1">
                {summary.active_subscriptions} active
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Monthly Spending</div>
              <div className="text-3xl font-bold text-blue-600 mt-2">
                ${summary.monthly_spend.toFixed(2)}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Annual Spending</div>
              <div className="text-3xl font-bold text-purple-600 mt-2">
                ${summary.annual_spend.toFixed(2)}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Highest Subscription</div>
              <div className="text-lg font-bold text-gray-900 mt-2">
                {summary.highest_subscription?.service_name}
              </div>
              <div className="text-sm text-gray-600">
                ${summary.highest_subscription?.price}/
                {summary.highest_subscription?.billing_period}
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search subscriptions..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <select
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="all">All Subscriptions</option>
              <option value="active">Active Only</option>
              <option value="cancelled">Cancelled</option>
            </select>

            <button
              onClick={fetchDashboardData}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Subscription List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Service
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Billing
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Next Renewal
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredSubscriptions.map((subscription) => (
                <tr key={subscription.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        {subscription.service_logo_url ? (
                          <img
                            className="h-10 w-10 rounded"
                            src={subscription.service_logo_url}
                            alt={subscription.service_name}
                          />
                        ) : (
                          <div className="h-10 w-10 rounded bg-blue-100 flex items-center justify-center">
                            <span className="text-blue-600 font-semibold">
                              {subscription.service_name.charAt(0)}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
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
                    <div className="text-sm font-semibold text-gray-900">
                      ${subscription.price.toFixed(2)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {subscription.currency}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {subscription.billing_period}
                    </span>
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {subscription.next_renewal_date ? (
                      new Date(subscription.next_renewal_date).toLocaleDateString()
                    ) : (
                      'N/A'
                    )}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
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
                    <button
                      onClick={() => handleCancelSubscription(subscription.id)}
                      disabled={subscription.status !== 'active'}
                      className="text-red-600 hover:text-red-900 disabled:text-gray-400 disabled:cursor-not-allowed"
                    >
                      Cancel
                    </button>
                    <a
                      href={subscription.unsubscribe_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-4 text-blue-600 hover:text-blue-900"
                    >
                      Manage
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredSubscriptions.length === 0 && (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
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
              <h3 className="mt-2 text-sm font-medium text-gray-900">No subscriptions found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Start by scanning your inbox for subscriptions.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
