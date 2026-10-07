from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


def ensure_default_admin():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='ADMIN',
        defaults={
            'name': 'ADMIN',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        },
    )

    user.name = 'ADMIN'
    user.role = 'admin'
    user.is_staff = True
    user.is_superuser = True
    user.set_password('admin1234!')
    user.save()
    return user, created


def ensure_demo_hr_data():
    from django.apps import apps
    from django.contrib.auth import get_user_model

    User = get_user_model()
    Team = apps.get_model('teams', 'Team')
    EvaluationItem = apps.get_model('evaluations', 'EvaluationItem')
    EvaluationResponse = apps.get_model('evaluations', 'EvaluationResponse')

    Team.objects.exclude(name__in=['개발팀', '영업팀']).delete()
    User.objects.filter(role='manager').exclude(username__in=['M1', 'M2']).delete()
    User.objects.filter(role='employee').exclude(username__in=['E1', 'E2', 'E3', 'E4']).delete()

    team_specs = [
        ('개발팀', 'M1', 5),
        ('영업팀', 'M2', 0),
    ]
    team_map = {}

    for team_name, manager_username, bonus in team_specs:
        team, _ = Team.objects.get_or_create(name=team_name, defaults={'bonus_score': bonus})
        team.bonus_score = bonus
        manager, _ = User.objects.get_or_create(
            username=manager_username,
            defaults={'name': manager_username, 'role': 'manager'},
        )
        manager.name = '매니저1' if manager_username == 'M1' else '매니저2'
        manager.role = 'manager'
        manager.team = team
        manager.set_password('1234')
        manager.save()
        team.manager = manager
        team.save(update_fields=['manager', 'bonus_score'])
        team_map[team_name] = team

    employees = [
        ('E1', '직원1', '개발팀'),
        ('E2', '직원2', '개발팀'),
        ('E3', '직원3', '영업팀'),
        ('E4', '직원4', '영업팀'),
    ]
    employee_map = {}
    for username, name, team_name in employees:
        user, _ = User.objects.get_or_create(username=username, defaults={'name': name, 'role': 'employee'})
        user.name = name
        user.role = 'employee'
        user.team = team_map[team_name]
        user.set_password('1234')
        user.save()
        employee_map[username] = user

    item_specs = [
        ('업무 수행', 50, '업무 수행 역량 평가'),
        ('협업', 30, '협업 역량 평가'),
        ('태도', 20, '태도 및 참여도 평가'),
    ]
    items_by_name = {}
    for item_name, weight, description in item_specs:
        item, _ = EvaluationItem.objects.get_or_create(name=item_name, defaults={'weight': weight, 'description': description})
        item.weight = weight
        item.description = description
        item.save()
        items_by_name[item_name] = item

    response_specs = [
        ('E1', {'1': 4, '2': 5, '3': 3}, True),
        ('E2', {'1': 4, '2': 5, '3': 4}, True),
        ('E3', {'1': 4, '2': 4, '3': 4}, True),
        ('E4', {'1': 4, '2': 4, '3': 4}, True),
    ]
    for username, score_values, is_submitted in response_specs:
        employee = employee_map[username]
        manager = employee.team.manager
        EvaluationResponse.objects.filter(employee=employee).delete()
        response, _ = EvaluationResponse.objects.get_or_create(
            employee=employee,
            manager=manager,
            team=employee.team,
            defaults={'score_values': score_values, 'temporary_save': score_values, 'is_submitted': is_submitted, 'progress': 100, 'submitted_at': timezone.now()},
        )
        response.employee = employee
        response.manager = manager
        response.team = employee.team
        response.score_values = score_values
        response.temporary_save = score_values
        response.is_submitted = is_submitted
        response.progress = 100
        response.submitted_at = timezone.now()
        response.save()

    return {'teams': team_map, 'employees': list(employee_map.values()), 'items': list(items_by_name.values())}


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '관리자'),
        ('manager', '매니저'),
        ('employee', '직원'),
    ]

    name = models.CharField(max_length=100, blank=True, default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    team = models.ForeignKey(
        'teams.Team',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='members',
    )

    def __str__(self):
        return self.username
