from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from groups.models import Group
from pets.models import Pet
from pets.serializers import PetSerializer
from traits.models import Trait
from rest_framework.response import Response


# Create your views here.
class PetView(APIView, PageNumberPagination):
    def get(self, request):
        pets = Pet.objects.all()
        result_page = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)

    def post(self, request):
        serializer_data = PetSerializer(data=request.data)

        if serializer_data.is_valid():
            group_request = serializer_data.validated_data["group"]["scientific_name"]
            group, created = Group.objects.get_or_create(scientific_name=group_request)

            traits_request = serializer_data.validated_data["traits"]
            trait_objects = []
            for trait_data in traits_request:
                trait_name = trait_data["name"].lower()
                trait, created = Trait.objects.get_or_create(name=trait_name)
                trait_objects.append(trait)

            pet = Pet.objects.create(
                name=serializer_data.validated_data["name"],
                age=serializer_data.validated_data["age"],
                weight=serializer_data.validated_data["weight"],
                sex=serializer_data.validated_data["sex"],
                group=group
            )
            pet.traits.set(trait_objects)

            return Response(PetSerializer(pet).data, 201)

        else:
            return Response(serializer_data.errors, 400)
