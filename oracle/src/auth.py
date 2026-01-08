"""
Authentication and Authorization
JWT-based authentication system with role-based access control
Supports email/password with verification and OAuth (Google/Microsoft)
"""

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

from config import settings
from database import get_db
from models import TokenData, User

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer(auto_error=False)  # Don't auto-error, we check manually


# Request/Response Models for Auth Endpoints
class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=200)


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    """Email verification request"""
    token: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Password reset request"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    """Change password request (when logged in)"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class AuthResponse(BaseModel):
    """Authentication response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class MessageResponse(BaseModel):
    """Simple message response"""
    success: bool
    message: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=scopes)
        return token_data
        
    except JWTError:
        raise credentials_exception

async def get_user(username: str) -> Optional[User]:
    """Get user from database"""
    try:
        from sqlalchemy import text
        async with get_db() as db:
            result = await db.execute(
                text("SELECT * FROM users WHERE username = :username AND is_active = true"),
                {"username": username}
            )
            user_data = result.fetchone()
            
            if user_data:
                return User(
                    username=user_data.username,
                    email=user_data.email,
                    full_name=user_data.full_name,
                    is_active=user_data.is_active,
                    roles=user_data.roles or []
                )
            return None
            
    except Exception as e:
        logger.error(f"Failed to get user {username}: {e}")
        return None

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user credentials"""
    try:
        from sqlalchemy import text
        async with get_db() as db:
            result = await db.execute(
                text("SELECT * FROM users WHERE username = :username AND is_active = true"),
                {"username": username}
            )
            user_data = result.fetchone()
            
            if user_data and verify_password(password, user_data.hashed_password):
                # Update last login
                await db.execute(
                    text("UPDATE users SET last_login = :last_login WHERE username = :username"),
                    {"last_login": datetime.now(timezone.utc), "username": username}
                )
                await db.commit()
                
                return User(
                    username=user_data.username,
                    email=user_data.email,
                    full_name=user_data.full_name,
                    is_active=user_data.is_active,
                    roles=user_data.roles or []
                )
            return None
            
    except Exception as e:
        logger.error(f"Authentication failed for {username}: {e}")
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""
    try:
        token_data = verify_token(credentials.credentials)
        user = await get_user(username=token_data.username)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
        
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def check_permissions(required_roles: list[str]):
    """Dependency to check if user has required roles"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        if not any(role in current_user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return permission_checker

async def create_user(
    username: str,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    roles: Optional[list[str]] = None
) -> User:
    """Create a new user"""
    try:
        hashed_password = get_password_hash(password)
        user_roles = roles or ["user"]
        
        async with get_db() as db:
            # Check if user already exists
            existing = await db.execute(
                "SELECT username FROM users WHERE username = %s OR email = %s",
                (username, email)
            )
            if existing.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists"
                )
            
            # Insert new user
            await db.execute(
                """
                INSERT INTO users (username, email, hashed_password, full_name, roles, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (username, email, hashed_password, full_name, user_roles, True)
            )
            await db.commit()
            
            return User(
                username=username,
                email=email,
                full_name=full_name,
                is_active=True,
                roles=user_roles
            )
            
    except Exception as e:
        logger.error(f"Failed to create user {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

async def create_default_admin():
    """Create default admin user if none exists"""
    try:
        async with get_db() as db:
            # Check if any admin user exists
            result = await db.execute(
                "SELECT COUNT(*) FROM users WHERE roles @> %s",
                ('["admin"]',)
            )
            admin_count = result.scalar()
            
            if admin_count == 0:
                # Create default admin
                admin_password = os.getenv("ADMIN_PASSWORD", secrets.token_urlsafe(16))
                
                await create_user(
                    username="admin",
                    email="admin@cardea.local",
                    password=admin_password,
                    full_name="System Administrator",
                    roles=["admin", "user"]
                )
                
                # Log creation without exposing the password
                if os.getenv("ADMIN_PASSWORD"):
                    logger.info("Created default admin user with password from ADMIN_PASSWORD env var")
                else:
                    logger.warning("Created default admin user with auto-generated password. Set ADMIN_PASSWORD env var to specify.")
                logger.warning("Please change the admin password immediately!")
                
    except Exception as e:
        logger.error(f"Failed to create default admin: {e}")

# Webhook authentication for Sentry services
async def verify_sentry_webhook(token: str) -> bool:
    """Verify webhook token from Sentry services"""
    return token == settings.SENTRY_WEBHOOK_TOKEN

def webhook_auth_required():
    """Dependency for webhook authentication"""
    def webhook_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
        if not verify_sentry_webhook(credentials.credentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return True
    return webhook_checker


# ============================================================================
# Email/Password Registration with Email Verification
# ============================================================================

async def register_user(request: RegisterRequest) -> MessageResponse:
    """
    Register a new user with email/password.
    Sends verification email before account is active.
    """
    from email_service import send_verification_email, generate_verification_token
    from sqlalchemy import text
    
    try:
        async with get_db() as db:
            # Check if email already exists
            existing = await db.execute(
                text("SELECT id, email_verified FROM users WHERE email = :email"),
                {"email": request.email}
            )
            existing_user = existing.fetchone()
            
            if existing_user:
                if existing_user.email_verified:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="An account with this email already exists"
                    )
                else:
                    # Resend verification email for unverified account
                    token = generate_verification_token()
                    expires = datetime.now(timezone.utc) + timedelta(hours=24)
                    
                    await db.execute(
                        text("""
                            UPDATE users 
                            SET email_verification_token = :token,
                                email_verification_expires = :expires,
                                updated_at = :updated_at
                            WHERE id = :user_id
                        """),
                        {
                            "token": token,
                            "expires": expires,
                            "updated_at": datetime.now(timezone.utc),
                            "user_id": existing_user.id
                        }
                    )
                    await db.commit()
                    
                    # Send verification email
                    await send_verification_email(
                        to_email=request.email,
                        user_name=request.full_name or request.email.split("@")[0],
                        verification_token=token
                    )
                    
                    return MessageResponse(
                        success=True,
                        message="Verification email sent. Please check your inbox."
                    )
            
            # Create new user
            hashed_password = get_password_hash(request.password)
            username = request.email.split("@")[0]  # Use email prefix as username
            token = generate_verification_token()
            expires = datetime.now(timezone.utc) + timedelta(hours=24)
            
            # Make username unique if already exists
            base_username = username
            counter = 1
            while True:
                check = await db.execute(
                    text("SELECT id FROM users WHERE username = :username"),
                    {"username": username}
                )
                if not check.fetchone():
                    break
                username = f"{base_username}{counter}"
                counter += 1
            
            # Insert new user
            await db.execute(
                text("""
                    INSERT INTO users (
                        username, email, hashed_password, full_name,
                        email_verified, email_verification_token, email_verification_expires,
                        is_active, roles, created_at, updated_at
                    ) VALUES (
                        :username, :email, :hashed_password, :full_name,
                        false, :token, :expires,
                        true, '["user"]'::jsonb, :now, :now
                    )
                """),
                {
                    "username": username,
                    "email": request.email,
                    "hashed_password": hashed_password,
                    "full_name": request.full_name,
                    "token": token,
                    "expires": expires,
                    "now": datetime.now(timezone.utc)
                }
            )
            await db.commit()
            
            # Send verification email
            await send_verification_email(
                to_email=request.email,
                user_name=request.full_name or username,
                verification_token=token
            )
            
            logger.info(f"New user registered: {request.email}")
            
            return MessageResponse(
                success=True,
                message="Account created! Please check your email to verify your account."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


async def verify_email(request: VerifyEmailRequest) -> AuthResponse:
    """
    Verify email address using token from email.
    Returns auth token on success so user is logged in immediately.
    """
    from sqlalchemy import text
    
    try:
        async with get_db() as db:
            # Find user with this token
            result = await db.execute(
                text("""
                    SELECT id, username, email, full_name, roles,
                           email_verification_expires
                    FROM users 
                    WHERE email_verification_token = :token
                    AND email_verified = false
                """),
                {"token": request.token}
            )
            user_data = result.fetchone()
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired verification link"
                )
            
            # Check if token expired
            if user_data.email_verification_expires < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification link has expired. Please request a new one."
                )
            
            # Mark email as verified
            await db.execute(
                text("""
                    UPDATE users 
                    SET email_verified = true,
                        email_verification_token = NULL,
                        email_verification_expires = NULL,
                        updated_at = :now
                    WHERE id = :user_id
                """),
                {
                    "now": datetime.now(timezone.utc),
                    "user_id": user_data.id
                }
            )
            await db.commit()
            
            # Create auth token
            user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                is_active=True,
                roles=user_data.roles or ["user"]
            )
            
            access_token = create_access_token(
                data={"sub": user.username, "scopes": user.roles}
            )
            
            logger.info(f"Email verified for user: {user.email}")
            
            return AuthResponse(
                access_token=access_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed. Please try again."
        )


