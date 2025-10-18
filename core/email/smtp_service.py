"""
SMTP email service for sending emails.
"""
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context, Template

logger = logging.getLogger(__name__)

class SMTPEmailService:
    """SMTP email service for sending emails."""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'EMAIL_PORT', 587)
        self.smtp_username = getattr(settings, 'EMAIL_HOST_USER', '')
        self.smtp_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        self.use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
        self.use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send email via SMTP.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            from_email: Sender email address
            reply_to: Reply-to email address
            attachments: List of attachment dictionaries with 'filename' and 'content'
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or self.from_email
            msg['To'] = ', '.join(to_emails)
            
            if reply_to:
                msg['Reply-To'] = reply_to
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)
            
            # Connect to SMTP server and send email
            context = ssl.create_default_context()
            
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls(context=context)
            
            # Login and send email
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            logger.info("Email sent successfully to %s", ', '.join(to_emails))
            return True
            
        except Exception as e:
            logger.error("Failed to send email: %s", e)
            return False
    
    def send_organization_invite(
        self,
        invitee_email: str,
        organization_name: str,
        inviter_name: str,
        invite_url: str,
        expires_at: Optional[str] = None
    ) -> bool:
        """
        Send organization invitation email.
        
        Args:
            invitee_email: Email address of the person being invited
            organization_name: Name of the organization
            inviter_name: Name of the person sending the invite
            invite_url: URL to accept the invitation
            expires_at: Expiration date of the invitation
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"You're invited to join {organization_name}"
            
            # Render HTML template
            html_content = self._render_invite_template(
                invitee_email=invitee_email,
                organization_name=organization_name,
                inviter_name=inviter_name,
                invite_url=invite_url,
                expires_at=expires_at
            )
            
            # Create plain text version
            text_content = self._create_text_invite(
                organization_name=organization_name,
                inviter_name=inviter_name,
                invite_url=invite_url,
                expires_at=expires_at
            )
            
            return self.send_email(
                to_emails=[invitee_email],
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error("Failed to send organization invite: %s", e)
            return False
    
    def _render_invite_template(
        self,
        invitee_email: str,
        organization_name: str,
        inviter_name: str,
        invite_url: str,
        expires_at: Optional[str] = None
    ) -> str:
        """Render HTML email template for organization invite."""
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Organization Invitation</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }
                .container {
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 40px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .logo {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2563eb;
                    margin-bottom: 10px;
                }
                .title {
                    font-size: 28px;
                    font-weight: bold;
                    color: #1f2937;
                    margin-bottom: 20px;
                }
                .content {
                    margin-bottom: 30px;
                }
                .invite-button {
                    display: inline-block;
                    background-color: #2563eb;
                    color: #ffffff;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 16px;
                    margin: 20px 0;
                }
                .invite-button:hover {
                    background-color: #1d4ed8;
                }
                .details {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 6px;
                    margin: 20px 0;
                }
                .footer {
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    color: #6b7280;
                    font-size: 14px;
                }
                .expiry {
                    color: #dc2626;
                    font-weight: 600;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🔗 ShortURL</div>
                    <h1 class="title">You're Invited!</h1>
                </div>
                
                <div class="content">
                    <p>Hello!</p>
                    
                    <p><strong>{{ inviter_name }}</strong> has invited you to join the organization <strong>{{ organization_name }}</strong> on ShortURL.</p>
                    
                    <p>ShortURL is a powerful URL shortening service that helps organizations manage and track their links efficiently.</p>
                    
                    <div class="details">
                        <h3>What you'll get:</h3>
                        <ul>
                            <li>Create and manage short URLs</li>
                            <li>Track click analytics</li>
                            <li>Organize URLs by namespaces</li>
                            <li>Collaborate with team members</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{{ invite_url }}" class="invite-button">Accept Invitation</a>
                    </div>
                    
                    {% if expires_at %}
                    <p class="expiry">⏰ This invitation expires on {{ expires_at }}</p>
                    {% endif %}
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #2563eb;">{{ invite_url }}</p>
                </div>
                
                <div class="footer">
                    <p>This invitation was sent to {{ invitee_email }}</p>
                    <p>If you didn't expect this invitation, you can safely ignore this email.</p>
                    <p>&copy; 2024 ShortURL. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Simple template rendering
        template = Template(html_template)
        context = {
            'invitee_email': invitee_email,
            'organization_name': organization_name,
            'inviter_name': inviter_name,
            'invite_url': invite_url,
            'expires_at': expires_at
        }
        
        return template.render(Context(context))
    
    def _create_text_invite(
        self,
        organization_name: str,
        inviter_name: str,
        invite_url: str,
        expires_at: Optional[str] = None
    ) -> str:
        """Create plain text version of the invite email."""
        
        text_content = f"""
You're Invited to Join {organization_name}!

Hello!

{inviter_name} has invited you to join the organization {organization_name} on ShortURL.

ShortURL is a powerful URL shortening service that helps organizations manage and track their links efficiently.

What you'll get:
- Create and manage short URLs
- Track click analytics  
- Organize URLs by namespaces
- Collaborate with team members

To accept this invitation, click the link below:
{invite_url}

"""
        
        if expires_at:
            text_content += f"This invitation expires on {expires_at}\n\n"
        
        text_content += f"""
If the link doesn't work, you can copy and paste it into your browser.

This invitation was sent to you. If you didn't expect this invitation, you can safely ignore this email.

© 2024 ShortURL. All rights reserved.
"""
        
        return text_content
