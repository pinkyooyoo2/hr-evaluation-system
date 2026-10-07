from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer


def require_admin(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return False
    return True


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': '사번과 비밀번호를 입력해 주세요.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {'error': '잘못된 사번 또는 비밀번호입니다.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    login(request, user)
    return Response(
        {
            'message': '로그인 성공',
            'user': UserSerializer(user).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': '로그아웃 되었습니다.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response({'user': UserSerializer(request.user).data}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_user_list_create(request):
    if not require_admin(request):
        return Response({'error': '관리자만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        users = User.objects.all().order_by('username')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        if not user.password or user.password == '':
            user.set_password(f"{user.username}123!")
            user.save(update_fields=['password'])
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_user_detail(request, pk):
    if not require_admin(request):
        return Response({'error': '관리자만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(User, pk=pk)

    if request.method == 'GET':
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            if request.data.get('password'):
                updated_user.set_password(request.data['password'])
                updated_user.save(update_fields=['password'])
            return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user.delete()
    return Response({'message': '사용자가 삭제되었습니다.'}, status=status.HTTP_200_OK)