async def login_with_email(request: LoginRequest) -> AuthResponse:
    """
    Login with email and password.
    Requires verified email.
    """
    from sqlalchemy import text
    
    try:
        async with get_db() as db:
            # Find user
            result = await db.execute(
                text("""
                    SELECT id, username, email, hashed_password, full_name, 
                           is_active, is_locked, locked_until, email_verified,
                           failed_login_attempts, roles
                    FROM users 
                    WHERE email = :email
                """),
                {"email": request.email}
            )
            user_data = result.fetchone()
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Check if email is verified
            if not user_data.email_verified:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Please verify your email before logging in"
                )
            
            # Check if account is locked
            if user_data.is_locked:
                if user_data.locked_until and user_data.locked_until > datetime.now(timezone.utc):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Account is temporarily locked. Please try again later."
                    )
                else:
                    # Unlock account
                    await db.execute(
                        text("UPDATE users SET is_locked = false, failed_login_attempts = 0 WHERE id = :id"),
                        {"id": user_data.id}
                    )
            
            # Check if account is active
            if not user_data.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is disabled"
                )
            
            # Verify password
            if not user_data.hashed_password or not verify_password(request.password, user_data.hashed_password):
                # Increment failed attempts
                failed_attempts = (user_data.failed_login_attempts or 0) + 1
                
                # Lock account after 5 failed attempts
                if failed_attempts >= 5:
                    await db.execute(
                        text("""
                            UPDATE users 
                            SET failed_login_attempts = :attempts,
                                is_locked = true,
                                locked_until = :locked_until
                            WHERE id = :id
                        """),
                        {
                            "attempts": failed_attempts,
                            "locked_until": datetime.now(timezone.utc) + timedelta(minutes=15),
                            "id": user_data.id
                        }
                    )
                    await db.commit()
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Too many failed attempts. Account locked for 15 minutes."
                    )
                else:
                    await db.execute(
                        text("UPDATE users SET failed_login_attempts = :attempts WHERE id = :id"),
                        {"attempts": failed_attempts, "id": user_data.id}
                    )
                    await db.commit()
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Successful login - reset failed attempts and update last login
            await db.execute(
                text("""
                    UPDATE users 
                    SET failed_login_attempts = 0,
                        last_login = :now
                    WHERE id = :id
                """),
                {"now": datetime.now(timezone.utc), "id": user_data.id}
            )
            await db.commit()
            
            # Create auth token
            user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                is_active=True,
                roles=user_data.roles or ["user"]
            )
            
            access_token = create_access_token(
                data={"sub": user.username, "scopes": user.roles}
            )
            
            logger.info(f"User logged in: {user.email}")
            
            return AuthResponse(
                access_token=access_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


async def forgot_password(request: ForgotPasswordRequest) -> MessageResponse:
    """
    Request password reset email.
    Always returns success to prevent email enumeration.
    """
    from email_service import send_password_reset_email, generate_verification_token
    from sqlalchemy import text
    
    try:
        async with get_db() as db:
            # Find user
            result = await db.execute(
                text("SELECT id, full_name, email_verified FROM users WHERE email = :email"),
                {"email": request.email}
            )
            user_data = result.fetchone()
            
            # Always return success to prevent email enumeration
            if not user_data or not user_data.email_verified:
                return MessageResponse(
                    success=True,
                    message="If an account exists with this email, you will receive a password reset link."
                )
            
            # Generate reset token
            token = generate_verification_token()
            expires = datetime.now(timezone.utc) + timedelta(hours=1)
            
            await db.execute(
                text("""
                    UPDATE users 
                    SET password_reset_token = :token,
                        password_reset_expires = :expires,
                        updated_at = :now
                    WHERE id = :id
                """),
                {
                    "token": token,
                    "expires": expires,
                    "now": datetime.now(timezone.utc),
                    "id": user_data.id
                }
            )
            await db.commit()
            
            # Send reset email
            await send_password_reset_email(
                to_email=request.email,
                user_name=user_data.full_name or request.email.split("@")[0],
                reset_token=token
            )
            
            logger.info(f"Password reset requested for: {request.email}")
            
    except Exception as e:
        logger.error(f"Forgot password failed: {e}")
    
    # Always return success
    return MessageResponse(
        success=True,
        message="If an account exists with this email, you will receive a password reset link."
    )


async def reset_password(request: ResetPasswordRequest) -> MessageResponse:
    """
    Reset password using token from email.
    """
    from sqlalchemy import text
    
    try:
        async with get_db() as db:
            # Find user with this token
            result = await db.execute(
                text("""
                    SELECT id, password_reset_expires
                    FROM users 
                    WHERE password_reset_token = :token
                """),
                {"token": request.token}
            )
            user_data = result.fetchone()
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset link"
                )
            
            # Check if token expired
            if user_data.password_reset_expires < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reset link has expired. Please request a new one."
                )
            
            # Update password
            hashed_password = get_password_hash(request.new_password)
            
            await db.execute(
                text("""
                    UPDATE users 
                    SET hashed_password = :password,
                        password_reset_token = NULL,
                        password_reset_expires = NULL,
                        last_password_change = :now,
                        updated_at = :now,
                        failed_login_attempts = 0,
                        is_locked = false
                    WHERE id = :id
                """),
                {
                    "password": hashed_password,
                    "now": datetime.now(timezone.utc),
                    "id": user_data.id
                }
            )
            await db.commit()
            
            logger.info(f"Password reset for user id: {user_data.id}")
            
            return MessageResponse(
                success=True,
                message="Password reset successfully. You can now log in with your new password."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed. Please try again."
        )


