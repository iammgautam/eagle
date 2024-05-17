from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import CaseHistory
from .serializers import CaseHistorySerializer

class CaseHistoryViewSet(viewsets.ModelViewSet):
    queryset = CaseHistory.objects.all()
    serializer_class = CaseHistorySerializer

    @action(methods=['POST', 'PUT'], detail=False)
    def create_or_update(self, request):
        id = request.data.get('id')
        if request.method == 'PUT' and id:
            case_history = self.get_object(id)
            serializer = self.serializer_class(case_history, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'POST':
            serializer = CaseHistorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid request method or missing ID'}, status=status.HTTP_400_BAD_REQUEST)