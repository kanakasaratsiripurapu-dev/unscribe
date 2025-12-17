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
      let errorMessage = `HTTP ${response.status}`;
      try {
        const errorData = await response.json();
        // Handle FastAPI error format
        if (errorData.error?.message) {
          errorMessage = errorData.error.message;
        } else if (errorData.detail) {
          // FastAPI returns errors in 'detail' field
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (e) {
        // If JSON parsing fails, try to get text
        const text = await response.text().catch(() => 'Unknown error');
        errorMessage = text || `HTTP ${response.status}`;
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  // Auth endpoints
  async getAuthURL(): Promise<{ auth_url: string; state: string }> {
    return this.request('/auth/login');
  }

  async handleAuthCallback(code: string, state: string): Promise<{
    user_id: string;
    email: string;
    access_token: string;
  }> {
    return this.request(`/auth/callback?code=${code}&state=${state}`, {
      method: 'POST',
    });
  }

  // Scan endpoints
  async startScan(userId: string, dateRangeYears: number = 3): Promise<{
    session_id: string;
    status: string;
    started_at: string;
  }> {
    return this.request(`/api/scan/start?user_id=${userId}&date_range_years=${dateRangeYears}`, {
      method: 'POST',
    });
  }

  async getScanStatus(sessionId: string): Promise<{
    session_id: string;
    status: string;
    total_emails_found: number;
    emails_processed: number;
    subscriptions_found: number;
    started_at: string;
    completed_at: string | null;
  }> {
    return this.request(`/api/scan/status/${sessionId}`);
  }

  // Subscription endpoints
  async getSubscriptions(userId: string): Promise<Array<{
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
  }>> {
    return this.request(`/api/subscriptions/?user_id=${userId}`);
  }

  async cancelSubscription(subscriptionId: string, userId: string): Promise<{
    subscription_id: string;
    status: string;
    message: string;
  }> {
    return this.request(`/api/subscriptions/${subscriptionId}/cancel?user_id=${userId}`, {
      method: 'POST',
    });
  }

  // Dashboard endpoints
  async getDashboardStats(userId: string): Promise<{
    total_subscriptions: number;
    estimated_monthly_spend: number;
    estimated_annual_spend: number;
    last_scan_at: string | null;
  }> {
    return this.request(`/api/dashboard/stats/${userId}`);
  }

  // Activity endpoints
  async getActivity(userId: string, limit: number = 50): Promise<Array<{
    id: string;
    activity_type: string;
    activity_description: string;
    created_at: string;
  }>> {
    return this.request(`/api/activity/${userId}?limit=${limit}`);
  }
}

// Global API client instance
export const apiClient = new APIClient();

