from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


# Task 1: Send welcome email when user registers - using .delay()
@shared_task
def send_welcome_email(user_email, user_first_name='User'):
    """
    Send welcome email to newly registered user.
    Called with: send_welcome_email.delay(user_email, user_first_name)
    """
    subject = 'Welcome to Our Shop!'
    message = f'''
    Hello {user_first_name}!
    
    Thank you for registering on our platform. We're excited to have you on board!
    
    Please confirm your email to activate your account.
    
    Best regards,
    Shop Team
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to {user_email}")
        return f"Email sent to {user_email}"
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user_email}: {str(e)}")
        return f"Error: {str(e)}"


# Task 2: Clean unconfirmed users - scheduled task (crontab)
@shared_task
def clean_unconfirmed_users():
    """
    Delete users who haven't confirmed their email in more than 7 days.
    Scheduled to run every day at 2:00 AM.
    """
    days_ago = timezone.now() - timedelta(days=7)
    unconfirmed_users = User.objects.filter(is_active=False, date_joined__lt=days_ago)
    count = unconfirmed_users.count()
    
    try:
        unconfirmed_users.delete()
        logger.info(f"Deleted {count} unconfirmed users")
        return f"Deleted {count} unconfirmed users"
    except Exception as e:
        logger.error(f"Failed to clean unconfirmed users: {str(e)}")
        return f"Error: {str(e)}"


# Task 3: Send activity report via SMTP - scheduled task
@shared_task
def send_activity_report():
    """
    Send weekly activity report to admin with user statistics.
    Scheduled to run every Monday at 10:00 AM.
    """
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    new_users_this_week = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    subject = 'Weekly User Activity Report'
    message = f'''
    Weekly Activity Report
    
    Total Users: {total_users}
    Active Users: {active_users}
    Inactive Users: {inactive_users}
    New Users This Week: {new_users_this_week}
    
    Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['admin@shop.com'],  # Send to admin
            fail_silently=False,
        )
        logger.info("Activity report sent to admin")
        return "Activity report sent successfully"
    except Exception as e:
        logger.error(f"Failed to send activity report: {str(e)}")
        return f"Error: {str(e)}"


# Bonus Task 4: Send confirmation code via email with SMTP
@shared_task
def send_confirmation_code(user_email, confirmation_code):
    """
    Send confirmation code to user email.
    Can be called with: send_confirmation_code.delay(email, code)
    """
    subject = 'Email Confirmation Code'
    message = f'''
    Hello,
    
    Your email confirmation code is: {confirmation_code}
    
    This code will expire in 5 minutes.
    
    If you didn't request this code, please ignore this email.
    
    Best regards,
    Shop Team
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Confirmation code sent to {user_email}")
        return f"Confirmation code sent to {user_email}"
    except Exception as e:
        logger.error(f"Failed to send confirmation code to {user_email}: {str(e)}")
        return f"Error: {str(e)}"


# Bonus Task 5: Delete inactive products after certain time - scheduled task
@shared_task
def delete_old_unreviewed_products():
    """
    Delete products that have no reviews and were created more than 30 days ago.
    Scheduled to run daily.
    """
    from product.models import Product
    
    days_ago = timezone.now() - timedelta(days=30)
    old_products = Product.objects.filter(
        reviews__isnull=True,
        created_at__lt=days_ago
    ).distinct()
    
    count = old_products.count()
    
    try:
        old_products.delete()
        logger.info(f"Deleted {count} old unreviewed products")
        return f"Deleted {count} old unreviewed products"
    except Exception as e:
        logger.error(f"Failed to delete old products: {str(e)}")
        return f"Error: {str(e)}"


# Bonus Task 6: Generate daily statistics
@shared_task
def generate_daily_stats():
    """
    Generate and store daily statistics about users and products.
    Could be scheduled to run every day at midnight.
    """
    from product.models import Product, Review
    
    stats = {
        'date': timezone.now().date(),
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_products': Product.objects.count(),
        'total_reviews': Review.objects.count(),
        'avg_rating': Review.objects.values('stars').count() if Review.objects.count() > 0 else 0,
    }
    
    logger.info(f"Daily stats generated: {stats}")
    return stats
