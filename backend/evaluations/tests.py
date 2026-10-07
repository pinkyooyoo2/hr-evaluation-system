from django.test import TestCase
from rest_framework.test import APIClient

from evaluations.models import EvaluationItem, EvaluationResponse
from teams.models import Team
from users.models import User


class ManagerEvaluationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.manager = User.objects.create_user(
            username='MGR001',
            password='manager123!',
            name='김매니저',
            role='manager',
        )
        self.team = Team.objects.create(name='개발팀', manager=self.manager)
        self.employee = User.objects.create_user(
            username='EMP001',
            password='employee123!',
            name='이직원',
            role='employee',
            team=self.team,
        )
        self.item1 = EvaluationItem.objects.create(name='업무 수행', weight=60)
        self.item2 = EvaluationItem.objects.create(name='협업', weight=40)
        self.client.force_authenticate(user=self.manager)

    def test_manager_can_save_temporary_evaluation_for_team_member(self):
        response = self.client.post(
            '/api/evaluations/responses/',
            {
                'employee': self.employee.id,
                'score_values': {'1': 4, '2': 5},
                'temporary_save': {'1': 4, '2': 5},
                'is_submitted': False,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['employee'], self.employee.id)
        self.assertFalse(response.data['is_submitted'])
        self.assertEqual(response.data['progress'], 100)

    def test_manager_cannot_evaluate_employee_outside_team(self):
        another_team = Team.objects.create(name='인사팀', manager=None)
        outsider = User.objects.create_user(
            username='EMP002',
            password='employee123!',
            name='박직원',
            role='employee',
            team=another_team,
        )

        response = self.client.post(
            '/api/evaluations/responses/',
            {'employee': outsider.id, 'score_values': {'1': 4, '2': 5}, 'is_submitted': False},
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_submitted_response_cannot_be_modified(self):
        response = EvaluationResponse.objects.create(
            employee=self.employee,
            manager=self.manager,
            team=self.team,
            is_submitted=True,
            submitted_at='2024-01-01T00:00:00Z',
            score_values={'1': 4, '2': 5},
            progress=100,
        )

        update_response = self.client.post(
            '/api/evaluations/responses/',
            {'employee': self.employee.id, 'score_values': {'1': 5, '2': 5}, 'is_submitted': False},
            format='json',
        )

        self.assertEqual(update_response.status_code, 400)
        response.refresh_from_db()
        self.assertEqual(response.score_values, {'1': 4, '2': 5})
