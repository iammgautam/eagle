from django.shortcuts import render
from rest_framework import viewsets
from .models import Argument, BriefArgument
from .serializers import ArgumentSerializer, BriefArgumentSerializer

class ArgumentViewSet(viewsets.ModelViewSet):
    queryset = Argument.objects.all()
    serializer_class = ArgumentSerializer

class BriefArgumentViewSet(viewsets.ModelViewSet):
    queryset = BriefArgument.objects.all()
    serializer_class = BriefArgumentSerializer

