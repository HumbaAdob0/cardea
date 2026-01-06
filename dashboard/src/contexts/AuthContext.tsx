import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { 
  InteractionRequiredAuthError,
  EventType,
} from '@azure/msal-browser';
import type {
  AuthenticationResult,
  AccountInfo,
  EventMessage,
} from '@azure/msal-browser';
import { 
  msalInstance, 
  loginRequest, 
  apiRequest, 
  isAzureAuthEnabled, 
  isGoogleAuthEnabled,
  API_URL 
} from '../authConfig';

/**
 * Authentication Provider Type
 */
export type AuthProvider = 'microsoft' | 'google' | 'traditional' | null;

/**
 * User Interface - Unified user object from different providers
 */
export interface User {
  id: string;
  email: string;
  name: string;
  provider: AuthProvider;
  profilePicture?: string;
  accessToken: string;
}

/**
 * Auth Context Interface
 */
interface AuthContextType {
  // State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  azureAuthEnabled: boolean;
  googleAuthEnabled: boolean;

  // Microsoft Auth Methods
  login: () => Promise<void>;
  loginPopup: () => Promise<void>;
  logout: () => Promise<void>;
  
  // Google Auth Methods
  loginWithGoogle: (credentialResponse: any) => Promise<void>;
  
  // Token Management
  getAccessToken: () => Promise<string | null>;
  
  // Error Handling
  clearError: () => void;
}

