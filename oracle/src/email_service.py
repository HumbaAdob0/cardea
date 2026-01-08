"""
Email Service for Cardea Oracle
Handles email verification, password reset, and security notifications
Uses Azure Communication Services in production, SMTP fallback for dev
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
import smtplib
import os

from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

# Email configuration from environment
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@cardea.security")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Cardea Security")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

# Azure Communication Services (production)
AZURE_COMM_CONNECTION_STRING = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING", "")

# App URLs
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5173")


class EmailTemplate(BaseModel):
    """Email template with subject and body"""
    subject: str
    html_body: str
    text_body: str


def generate_verification_token() -> str:
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)


def get_verification_email_template(
    user_name: str,
    verification_url: str
) -> EmailTemplate:
    """Generate email verification template"""
    subject = "Verify your Cardea Security account"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify your email</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; padding: 40px; border: 1px solid #334155;">
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-flex; align-items: center; gap: 8px;">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="2">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                    <span style="font-size: 24px; font-weight: bold; color: #f1f5f9;">CARDEA</span>
                </div>
            </div>
            
            <h1 style="color: #f1f5f9; font-size: 24px; margin-bottom: 16px;">Welcome to Cardea, {user_name}! 👋</h1>
            
            <p style="color: #94a3b8; font-size: 16px; line-height: 1.6; margin-bottom: 24px;">
                Thanks for signing up! Please verify your email address to get started with AI-powered network security.
            </p>
            
            <div style="text-align: center; margin: 32px 0;">
                <a href="{verification_url}" style="display: inline-block; background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                    Verify Email Address
                </a>
            </div>
            
            <p style="color: #64748b; font-size: 14px; margin-top: 24px;">
                This link expires in 24 hours. If you didn't create a Cardea account, you can safely ignore this email.
            </p>
            
            <p style="color: #64748b; font-size: 14px;">
                Or copy this link: <span style="color: #22d3ee; word-break: break-all;">{verification_url}</span>
            </p>
            
            <hr style="border: none; border-top: 1px solid #334155; margin: 32px 0;">
            
            <p style="color: #475569; font-size: 12px; text-align: center;">
                © 2026 Cardea Security. Protecting networks with AI.
            </p>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Welcome to Cardea, {user_name}!
    
    Thanks for signing up! Please verify your email address to get started.
    
    Click this link to verify: {verification_url}
    
    This link expires in 24 hours.
    
    If you didn't create a Cardea account, you can safely ignore this email.
    
    - Cardea Security Team
    """
    
    return EmailTemplate(subject=subject, html_body=html_body, text_body=text_body)


