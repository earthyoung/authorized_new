class JwtNotExistException(Exception):
    def __init__(self, message="JWT 토큰이 없습니다."):
        self.message = "JWT 토큰이 없습니다."


class JwtInvalidException(Exception):
    def __init__(self, message="JWT 토큰이 유효하지 않습니다."):
        self.message = "JWT 토큰이 유효하지 않습니다."


class JwtOutdatedException(Exception):
    def __init__(self, message="JWT 유효기간이 만료되었습니다."):
        self.message = "JWT 유효기간이 만료되었습니다."


class KakaoNotExistAccessTokenException(Exception):
    def __init__(self, message="kakao access token이 주어지지 않았습니다."):
        self.message = "kakao access token이 주어지지 않았습니다."


class UserInvalidException(Exception):
    def __init__(self, message="id에 맞는 user가 존재하지 않습니다."):
        self.message = "id에 맞는 user가 존재하지 않습니다."


class RefreshTokenInvalidException(Exception):
    def __init__(self, message="유효한 refresh token이 아닙니다."):
        self.message = "유효한 refresh token이 아닙니다."
