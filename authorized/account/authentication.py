from rest_framework.authentication import SessionAuthentication
from .exception import *
import os, jwt
from datetime import datetime
from .models import User


class CustomJwtAuthentication(SessionAuthentication):
    secret = os.environ.get("SECRET_KEY")
    path_starts_with = ["/account/google/", "/account/kakao/", "/account/health/"]
    path_exact = ["/account/convert/"]

    def authenticate(self, request):
        try:
            user = request.user
            if user and (not user.is_anonymous):
                return (user, None)
        except Exception:
            pass

        for path in self.path_starts_with:
            if request.path.starswith(path):
                return None
        # JWT 토큰 없이 접근 가능한 요청
        if request.path in self.path_exact:
            return None
        else:
            token = request.META.get("HTTP_AUTHORIZATION")
            if not token:
                raise JwtNotExistException()
            token = token[7:]

            user_info = jwt.decode(token, self.secret, algorithms=["HS256"])
            # JWT 토큰 유효한지 확인
            try:
                id = user_info.get("id")
                expire_at = user_info.get("expire_at")
                email = user_info.get("email")
            except Exception:
                raise JwtInvalidException()

            try:
                user = User.objects.get(pk=id)
            except User.MultipleObjectsReturned:
                raise UserInvalidException()
            except User.DoesNotExist:
                pass

            # 기간이 지났는지 확인
            expire_at = datetime.strptime(expire_at, "%Y%m%dT%H:%M:%S")
            if expire_at < datetime.now():
                raise JwtOutdatedException()

            return (user, None)
