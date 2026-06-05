from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

schema_view = get_schema_view(
   openapi.Info(
      title="Comestask API",
      default_version='v1',
      description=(
          "Comestask API.\n\n"
          "## Canlı Chat — WebSocket\n"
          "Mətn mesajları real-time WebSocket ilə gedir (Swagger yalnız REST-i göstərir):\n\n"
          "- Direct: `ws://<host>/ws/chat/direct/<user_id>/?token=<access_token>`\n"
          "- Squad: `ws://<host>/ws/chat/squad/<squad_id>/?token=<access_token>`\n\n"
          "Mesaj göndərmək (JSON): `{\"text\": \"salam\"}`. "
          "Gələn mesajlar həmin formatda serializasiya olunmuş obyekt kimi qayıdır.\n\n"
          "**Fayl** mesajları isə `POST /chat/api/...` endpoint-ləri ilə "
          "`multipart/form-data` formasında göndərilir və qoşulu olanlara WebSocket ilə canlı çatdırılır."
      ),
      terms_of_service="",
      contact=openapi.Contact(email="rzayev592@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=False,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/register/', RegisterView.as_view(), name='auth_register'),
    path('api/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("api/reset_password/request/",RequestPasswordReset.as_view(),name='reset_passwrod_request'),
    path("api/reset_password/<token>/",ResetPassword.as_view(),name="reset_password"),
    path('api/user/', GetUserVirews.as_view(), name='get_user'),
    path('api/user/<int:pk>/', DetailAndUpdateUser.as_view(),name="detail_or_update_user")
]
