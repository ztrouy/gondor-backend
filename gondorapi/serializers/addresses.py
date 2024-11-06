from gondorapi.models import Address
from rest_framework import serializers


class AddressSerializers:
    class AddressSerializer(serializers.ModelSerializer):
        class Meta:
            model = Address
            fields = ["line1", "line2", "city", "state_code", "postal_code"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["stateCode"] = rep.pop("state_code")
            rep["postalCode"] = rep.pop("postal_code")
            return rep