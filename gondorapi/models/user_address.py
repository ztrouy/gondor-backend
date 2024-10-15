from django.db import models
from .user import User
from .address import Address
from .address_type import AddressType
import uuid

class UserAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="active_addresses")
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    address_type = models.ForeignKey(AddressType, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "address_type"], name="unique_user_address_type")
        ]
