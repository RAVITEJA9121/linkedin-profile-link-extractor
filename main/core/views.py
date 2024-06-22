from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import SerializerClass
from .linked_in import run
from rest_framework import validators
from googlesearch import search
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


class LinkedInView(APIView):
    def post(self, request):
        serializer_class = SerializerClass(data=request.data)
        if serializer_class.is_valid():
            data = request.data
            query = f"linkedin profile of {data["user_name"]} who is working in {data["domain"]}"
            links = []
            try:
                response = search(query)
                for result in response:
                    links.append(result)
                return Response(data=links[0], status=status.HTTP_200_OK)
            except:
                response = search(query)
                for result in response:
                    links.append(result)
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return validators.ValidationError("Check the fields and their values", 400)