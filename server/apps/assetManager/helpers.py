import jwt
from django.conf import settings


def decoded_token(request):
    token = request.headers['Authorization'].split(' ').pop()
    decoded_token = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
    return decoded_token.get('user_id')