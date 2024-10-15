from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from .address_type import AddressType
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    updated_timestamp = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def primary_address(self):
        try:
            primary_address_type = AddressType.objects.get(name="Primary Address")
            user_address = self.active_addresses.get(address_type=primary_address_type)

            if user_address:
                return user_address.address
            
            return None
        
        except:
            return None

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