def get_password_reset_email_template(
    user_name: str,
    reset_url: str
) -> EmailTemplate:
    """Generate password reset email template"""
    subject = "Reset your Cardea Security password"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset your password</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; padding: 40px; border: 1px solid #334155;">
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-flex; align-items: center; gap: 8px;">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="2">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                    <span style="font-size: 24px; font-weight: bold; color: #f1f5f9;">CARDEA</span>
                </div>
            </div>
            
            <h1 style="color: #f1f5f9; font-size: 24px; margin-bottom: 16px;">Password Reset Request</h1>
            
            <p style="color: #94a3b8; font-size: 16px; line-height: 1.6; margin-bottom: 24px;">
                Hi {user_name}, we received a request to reset your password. Click the button below to create a new password.
            </p>
            
            <div style="text-align: center; margin: 32px 0;">
                <a href="{reset_url}" style="display: inline-block; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                    Reset Password
                </a>
            </div>
            
            <p style="color: #64748b; font-size: 14px; margin-top: 24px;">
                This link expires in 1 hour. If you didn't request a password reset, please ignore this email or contact support if you're concerned.
            </p>
            
            <hr style="border: none; border-top: 1px solid #334155; margin: 32px 0;">
            
            <p style="color: #475569; font-size: 12px; text-align: center;">
                © 2026 Cardea Security. Protecting networks with AI.
            </p>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Password Reset Request
    
    Hi {user_name}, we received a request to reset your password.
    
    Click this link to reset: {reset_url}
    
    This link expires in 1 hour.
    
    If you didn't request this, please ignore this email.
    
    - Cardea Security Team
    """
    
    return EmailTemplate(subject=subject, html_body=html_body, text_body=text_body)


def get_security_alert_email_template(
    user_name: str,
    alert_type: str,
    alert_details: str,
    dashboard_url: str
) -> EmailTemplate:
    """Generate security alert notification email"""
    subject = f"🚨 Security Alert: {alert_type}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Security Alert</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; padding: 40px; border: 1px solid #dc2626;">
            <div style="text-align: center; margin-bottom: 30px;">
                <span style="font-size: 48px;">🚨</span>
                <h1 style="color: #fca5a5; font-size: 24px; margin: 16px 0 0 0;">Security Alert Detected</h1>
            </div>
            
            <p style="color: #94a3b8; font-size: 16px; line-height: 1.6; margin-bottom: 24px;">
                Hi {user_name}, Cardea has detected a potential security issue on your network.
            </p>
            
            <div style="background-color: #7f1d1d20; border: 1px solid #7f1d1d; border-radius: 8px; padding: 16px; margin-bottom: 24px;">
                <h3 style="color: #fca5a5; margin: 0 0 8px 0;">{alert_type}</h3>
                <p style="color: #94a3b8; margin: 0;">{alert_details}</p>
            </div>
            
            <div style="text-align: center; margin: 32px 0;">
                <a href="{dashboard_url}" style="display: inline-block; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                    View in Dashboard
                </a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #334155; margin: 32px 0;">
            
            <p style="color: #475569; font-size: 12px; text-align: center;">
                © 2026 Cardea Security. Protecting networks with AI.
            </p>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    🚨 Security Alert Detected
    
    Hi {user_name}, Cardea has detected a potential security issue.
    
    Alert: {alert_type}
    Details: {alert_details}
    
    View in dashboard: {dashboard_url}
    
    - Cardea Security Team
    """
    
    return EmailTemplate(subject=subject, html_body=html_body, text_body=text_body)


async def send_email_smtp(
    to_email: str,
    template: EmailTemplate
) -> bool:
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = template.subject
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        
        # Attach both plain text and HTML
        text_part = MIMEText(template.text_body, 'plain', 'utf-8')
        html_part = MIMEText(template.html_body, 'html', 'utf-8')
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Connect and send
        if SMTP_USE_TLS:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        
        if SMTP_USER and SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
        
        server.sendmail(SMTP_FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


async def send_email_azure(
    to_email: str,
    template: EmailTemplate
) -> bool:
    """Send email using Azure Communication Services"""
    try:
        # Lazy import to avoid dependency issues
        from azure.communication.email import EmailClient
        
        client = EmailClient.from_connection_string(AZURE_COMM_CONNECTION_STRING)
        
        message = {
            "senderAddress": SMTP_FROM_EMAIL,
            "recipients": {
                "to": [{"address": to_email}]
            },
            "content": {
                "subject": template.subject,
                "plainText": template.text_body,
                "html": template.html_body
            }
        }
        
        poller = client.begin_send(message)
        result = poller.result()
        
        logger.info(f"Email sent via Azure to {to_email}, message_id: {result.message_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email via Azure to {to_email}: {e}")
        return False


async def send_email(
    to_email: str,
    template: EmailTemplate
) -> bool:
    """Send email using configured provider"""
    # Use Azure in production, SMTP in development
    if AZURE_COMM_CONNECTION_STRING:
        return await send_email_azure(to_email, template)
    else:
        return await send_email_smtp(to_email, template)


async def send_verification_email(
    to_email: str,
    user_name: str,
    verification_token: str
) -> bool:
    """Send email verification link"""
    verification_url = f"{APP_BASE_URL}/verify-email?token={verification_token}"
    template = get_verification_email_template(user_name, verification_url)
    return await send_email(to_email, template)


async def send_password_reset_email(
    to_email: str,
    user_name: str,
    reset_token: str
) -> bool:
    """Send password reset link"""
    reset_url = f"{APP_BASE_URL}/reset-password?token={reset_token}"
    template = get_password_reset_email_template(user_name, reset_url)
    return await send_email(to_email, template)


async def send_security_alert_email(
    to_email: str,
    user_name: str,
    alert_type: str,
    alert_details: str
) -> bool:
    """Send security alert notification"""
    dashboard_url = f"{APP_BASE_URL}/dashboard"
    template = get_security_alert_email_template(user_name, alert_type, alert_details, dashboard_url)
    return await send_email(to_email, template)
