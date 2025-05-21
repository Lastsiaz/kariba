from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AnalyticsQuery, AnalyticsResult

@receiver(post_save, sender=AnalyticsResult)
def update_query_last_run(sender, instance, created, **kwargs):
    """Update the last_run timestamp of the associated query when a result is created."""
    if created:
        instance.query.last_run = instance.created_at
        instance.query.save(update_fields=['last_run'])

@receiver(post_delete, sender=AnalyticsQuery)
def cleanup_query_results(sender, instance, **kwargs):
    """Clean up all results associated with a deleted query."""
    AnalyticsResult.objects.filter(query=instance).delete() 