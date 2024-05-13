from django.shortcuts import render
from rest_framework import viewsets
from .models import CaseHistory
from .serializers import CaseHistorySerializer

class CaseHistoryViewSet(viewsets.ModelViewSet):
    queryset = CaseHistory.objects.all()
    serializer_class = CaseHistorySerializer
