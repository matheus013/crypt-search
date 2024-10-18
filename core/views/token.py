from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from core.models.token import UserToken
from core.serializers.token import UserTokenSerializer


class UserTokenListCreateView(generics.ListCreateAPIView):
    serializer_class = UserTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
