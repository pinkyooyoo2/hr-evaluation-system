import csv
import io

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from evaluations.models import EvaluationItem, EvaluationResponse
from evaluations.serializers import EvaluationItemSerializer, EvaluationResponseSerializer
from teams.models import Team
from users.models import User


def require_admin(request):
    return request.user.is_authenticated and request.user.role == 'admin'


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def evaluation_item_list_create(request):
    if not require_admin(request):
        return Response({'error': '관리자만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        items = EvaluationItem.objects.all().order_by('id')
        serializer = EvaluationItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    data = request.data
    if isinstance(data, list):
        if not data:
            return Response({'weight': '최소 1개 이상의 평가 항목이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(int(item.get('weight', 0)) for item in data)
        if total != 100:
            return Response({'weight': '평가 항목 가중치 합계는 100이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        created_items = []
        for item in data:
            serializer = EvaluationItemSerializer(data=item)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            created_items.append(EvaluationItem.objects.create(**serializer.validated_data))

        return Response(EvaluationItemSerializer(created_items, many=True).data, status=status.HTTP_201_CREATED)

    serializer = EvaluationItemSerializer(data=data)
    if serializer.is_valid():
        item = serializer.save()
        return Response(EvaluationItemSerializer(item).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def evaluation_item_detail(request, pk):
    if not require_admin(request):
        return Response({'error': '관리자만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    item = get_object_or_404(EvaluationItem, pk=pk)

    if request.method == 'GET':
        return Response(EvaluationItemSerializer(item).data, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        serializer = EvaluationItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            updated_item = serializer.save()
            return Response(EvaluationItemSerializer(updated_item).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    item.delete()
    return Response({'message': '평가 항목이 삭제되었습니다.'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def evaluation_response_list_create(request):
    if request.user.role != 'manager':
        return Response({'error': '매니저만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        responses = EvaluationResponse.objects.filter(manager=request.user).order_by('employee__username')
        serializer = EvaluationResponseSerializer(responses, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    employee_id = request.data.get('employee')
    if employee_id is None:
        return Response({'employee': '평가 대상 직원을 선택해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)

    employee = get_object_or_404(User, pk=employee_id)
    if not employee.team or employee.team.manager_id != request.user.id:
        return Response({'employee': '본인 팀 직원만 평가할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    existing_response = EvaluationResponse.objects.filter(employee=employee, manager=request.user, team=employee.team).first()
    if existing_response and existing_response.is_submitted:
        return Response({'detail': '제출된 평가는 수정할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = EvaluationResponseSerializer(
        existing_response,
        data=request.data,
        context={'request': request},
        partial=True,
    )

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    response = serializer.save()
    response.manager = request.user
    response.team = employee.team
    response.save(update_fields=['manager', 'team', 'score_values', 'temporary_save', 'is_submitted', 'submitted_at', 'progress'])
    if response.is_submitted:
        response.submitted_at = timezone.now()
        response.save(update_fields=['submitted_at'])

    return Response(EvaluationResponseSerializer(response, context={'request': request}).data, status=status.HTTP_201_CREATED if not existing_response else status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evaluation_response_detail(request, pk):
    if request.user.role != 'manager':
        return Response({'error': '매니저만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    response = get_object_or_404(EvaluationResponse, pk=pk)
    if response.manager_id != request.user.id:
        return Response({'error': '본인 평가만 확인할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = EvaluationResponseSerializer(response, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


def calculate_personal_score(score_values):
    items = list(EvaluationItem.objects.all().order_by('id'))
    if not items:
        return 0

    total = 0.0
    for item in items:
        raw_value = score_values.get(str(item.id))
        if raw_value is None:
            raw_value = score_values.get(item.id)
        if raw_value is None:
            continue
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            continue
        if 1 <= value <= 5:
            total += (value / 5) * item.weight
    return total


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_score_view(request):
    if request.user.role != 'employee':
        return Response({'error': '직원만 자신의 점수를 조회할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    response = EvaluationResponse.objects.filter(employee=request.user, is_submitted=True).order_by('-submitted_at').first()
    team_bonus = request.user.team.bonus_score if request.user.team else 0
    score_values = response.score_values if response else {}
    personal_score = calculate_personal_score(score_values)
    final_score = max(0, min(100, personal_score + team_bonus))

    return Response(
        {
            'employee': request.user.id,
            'team_bonus': team_bonus,
            'personal_score': round(personal_score, 2),
            'final_score': round(final_score, 2),
            'submitted': response is not None,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_response_status_view(request):
    if not require_admin(request):
        return Response({'error': '관리자만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    status_rows = []
    teams = Team.objects.all().order_by('name')
    for team in teams:
        manager = team.manager
        responses = EvaluationResponse.objects.filter(team=team)
        submitted_employee_ids = list(
            responses.filter(is_submitted=True)
            .values_list('employee_id', flat=True)
            .distinct()
        )
        submitted_count = len(submitted_employee_ids)
        total_members = User.objects.filter(team=team, role='employee').count()
        status_rows.append({
            'team_id': team.id,
            'team_name': team.name,
            'manager_id': manager.id if manager else None,
            'manager_name': f"{manager.name} ({manager.username})" if manager else '미지정',
            'manager_username': manager.username if manager else None,
            'submitted_employee_ids': submitted_employee_ids,
            'submitted': submitted_count >= total_members if total_members else False,
            'submitted_count': submitted_count,
            'total_members': total_members,
            'team_bonus': team.bonus_score,
        })

    return Response(status_rows, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_result_summary_view(request):
    if not require_admin(request):
        return Response({'error': '관리자만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    items = list(EvaluationItem.objects.all().order_by('id'))
    item_names = [item.name for item in items]
    team_scores = {}
    personal_rows = []

    employees = User.objects.filter(role='employee').select_related('team').order_by('username')
    for employee in employees:
        response = EvaluationResponse.objects.filter(employee=employee, is_submitted=True).order_by('-submitted_at').first()
        team = employee.team
        team_name = team.name if team else '미배정'
        bonus = team.bonus_score if team else 0
        if response:
            personal_score = calculate_personal_score(response.score_values)
            final_score = max(0, min(100, personal_score + bonus))
            submission_status = '제출'
        else:
            personal_score = 0
            final_score = 0
            submission_status = '미제출'

        team_scores.setdefault(team_name, []).append(final_score)
        personal_rows.append({
            'employee_id': employee.id,
            'username': employee.username,
            'name': employee.name or employee.username,
            'team_name': team_name,
            'team_bonus': bonus,
            'personal_score': round(personal_score, 2),
            'final_score': round(final_score, 2),
            'status': submission_status,
        })

    team_average = [
        {
            'team_name': team_name,
            'avg_score': round(sum(values) / len(values), 2),
        }
        for team_name, values in sorted(team_scores.items())
    ]

    distribution = []
    score_ranges = [60, 70, 80, 90]
    for team_name, values in sorted(team_scores.items()):
        bins = []
        for threshold in score_ranges:
            if threshold == 90:
                count = sum(1 for value in values if value >= 90)
            else:
                upper = threshold + 9
                count = sum(1 for value in values if threshold <= value <= upper)
            bins.append({'label': str(threshold), 'count': count})
        distribution.append({'team_name': team_name, 'bins': bins})

    radar_series = []
    for team_name, values in sorted(team_scores.items()):
        series_values = []
        for item in items:
            item_values = []
            team_members = User.objects.filter(role='employee', team__name=team_name)
            for employee in team_members:
                item_response = EvaluationResponse.objects.filter(employee=employee, is_submitted=True).order_by('-submitted_at').first()
                if not item_response:
                    continue
                raw = item_response.score_values.get(str(item.id))
                if raw is None:
                    raw = item_response.score_values.get(item.id)
                if raw is None:
                    continue
                try:
                    item_values.append(int(raw))
                except (TypeError, ValueError):
                    continue
            if item_values:
                series_values.append(round(sum(item_values) / len(item_values) * 20, 2))
            else:
                series_values.append(0)
        radar_series.append({'team_name': team_name, 'values': series_values})

    return Response({
        'personal_rows': sorted(personal_rows, key=lambda item: item['final_score'], reverse=True),
        'team_average': team_average,
        'team_distribution': distribution,
        'radar': {
            'labels': item_names,
            'series': radar_series,
        },
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_result_csv_view(request):
    if not require_admin(request):
        return Response({'error': '관리자만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="evaluation_results.csv"'

    writer = csv.writer(response)
    writer.writerow(['사번', '성명', '팀', '개인 평가 점수', '팀 보너스', '최종 점수', '상태'])

    for team in Team.objects.all().order_by('name'):
        for employee in User.objects.filter(team=team, role='employee').order_by('username'):
            submitted_response = EvaluationResponse.objects.filter(employee=employee, is_submitted=True).order_by('-submitted_at').first()
            score_values = submitted_response.score_values if submitted_response else {}
            personal_score = calculate_personal_score(score_values)
            final_score = max(0, min(100, personal_score + team.bonus_score)) if submitted_response else 0

            writer.writerow([
                employee.username,
                employee.name or employee.username,
                team.name,
                round(personal_score, 2) if submitted_response else 0,
                team.bonus_score,
                round(final_score, 2) if submitted_response else 0,
                '제출' if submitted_response else '미제출',
            ])

    return response
