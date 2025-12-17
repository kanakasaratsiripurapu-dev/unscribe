/**
 * API client for SubScout backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIClient {
  private baseURL: string;
  private accessToken: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
    
    // Load token from localStorage if available
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
    }
  }

  setAccessToken(token: string) {
    this.accessToken = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  clearAccessToken() {
    this.accessToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
      throw new Error(error.error?.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async getGoogleAuthURL(): Promise<{ auth_url: string; state: string }> {
    return this.request('/auth/google');
  }

  async handleAuthCallback(code: string, state: string): Promise<{
    access_token: string;
    user: any;
  }> {
    return this.request(`/auth/google/callback?code=${code}&state=${state}`);
  }

  async getCurrentUser(): Promise<any> {
    return this.request('/auth/me');
  }

  async logout(): Promise<void> {
    await this.request('/auth/logout', { method: 'POST' });
    this.clearAccessToken();
  }

  // Scan endpoints
  async startScan(params?: { date_range_years?: number; force_rescan?: boolean }): Promise<{
    session_id: string;
    status: string;
    estimated_emails: number;
    started_at: string;
  }> {
    return this.request('/api/scan/start', {
      method: 'POST',
      body: JSON.stringify(params || {}),
    });
  }

  async getScanStatus(sessionId: string): Promise<{
    session_id: string;
    status: string;
    total_emails_found: number;
    emails_processed: number;
    subscriptions_found: number;
    progress_percent: number;
    estimated_time_remaining_seconds?: number;
  }> {
    return this.request(`/api/scan/status/${sessionId}`);
  }

  async getScanHistory(params?: { limit?: number; offset?: number }): Promise<{
    sessions: any[];
    total: number;
  }> {
    const query = new URLSearchParams();
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.offset) query.append('offset', params.offset.toString());
    
    return this.request(`/api/scan/history?${query}`);
  }

  // Subscription endpoints
  async getSubscriptions(params?: {
    status?: string;
    category?: string;
    price_min?: number;
    price_max?: number;
    search?: string;
    sort_by?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    subscriptions: any[];
    total: number;
    summary: {
      total_monthly_spend: number;
      total_annual_spend: number;
      active_count: number;
      cancelled_count: number;
    };
  }> {
    const query = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          query.append(key, value.toString());
        }
      });
    }

    return this.request(`/api/subscriptions?${query}`);
  }

  async getSubscription(id: string): Promise<any> {
    return this.request(`/api/subscriptions/${id}`);
  }

  async cancelSubscription(id: string, reason?: string): Promise<{
    action_id: string;
    status: string;
    message: string;
    estimated_completion: string;
  }> {
    return this.request(`/api/subscriptions/${id}/cancel`, {
      method: 'POST',
      body: JSON.stringify({ reason: reason || 'No longer using', notify_me: true }),
    });
  }

  async getCancellationStatus(subscriptionId: string): Promise<{
    action_id: string;
    status: string;
    initiated_at: string;
    completed_at?: string;
    confirmation_email_detected: boolean;
    timeline: any[];
  }> {
    return this.request(`/api/subscriptions/${subscriptionId}/cancel/status`);
  }

  async updateSubscription(id: string, data: {
    price?: number;
    next_renewal_date?: string;
    status?: string;
  }): Promise<any> {
    return this.request(`/api/subscriptions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteSubscription(id: string): Promise<void> {
    await this.request(`/api/subscriptions/${id}`, { method: 'DELETE' });
  }

  // Dashboard endpoints
  async getDashboardSummary(): Promise<{
    total_subscriptions: number;
    active_subscriptions: number;
    cancelled_subscriptions: number;
    monthly_spend: number;
    annual_spend: number;
    highest_subscription?: {
      service_name: string;
      price: number;
      billing_period: string;
    };
    upcoming_renewals: any[];
    spending_trend: any[];
  }> {
    return this.request('/api/dashboard/summary');
  }

  async getCategoryBreakdown(): Promise<{
    categories: Array<{
      name: string;
      count: number;
      monthly_spend: number;
      percentage: number;
    }>;
  }> {
    return this.request('/api/dashboard/categories');
  }

  // Activity log endpoints
  async getActivity(params?: {
    limit?: number;
    offset?: number;
    type?: string;
  }): Promise<{
    activities: any[];
    total: number;
  }> {
    const query = new URLSearchParams();
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.offset) query.append('offset', params.offset.toString());
    if (params?.type) query.append('type', params.type);
    
    return this.request(`/api/activity?${query}`);
  }

  async exportActivity(format: 'csv' | 'json' = 'csv'): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/api/activity/export?format=${format}`, {
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to export activity');
    }
    
    return response.blob();
  }

  // Settings endpoints
  async getSettings(): Promise<{
    notifications: {
      renewal_reminders: boolean;
      reminder_days_before: number;
      cancellation_confirmations: boolean;
    };
    privacy: {
      data_retention_days: number;
    };
  }> {
    return this.request('/api/settings');
  }

  async updateSettings(settings: any): Promise<any> {
    return this.request('/api/settings', {
      method: 'PATCH',
      body: JSON.stringify(settings),
    });
  }

  async deleteAccount(confirmation: string): Promise<void> {
    await this.request('/api/account', {
      method: 'DELETE',
      body: JSON.stringify({ confirmation }),
    });
  }

  async exportAccountData(): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/api/account/export`, {
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to export account data');
    }
    
    return response.blob();
  }
}

// Global API client instance
export const apiClient = new APIClient();
