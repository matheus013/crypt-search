from celery.result import AsyncResult
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

class TaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        task_id = request.data.get('task_id')
        task_result = AsyncResult(task_id)
        result = {
            'task_id': task_id,
            'status': task_result.status,
            'result': task_result.result
        }
        return Response(result)
