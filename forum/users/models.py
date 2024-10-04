from django.core.validators import EmailValidator
from django.db import models
import uuid

# Create your models here.
class Role(models.Model):
    role_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    role_name = models.CharField(max_length=50, null=False, unique=True)

class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_name = models.CharField(max_length=100, null=False, unique=True)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True, null=False, max_length=50, validators=[EmailValidator()])
    password = models.CharField(max_length=50)
    user_phone = models.CharField(max_length=15)
    roles = models.ManyToManyField(Role)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)






