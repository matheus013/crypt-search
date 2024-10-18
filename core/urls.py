from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from core.views.compare_texts import SaveVectorView, CompareTextView
from core.views.task import TaskStatusView
from core.views.token import UserTokenListCreateView

urlpatterns = [

    path('/', include('rest_framework.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('tokens/', UserTokenListCreateView.as_view(), name='user_tokens'),
    path('save-vector/', SaveVectorView.as_view(), name='save-vector'),
    path('compare-text/', CompareTextView.as_view(), name='compare-text'),
    path('task/', TaskStatusView.as_view(), name='task'),
]
