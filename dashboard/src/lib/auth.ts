/**
 * Authentication utilities for Cardea Dashboard
 * Uses Azure Static Web Apps built-in authentication
 */

export interface UserInfo {
  userId: string;
  userDetails: string;
  userRoles: string[];
  identityProvider: 'aad' | 'google' | 'github' | 'twitter' | 'dev';
  claims?: Record<string, string>;
}

export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserInfo | null;
  error: string | null;
}

// Azure Static Web Apps auth endpoints
export const AUTH_ENDPOINTS = {
  microsoft: '/.auth/login/aad',
  google: '/.auth/login/google',
  github: '/.auth/login/github',
  logout: '/.auth/logout',
  me: '/.auth/me',
  purge: '/.auth/purge/aad' // Remove cached tokens
} as const;

/**
 * Check if running on Azure Static Web Apps
 */
export const isAzureHosted = (): boolean => {
  if (typeof window === 'undefined') return false;
  const hostname = window.location.hostname;
  return (
    hostname.includes('azurestaticapps.net') ||
    hostname.includes('cardea') ||
    // Add your custom domain here
    hostname.endsWith('.azurewebsites.net')
  );
};

/**
 * Get the current authenticated user from Azure SWA
 */
export async function getCurrentUser(): Promise<UserInfo | null> {
  if (isAzureHosted()) {
    try {
      const response = await fetch(AUTH_ENDPOINTS.me);
      if (response.ok) {
        const data = await response.json();
        if (data.clientPrincipal) {
          return {
            userId: data.clientPrincipal.userId,
            userDetails: data.clientPrincipal.userDetails,
            userRoles: data.clientPrincipal.userRoles || ['anonymous'],
            identityProvider: data.clientPrincipal.identityProvider,
            claims: data.clientPrincipal.claims?.reduce(
              (acc: Record<string, string>, claim: { typ: string; val: string }) => {
                acc[claim.typ] = claim.val;
                return acc;
              },
              {}
            )
          };
        }
      }
    } catch (error) {
      console.error('Failed to get user info:', error);
    }
    return null;
  } else {
    // Development mode - check localStorage
    const devAuth = localStorage.getItem('cardea_dev_auth');
    if (devAuth === 'true') {
      const devUser = localStorage.getItem('cardea_dev_user');
      if (devUser) {
        const parsed = JSON.parse(devUser);
        return {
          userId: 'dev-user-001',
          userDetails: parsed.email || 'dev@cardea.local',
          userRoles: ['authenticated', 'admin'],
          identityProvider: 'dev',
          claims: { name: parsed.name || 'Dev User' }
        };
      }
    }
    return null;
  }
}

/**
 * Login with a specific provider
 */
export function login(provider: 'microsoft' | 'google' | 'github', redirectPath: string = '/dashboard'): void {
  if (isAzureHosted()) {
    const redirectUrl = encodeURIComponent(window.location.origin + redirectPath);
    window.location.href = `${AUTH_ENDPOINTS[provider]}?post_login_redirect_uri=${redirectUrl}`;
  } else {
    // Development mode - simulate login
    localStorage.setItem('cardea_dev_auth', 'true');
    localStorage.setItem('cardea_dev_provider', provider);
    localStorage.setItem('cardea_dev_user', JSON.stringify({
      name: 'Demo User',
      email: `demo@${provider}.com`,
      provider
    }));
    window.location.href = redirectPath;
  }
}

/**
 * Logout the current user
 */
export function logout(redirectPath: string = '/login'): void {
  if (isAzureHosted()) {
    const redirectUrl = encodeURIComponent(window.location.origin + redirectPath);
    window.location.href = `${AUTH_ENDPOINTS.logout}?post_logout_redirect_uri=${redirectUrl}`;
  } else {
    localStorage.removeItem('cardea_dev_auth');
    localStorage.removeItem('cardea_dev_provider');
    localStorage.removeItem('cardea_dev_user');
    window.location.href = redirectPath;
  }
}

/**
 * Check if user has a specific role
 */
export function hasRole(user: UserInfo | null, role: string): boolean {
  if (!user) return false;
  return user.userRoles.includes(role);
}

/**
 * Get display name from user info
 */
export function getDisplayName(user: UserInfo | null): string {
  if (!user) return 'Guest';
  
  // Try to get name from claims
  if (user.claims?.name) return user.claims.name;
  if (user.claims?.['preferred_username']) return user.claims['preferred_username'];
  
  // Fall back to userDetails (usually email)
  if (user.userDetails) {
    // Extract name from email
    const emailName = user.userDetails.split('@')[0];
    return emailName.charAt(0).toUpperCase() + emailName.slice(1);
  }
  
  return 'User';
}

/**
 * Get provider icon name
 */
export function getProviderName(provider: string): string {
  switch (provider) {
    case 'aad': return 'Microsoft';
    case 'google': return 'Google';
    case 'github': return 'GitHub';
    case 'twitter': return 'Twitter';
    case 'dev': return 'Development';
    default: return provider;
  }
}
