from gondorapi.models import Address, State
from rest_framework.response import Response
from rest_framework.decorators import action 
from rest_framework import viewsets, serializers, status
import uuid

class AddressSerializer(serializers.ModelSerializer):
    state_name = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ["id","line1","line2","city","state_code", "state_name","postal_code"]
    
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
        
    
class AddressViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="my")
    def get_user_addresses(self,request):
        user = request.user
        addresses = Address.objects.filter(user= user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)
    

  
    def destroy(self,request, pk=None):
        user = request.user
        
        try:
            address = Address.objects.get(pk=pk)
            if address.user == request.user:
                address.delete()
                return Response({"message": "Address deleted"}, status=status.HTTP_204_NO_CONTENT)

            return Response({"error": "You are not authorized to delete this address."},status=status.HTTP_401_UNAUTHORIZED)    

        except Address.DoesNotExist:
            return Response({"error":"Address not found!"}, status=status.HTTP_404_NOT_FOUND)
        

