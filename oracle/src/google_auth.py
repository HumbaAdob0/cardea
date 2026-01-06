"""
Google OAuth 2.0 Authentication Module

This module handles validation of Google OAuth 2.0 access tokens and ID tokens
for the Cardea Oracle backend API.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class GoogleAuthService:
    """Service for validating Google OAuth tokens"""

    def __init__(self):
        """Initialize Google Authentication Service"""
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.token_info_url = os.getenv(
            "GOOGLE_TOKEN_INFO_URL", "https://oauth2.googleapis.com/tokeninfo"
        )
        self.enabled = os.getenv("ENABLE_GOOGLE_AUTH", "true").lower() == "true"

        # Validate configuration
        if self.enabled:
            if not self.client_id or "PASTE_YOUR" in self.client_id:
                logger.warning(
                    "Google Client ID not configured. Set GOOGLE_CLIENT_ID in .env"
                )
                self.enabled = False

        if self.enabled:
            logger.info("Google Authentication Service initialized successfully")
        else:
            logger.info("Google Authentication is disabled")

    def is_enabled(self) -> bool:
        """Check if Google authentication is enabled and configured"""
        return self.enabled

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a Google OAuth 2.0 token (ID token or access token)

        Args:
            token: The JWT ID token from Google Sign-In

        Returns:
            Dict containing user information from the token

        Raises:
            HTTPException: If token validation fails
        """
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google authentication is not enabled",
            )

        try:
            # First, try to verify as an ID token using Google's library
            try:
                idinfo = id_token.verify_oauth2_token(
                    token, google_requests.Request(), self.client_id
                )

                # Token is valid, extract user information
                user_info = {
                    "provider": "google",
                    "user_id": idinfo.get("sub"),
                    "email": idinfo.get("email"),
                    "email_verified": idinfo.get("email_verified", False),
                    "name": idinfo.get("name", ""),
                    "given_name": idinfo.get("given_name", ""),
                    "family_name": idinfo.get("family_name", ""),
                    "picture": idinfo.get("picture"),
                    "locale": idinfo.get("locale"),
                    "expires_at": datetime.fromtimestamp(idinfo.get("exp", 0)),
                    "issued_at": datetime.fromtimestamp(idinfo.get("iat", 0)),
                }

                logger.info(
                    f"Successfully validated Google ID token for user: {user_info['email']}"
                )
                return user_info

            except ValueError as id_token_error:
                # If ID token verification fails, try as access token
                logger.debug(
                    f"Not a valid ID token, trying as access token: {id_token_error}"
                )
                return self._validate_access_token(token)

        except Exception as e:
            logger.error(f"Error validating Google token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def _validate_access_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a Google access token using Google's tokeninfo endpoint

        Args:
            token: The access token to validate

        Returns:
            Dict containing user information

        Raises:
            HTTPException: If validation fails
        """
        try:
            # Call Google's tokeninfo endpoint
            response = requests.get(
                f"{self.token_info_url}?access_token={token}", timeout=10
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token_info = response.json()

            # Verify the token is for our application
            if token_info.get("aud") != self.client_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token audience mismatch",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Extract user information
            user_info = {
                "provider": "google",
                "user_id": token_info.get("sub"),
                "email": token_info.get("email"),
                "email_verified": token_info.get("email_verified") == "true",
                "expires_at": datetime.fromtimestamp(int(token_info.get("exp", 0))),
                "scope": token_info.get("scope", "").split(),
            }

            # Fetch additional user information from Google+ API if needed
            if not user_info.get("name"):
                profile = self.get_user_profile(token)
                if profile:
                    user_info.update(profile)

            logger.info(
                f"Successfully validated Google access token for user: {user_info.get('email')}"
            )
            return user_info

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating Google access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to validate access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_user_profile(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user profile information from Google People API

        Args:
            token: Access token with appropriate scope

        Returns:
            Dict containing user profile information or None if failed
        """
        if not self.enabled:
            return None

        try:
            # Google People API endpoint
            people_url = "https://people.googleapis.com/v1/people/me"
            headers = {"Authorization": f"Bearer {token}"}
            params = {"personFields": "names,emailAddresses,photos"}

            response = requests.get(
                people_url, headers=headers, params=params, timeout=10
            )

            if response.status_code == 200:
                profile = response.json()

                # Extract primary email
                emails = profile.get("emailAddresses", [])
                primary_email = next(
                    (e["value"] for e in emails if e.get("metadata", {}).get("primary")),
                    emails[0]["value"] if emails else None,
                )

                # Extract primary name
                names = profile.get("names", [])
                primary_name = next(
                    (n for n in names if n.get("metadata", {}).get("primary")),
                    names[0] if names else {},
                )

                # Extract primary photo
                photos = profile.get("photos", [])
                primary_photo = next(
                    (p["url"] for p in photos if p.get("metadata", {}).get("primary")),
                    photos[0]["url"] if photos else None,
                )

                return {
                    "email": primary_email,
                    "name": primary_name.get("displayName"),
                    "given_name": primary_name.get("givenName"),
                    "family_name": primary_name.get("familyName"),
                    "picture": primary_photo,
                }
            else:
                logger.warning(
                    f"Failed to fetch Google user profile: {response.status_code}"
                )
                return None

        except Exception as e:
            logger.error(f"Error fetching Google user profile: {e}")
            return None

    def verify_id_token_simple(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Simple verification of Google ID token without full validation
        Useful for quick checks

        Args:
            token: The ID token to verify

        Returns:
            Dict containing basic token info or None if invalid
        """
        try:
            response = requests.get(
                f"{self.token_info_url}?id_token={token}", timeout=10
            )

            if response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            logger.error(f"Error in simple ID token verification: {e}")
            return None


# Global instance
google_auth_service = GoogleAuthService()