# ============================================================================
# Data Isolation - User Context
# ============================================================================

async def get_current_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[int]:
    """
    Get current user ID from JWT token or Azure SWA auth header.
    Returns None for unauthenticated requests (webhook/internal calls).
    """
    from sqlalchemy import text
    
    # Check for Azure Static Web Apps auth header
    azure_principal = request.headers.get("x-ms-client-principal-id")
    if azure_principal:
        # Azure SWA auth - look up user by OAuth provider ID
        async with get_db() as db:
            result = await db.execute(
                text("SELECT id FROM users WHERE oauth_provider_id = :provider_id"),
                {"provider_id": azure_principal}
            )
            user_row = result.fetchone()
            if user_row:
                return user_row.id
        return None
    
    # Check for JWT token
    if credentials:
        try:
            token_data = verify_token(credentials.credentials)
            async with get_db() as db:
                result = await db.execute(
                    text("SELECT id FROM users WHERE username = :username"),
                    {"username": token_data.username}
                )
                user_row = result.fetchone()
                if user_row:
                    return user_row.id
        except Exception:
            pass
    
    return None


def require_user():
    """Dependency that requires authenticated user and returns user ID."""
    async def get_required_user(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> int:
        user_id = await get_current_user_id(request, credentials)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    return get_required_user