# core/middleware/audit.py
import time
from django.utils.deprecation import MiddlewareMixin
from core.models.api_log import APILog

class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Captura o tempo de início da requisição
        request.start_time = time.time()

    def process_response(self, request, response):
        # Registrar apenas requisições de usuários autenticados e API (se desejado)
        if request.user.is_authenticated:
            # Calcula o tempo de processamento
            processing_time = time.time() - getattr(request, 'start_time', time.time())

            # Criar o log com o tempo de processamento
            APILog.objects.create(
                user=request.user,
                method=request.method,
                path=request.path,
                action=self.get_action_description(request),
                status_code=response.status_code,
                response_data=response.content.decode('utf-8') if hasattr(response, 'content') else '',
                processing_time=processing_time  # Salva o tempo de processamento
            )
        return response

    def get_action_description(self, request):
        # Personalizar a ação com base na rota ou outras regras
        if request.method == "GET":
            return f"Visualizou o recurso {request.path}"
        elif request.method == "POST":
            return f"Criou um novo recurso em {request.path}"
        elif request.method == "PUT":
            return f"Atualizou o recurso {request.path}"
        elif request.method == "DELETE":
            return f"Removeu o recurso {request.path}"
        return f"Ação indefinida {request.method} {request.path}"
