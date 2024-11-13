from gondorapi.models import Address, State
from rest_framework import serializers


class AddressSerializers:
    class AddressSerializer(serializers.ModelSerializer):
        state_name = serializers.SerializerMethodField()

        class Meta:
            model = Address
            fields = ["id", "line1", "line2", "city", "state_code", "state_name", "postal_code"]
        
        def get_state_name(self,obj):
            try:
                state = State.objects.get(state_code = obj.state_code)
                return state.name
            except State.DoesNotExist:
                return None
            
        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["stateCode"] = rep.pop("state_code")
            rep["stateName"] = rep.pop("state_name")
            rep["postalCode"] = rep.pop("postal_code")
            return rep
    
    
    class AddressSimpleSerializer(serializers.ModelSerializer):
        class Meta:
            model = Address
            fields = ["line1", "line2", "city", "state_code", "postal_code"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["stateCode"] = rep.pop("state_code")
            rep["postalCode"] = rep.pop("postal_code")
            return rep