/**
 * Create Auth Context
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Auth Provider Component
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const azureAuthEnabled = isAzureAuthEnabled();
  const googleAuthEnabled = isGoogleAuthEnabled();

  /**
   * Convert Microsoft account to User object
   */
  const convertMicrosoftAccountToUser = (
    account: AccountInfo, 
    accessToken: string
  ): User => {
    return {
      id: account.localAccountId,
      email: account.username,
      name: account.name || account.username,
      provider: 'microsoft',
      accessToken,
    };
  };

  /**
   * Convert Google credential to User object
   */
  const convertGoogleCredentialToUser = async (
    credentialResponse: any
  ): Promise<User> => {
    // Decode JWT token to get user info
    const token = credentialResponse.credential;
    const payload = JSON.parse(atob(token.split('.')[1]));
    
    return {
      id: payload.sub,
      email: payload.email,
      name: payload.name,
      provider: 'google',
      profilePicture: payload.picture,
      accessToken: token,
    };
  };

  /**
   * Initialize Microsoft Authentication
   */
  useEffect(() => {
    if (!azureAuthEnabled || !msalInstance) {
      setIsLoading(false);
      return;
    }

    const initializeMsal = async () => {
      try {
        await msalInstance.initialize();
        
        // Handle redirect promise
        const response = await msalInstance.handleRedirectPromise();
        
        if (response) {
          // User just logged in via redirect
          const account = response.account;
          if (account) {
            msalInstance.setActiveAccount(account);
            const userObj = convertMicrosoftAccountToUser(account, response.accessToken);
            setUser(userObj);
            
            // Send token to backend for validation and user creation
            await validateTokenWithBackend(response.accessToken, 'microsoft');
          }
        } else {
          // Check if user is already logged in
          const accounts = msalInstance.getAllAccounts();
          if (accounts.length > 0) {
            const account = accounts[0];
            msalInstance.setActiveAccount(account);
            
            // Try to get token silently
            try {
              const tokenResponse = await msalInstance.acquireTokenSilent({
                ...apiRequest,
                account: account,
              });
              
              const userObj = convertMicrosoftAccountToUser(account, tokenResponse.accessToken);
              setUser(userObj);
              
              await validateTokenWithBackend(tokenResponse.accessToken, 'microsoft');
            } catch (err) {
              console.error('Silent token acquisition failed:', err);
            }
          }
        }
      } catch (err) {
        console.error('MSAL initialization error:', err);
        setError('Failed to initialize Microsoft authentication');
      } finally {
        setIsLoading(false);
      }
    };

    initializeMsal();

    // Register event callbacks
    const callbackId = msalInstance.addEventCallback((event: EventMessage) => {
      if (event.eventType === EventType.LOGIN_SUCCESS && event.payload) {
        const payload = event.payload as AuthenticationResult;
        const account = payload.account;
        msalInstance.setActiveAccount(account);
      }
    });

    return () => {
      if (callbackId) {
        msalInstance.removeEventCallback(callbackId);
      }
    };
  }, [azureAuthEnabled]);

  /**
   * Validate token with backend and create/update user
   */
  const validateTokenWithBackend = async (token: string, provider: AuthProvider) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/oauth/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ provider }),
      });

      if (!response.ok) {
        throw new Error('Token validation failed');
      }

      const data = await response.json();
      console.log('Token validated successfully:', data);
    } catch (err) {
      console.error('Backend token validation error:', err);
      // Don't throw - allow frontend auth to continue even if backend validation fails
    }
  };

  /**
   * Microsoft Login - Redirect Flow (Recommended for production)
   */
  const login = useCallback(async () => {
    if (!azureAuthEnabled || !msalInstance) {
      setError('Microsoft authentication is not enabled');
      return;
    }

    try {
      setError(null);
      setIsLoading(true);
      await msalInstance.loginRedirect(loginRequest);
      // User will be redirected to Microsoft login page
      // After login, they'll be redirected back and handleRedirectPromise will handle it
    } catch (err: any) {
      console.error('Microsoft login error:', err);
      setError(err.message || 'Microsoft login failed');
      setIsLoading(false);
    }
  }, [azureAuthEnabled]);

  /**
   * Microsoft Login - Popup Flow (Alternative)
   */
  const loginPopup = useCallback(async () => {
    if (!azureAuthEnabled || !msalInstance) {
      setError('Microsoft authentication is not enabled');
      return;
    }

    try {
      setError(null);
      setIsLoading(true);
      
      const response = await msalInstance.loginPopup(loginRequest);
      
      if (response.account) {
        msalInstance.setActiveAccount(response.account);
        const userObj = convertMicrosoftAccountToUser(response.account, response.accessToken);
        setUser(userObj);
        
        await validateTokenWithBackend(response.accessToken, 'microsoft');
      }
    } catch (err: any) {
      console.error('Microsoft login popup error:', err);
      setError(err.message || 'Microsoft login failed');
    } finally {
      setIsLoading(false);
    }
  }, [azureAuthEnabled]);

  /**
   * Google Login
   */
  const loginWithGoogle = useCallback(async (credentialResponse: any) => {
    if (!googleAuthEnabled) {
      setError('Google authentication is not enabled');
      return;
    }

    try {
      setError(null);
      setIsLoading(true);
      
      const userObj = await convertGoogleCredentialToUser(credentialResponse);
      setUser(userObj);
      
      await validateTokenWithBackend(credentialResponse.credential, 'google');
    } catch (err: any) {
      console.error('Google login error:', err);
      setError(err.message || 'Google login failed');
    } finally {
      setIsLoading(false);
    }
  }, [googleAuthEnabled]);

  /**
   * Logout
   */
  const logout = useCallback(async () => {
    try {
      setError(null);
      
      if (user?.provider === 'microsoft' && msalInstance) {
        const account = msalInstance.getActiveAccount();
        await msalInstance.logoutRedirect({
          account: account || undefined,
        });
      } else if (user?.provider === 'google') {
        // Google logout - just clear local state
        // The user will need to re-authenticate next time
        setUser(null);
        localStorage.removeItem('access_token');
      }
      
      setUser(null);
    } catch (err: any) {
      console.error('Logout error:', err);
      setError(err.message || 'Logout failed');
    }
  }, [user]);

  /**
   * Get Access Token
   */
  const getAccessToken = useCallback(async (): Promise<string | null> => {
    if (!user) return null;

    try {
      if (user.provider === 'microsoft' && msalInstance) {
        const account = msalInstance.getActiveAccount();
        if (!account) return null;

        try {
          const response = await msalInstance.acquireTokenSilent({
            ...apiRequest,
            account: account,
          });
          return response.accessToken;
        } catch (err) {
          if (err instanceof InteractionRequiredAuthError) {
            // Silent token acquisition failed, user needs to login again
            const response = await msalInstance.acquireTokenPopup(apiRequest);
            return response.accessToken;
          }
          throw err;
        }
      } else if (user.provider === 'google') {
        // Google tokens are short-lived, return the stored token
        // In production, implement token refresh logic
        return user.accessToken;
      }
      
      return null;
    } catch (err) {
      console.error('Get access token error:', err);
      return null;
    }
  }, [user]);

  /**
   * Clear Error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    azureAuthEnabled,
    googleAuthEnabled,
    login,
    loginPopup,
    loginWithGoogle,
    logout,
    getAccessToken,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * Hook to use Auth Context
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
