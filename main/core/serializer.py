from rest_framework import serializers

class SerializerClass(serializers.Serializer):
    user_name = serializers.CharField()
    domain = serializers.CharField()
    