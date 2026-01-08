/**
 * React hook for authentication state
 */

import { useState, useEffect, useCallback } from 'react';
import { getCurrentUser, logout as authLogout, login as authLogin, type AuthState } from './auth';

export function useAuth(): AuthState & {
  login: (provider: 'microsoft' | 'google' | 'github') => void;
  logout: () => void;
  refresh: () => Promise<void>;
} {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
    error: null
  });

  const checkAuth = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const user = await getCurrentUser();
      setState({
        isAuthenticated: user !== null,
        isLoading: false,
        user,
        error: null
      });
    } catch (error) {
      setState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        error: error instanceof Error ? error.message : 'Authentication check failed'
      });
    }
  }, []);

  useEffect(() => {
    // Use void to explicitly ignore the promise and avoid ESLint warning
    void checkAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback((provider: 'microsoft' | 'google' | 'github') => {
    authLogin(provider);
  }, []);

  const logout = useCallback(() => {
    authLogout();
  }, []);

  return {
    ...state,
    login,
    logout,
    refresh: checkAuth
  };
}

export default useAuth;
