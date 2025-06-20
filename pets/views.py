from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from groups.models import Group
from pets.models import Pet
from pets.serializers import Pet_Update_Serializer, PetSerializer
from traits.models import Trait
from rest_framework.response import Response


# Create your views here.
class PetView(APIView, PageNumberPagination):
    def get(self, request):
        trait_name = request.query_params.get("trait", None)

        pets = Pet.objects.all()

        if trait_name:
            pets = pets.filter(traits__name__iexact=trait_name.strip()).distinct()

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


class PetDetailView(APIView):
    def get(self, request, pet_id):
        try:
            pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found"}, 404)

        serializer = PetSerializer(pet)
        return Response(serializer.data, 200)       

    def delete(self, request, pet_id):
        try:
            pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found"}, 404)

        pet.delete()
        return Response({}, 204)

    def patch(self, request, pet_id):
        try:
            pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found"}, 404)

        pet_request = Pet_Update_Serializer(data=request.data)

        if pet_request.is_valid():
            if "group" in pet_request.validated_data:
                group, created = Group.objects.get_or_create(scientific_name=pet_request.validated_data["group"]["scientific_name"])
                pet.group = group
                pet.save()
                serializer = PetSerializer(pet)
                return Response(serializer.data, 200)

            elif "traits" in pet_request.validated_data:
                traits_request = pet_request.validated_data["traits"]
                trait_objects = []
                for trait_data in traits_request:
                    trait_name = trait_data["name"].lower()
                    trait, created = Trait.objects.get_or_create(name=trait_name)
                    trait_objects.append(trait)
                    pet.traits.set(trait_objects)
                    pet.save()
                serializer = PetSerializer(pet)
                return Response(serializer.data, 200)

            else:
                for keys in ["name", "age", "weight", "sex"]:
                    if keys in pet_request.data:
                        setattr(pet, keys, pet_request.data[keys])
                pet.save()
                serializer = PetSerializer(pet)
                print(pet_request.is_valid())
                return Response(serializer.data, 200)
        else:
            return Response(pet_request.errors, 400)
