from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import AccountVerification


@receiver(post_save, sender=User)
def create_verification(sender, instance, created, **kwargs):
    account, created_account = AccountVerification.objects.get_or_create(user=instance)
    if created_account or created:
        account.refresh_completion()
        account.save(update_fields=['completion_score', 'limits_unlocked', 'updated_at'])
