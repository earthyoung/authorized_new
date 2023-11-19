from account.exception import *
import jwt, os
from datetime import datetime


class JwtAuthenticateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 로그인 요청
        if request.method == "GET" and (
            request.path.startswith("/account/google/")
            or request.path.startswith("/account/kakao/")
        ):
            pass
        # JWT 토큰 없이 접근 가능한 요청
        elif request.method == "GET" and request.path in []:
            pass
        else:
            secret = os.environ.get("SECRET_KEY")
            # validate JWT
            token = request.META.get("HTTP_AUTHORIZATION")
            if not token:
                raise JwtNotExistException("JWT 토큰이 없습니다.")

            token = token[7:]  # 'Bearer' 제거
            user_info = jwt.decode(token, secret, algorithms=["HS256"])

            # JWT 토큰 유효한지 확인
            try:
                user_id = user_info.get("user_id")
                email = user_info.get("email")
                expire_at = user_info.get("expire_at")
            except Exception:
                raise JwtInvalidException("JWT 토큰이 유효하지 않습니다.")

            # 기간이 지났는지 확인
            expire_at = datetime.strptime(expire_at, "%Y%m%dT%H:%M:%S")
            if expire_at < datetime.now():
                raise JwtOutdatedException("JWT 유효기간이 만료되었습니다.")

        response = self.get_response(request)
        return response
