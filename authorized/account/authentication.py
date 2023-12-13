from rest_framework.authentication import SessionAuthentication
from .exception import *
import os, jwt
from datetime import datetime
from .models import User


class CustomJwtAuthentication(SessionAuthentication):
    secret = os.environ.get("SECRET_KEY")

    def authenticate(self, request):
        try:
            user = request.user
            if user and (not user.is_anonymous):
                return (user, None)
        except Exception:
            pass

        if (
            request.path.startswith("/account/google/")
            or request.path.startswith("/account/kakao/")
            or request.path.startswith("/account/health")
        ):
            return None
        # JWT 토큰 없이 접근 가능한 요청
        elif request.path in ["/account/convert/"]:
            return None
        else:
            token = request.META.get("HTTP_AUTHORIZATION")[7:]
            if not token:
                raise JwtNotExistException()

            user_info = jwt.decode(token, self.secret, algorithms=["HS256"])
            # JWT 토큰 유효한지 확인
            try:
                id = user_info.get("id")
                user_id = user_info.get("user_id")
                expire_at = user_info.get("expire_at")
            except Exception:
                raise JwtInvalidException()

            try:
                user = User.objects.get(pk=id)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                raise UserInvalidException()

            # 기간이 지났는지 확인
            expire_at = datetime.strptime(expire_at, "%Y%m%dT%H:%M:%S")
            if expire_at < datetime.now():
                raise JwtOutdatedException()

            return (user, None)
