from gondorapi.models import Address
from rest_framework.response import Response
from rest_framework.decorators import action 
from rest_framework import viewsets, status
from gondorapi.serializers import AddressSerializers
        
    
class AddressViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="my")
    def get_user_addresses(self,request):
        user = request.user
        addresses = Address.objects.filter(user= user)
        serializer = AddressSerializers.AddressSerializer(addresses, many=True)
        return Response(serializer.data)
    

  
    def destroy(self, request, pk=None):
        try:
            address = Address.objects.get(pk=pk)
            if address.user == request.user:
                address.delete()
                return Response({"message": "Address deleted"}, status=status.HTTP_204_NO_CONTENT)

            return Response({"error": "You are not authorized to delete this address."}, status=status.HTTP_401_UNAUTHORIZED)    

        except Address.DoesNotExist:
            return Response({"error":"Address not found!"}, status=status.HTTP_404_NOT_FOUND)
        