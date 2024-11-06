from gondorapi.models import State
from rest_framework import serializers


class StateSerializers:
    class StateSerializer(serializers.ModelSerializer):
        class Meta:
            model = State
            fields = ["state_code", "name"]
        
        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["stateCode"] = rep.pop("state_code")
            return rep