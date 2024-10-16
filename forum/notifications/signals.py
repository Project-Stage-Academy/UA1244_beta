from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Project, Startup #InvestorProjectSubscription,
from .tasks import create_notification_task

@receiver(post_save, sender=Project)
def create_project_update_notification(sender, instance, created, **kwargs):
    if created:
        create_notification_task.delay(
            'project', 
            instance.id, 
            'project_created', 
            f"Project '{instance.name}' has been created.",
            initiator='system'
        )
    else:
        create_notification_task.delay(
            'project', 
            instance.id, 
            'project_profile_change', 
            f"Project '{instance.name}' has been updated.",
            initiator='project'
        )

@receiver(post_delete, sender=Project)
def create_project_deleted_notification(sender, instance, **kwargs):
    create_notification_task.delay(
        'project', 
        instance.id, 
        'project_deleted', 
        f"Project '{instance.name}' has been deleted.",
        initiator='system'
    )

# @receiver(post_save, sender=InvestorProjectSubscription)
# def create_investor_follow_notification(sender, instance, created, **kwargs):
#     if created:
#         create_notification_task.delay(
#             'investor', 
#             instance.investor.id, 
#             'project_follow', 
#             f"Investor '{instance.investor.name}' has followed project '{instance.project.name}'.",
#             initiator='investor'
#         )

@receiver(post_save, sender=Startup)
def create_startup_profile_update_notification(sender, instance, created, **kwargs):
    if not created:
        create_notification_task.delay(
            'startup', 
            instance.id, 
            'startup_profile_update', 
            f"Startup '{instance.name}' has updated its profile.",
            initiator='startup'
        )