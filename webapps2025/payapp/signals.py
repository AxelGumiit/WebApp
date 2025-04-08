
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    User = get_user_model()
    if not User.objects.filter(username="admin1").exists():
        User.objects.create_superuser(
            username="admin1",
            email="admin1@admin.com",
            password="admin1",  # You can set a random password or specify one
        )
        print("Admin user 'admin1' created successfully.")