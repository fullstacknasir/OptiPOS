from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import User
from user.serializer import UserSerializer, CreatePasswordSerializer


# Create your views here.
@extend_schema(tags=['User'])
class CreateUserAPIView(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin, ):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = None

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        return []

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response({}, status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(username=serializer.validated_data['username'])
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        link = f"{protocol}://{host}/v1/api/auth/set-password/{uid}/{token}/"
        return Response({'link': link}, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Auth'])
class SetPasswordAPIView(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin):
    serializer_class = CreatePasswordSerializer
    queryset = User.objects.all()

    permission_classes = []
    authentication_classes = []
    pagination_class = None

    def list(self, request, *args, **kwargs):
        try:
            # Decode the user ID
            uid = urlsafe_base64_decode(self.kwargs['uid']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate the token
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, self.kwargs['token']):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({})

    def create(self, request, *args, **kwargs):
        try:
            # Decode the user ID
            uid = urlsafe_base64_decode(self.kwargs['uid']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, self.kwargs['token']):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['password'] != serializer.validated_data['password2']:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({'detail': 'Password saved successfully'}, status=status.HTTP_200_OK)
