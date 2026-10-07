from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from teams.models import Team
from teams.serializers import TeamSerializer


def require_admin(request):
    return request.user.is_authenticated and request.user.role == 'admin'


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def team_list_create(request):
    if not require_admin(request):
        return Response({'error': '관리자만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        teams = Team.objects.all().order_by('name')
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = TeamSerializer(data=request.data)
    if serializer.is_valid():
        team = serializer.save()
        return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def team_detail(request, pk):
    if not require_admin(request):
        return Response({'error': '관리자만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    team = get_object_or_404(Team, pk=pk)

    if request.method == 'GET':
        return Response(TeamSerializer(team).data, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        serializer = TeamSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            team = serializer.save()
            return Response(TeamSerializer(team).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    team.delete()
    return Response({'message': '팀이 삭제되었습니다.'}, status=status.HTTP_200_OK)
