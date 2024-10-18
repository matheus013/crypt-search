from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.tasks import save_encrypted_vectors_task, compare_with_existing_vectors_task


class SaveVectorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        texts = request.data.get("text")

        if not texts:
            return Response({"error": "'text' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(texts, str):
            texts = [texts]

        task = save_encrypted_vectors_task.delay(texts, request.user.id)

        return Response({"message": "Tarefa de salvar vetores iniciada.", "task_id": task.id},
                        status=status.HTTP_202_ACCEPTED)


class CompareTextView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        text = request.data.get("text")

        if not text:
            return Response({"error": "'text' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        task = compare_with_existing_vectors_task.delay(text, request.user.id)

        return Response({"message": "Tarefa de comparação de texto iniciada.", "task_id": task.id},
                        status=status.HTTP_202_ACCEPTED)
