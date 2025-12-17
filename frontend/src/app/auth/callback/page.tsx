'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

export default function AuthCallback() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState<string | null>(null);
  const [processed, setProcessed] = useState(false);

  useEffect(() => {
    // Prevent multiple executions (e.g., React StrictMode double-invocation)
    if (processed) return;
    
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (!code || !state) {
      setError('Missing authorization code or state');
      setStatus('error');
      return;
    }

    setProcessed(true);

    const handleCallback = async () => {
      try {
        const result = await apiClient.handleAuthCallback(code, state);
        // Store user ID and token
        localStorage.setItem('user_id', result.user_id);
        if (result.access_token) {
          apiClient.setAccessToken(result.access_token);
        }
        setStatus('success');
        // Redirect to home page
        setTimeout(() => {
          router.push('/');
        }, 1000);
      } catch (err: any) {
        console.error('Auth callback error:', err);
        const errorMessage = err.message || err.error?.message || 'Authentication failed';
        setError(errorMessage);
        setStatus('error');
      }
    };

    handleCallback();
  }, [searchParams, router, processed]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center bg-white p-8 rounded-xl shadow-lg max-w-md">
        {status === 'loading' && (
          <>
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Completing Authentication...</h2>
            <p className="text-gray-600">Please wait while we verify your account</p>
          </>
        )}
        {status === 'success' && (
          <>
            <div className="text-green-500 text-6xl mb-4">✓</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Authentication Successful!</h2>
            <p className="text-gray-600">Redirecting to dashboard...</p>
          </>
        )}
        {status === 'error' && (
          <>
            <div className="text-red-500 text-6xl mb-4">✗</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Authentication Failed</h2>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={() => router.push('/')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Go to Home
            </button>
          </>
        )}
      </div>
    </div>
  );
}

