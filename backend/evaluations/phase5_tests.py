from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from evaluations.models import EvaluationItem, EvaluationResponse
from teams.models import Team
from users.models import User


class Phase5EvaluationLogicTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='ADMIN',
            password='admin1234!',
            name='ADMIN',
            role='admin',
        )
        self.manager = User.objects.create_user(
            username='MGR001',
            password='manager123!',
            name='김매니저',
            role='manager',
        )
        self.team = Team.objects.create(name='개발팀', manager=self.manager, bonus_score=5)
        self.employee = User.objects.create_user(
            username='EMP001',
            password='employee123!',
            name='이직원',
            role='employee',
            team=self.team,
        )
        self.item1 = EvaluationItem.objects.create(name='업무 수행', weight=50)
        self.item2 = EvaluationItem.objects.create(name='협업', weight=30)
        self.item3 = EvaluationItem.objects.create(name='태도', weight=20)

    def test_employee_final_score_is_computed_from_scores_and_team_bonus(self):
        response = EvaluationResponse.objects.create(
            employee=self.employee,
            manager=self.manager,
            team=self.team,
            is_submitted=True,
            score_values={'1': 4, '2': 5, '3': 3},
            progress=100,
        )

        self.client.force_authenticate(user=self.employee)
        url = reverse('employee-score')
        result = self.client.get(url)

        self.assertEqual(result.status_code, 200)
        self.assertAlmostEqual(result.data['final_score'], 87.0)
        self.assertEqual(result.data['team_bonus'], 5)

    def test_admin_can_get_response_status_summary(self):
        self.client.force_authenticate(user=self.admin)
        EvaluationResponse.objects.create(
            employee=self.employee,
            manager=self.manager,
            team=self.team,
            is_submitted=False,
            progress=50,
        )

        response = self.client.get('/api/evaluations/status/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertIn('submitted', response.data[0])

    def test_status_counts_unique_employee_submissions(self):
        self.client.force_authenticate(user=self.admin)
        EvaluationResponse.objects.create(
            employee=self.employee,
            manager=self.manager,
            team=self.team,
            is_submitted=True,
            score_values={'1': 4, '2': 5, '3': 3},
            progress=100,
        )
        EvaluationResponse.objects.create(
            employee=self.employee,
            manager=User.objects.create_user(
                username='MGR002',
                password='manager123!',
                name='김매니저2',
                role='manager',
            ),
            team=self.team,
            is_submitted=True,
            score_values={'1': 5, '2': 5, '3': 5},
            progress=100,
        )

        response = self.client.get('/api/evaluations/status/')
        self.assertEqual(response.status_code, 200)
        team_row = next(row for row in response.data if row['team_name'] == '개발팀')
        self.assertEqual(team_row['total_members'], 1)
        self.assertEqual(team_row['submitted_count'], 1)

    def test_admin_can_get_result_summary_dashboard(self):
        self.client.force_authenticate(user=self.admin)
        EvaluationResponse.objects.create(
            employee=self.employee,
            manager=self.manager,
            team=self.team,
            is_submitted=True,
            score_values={'1': 4, '2': 5, '3': 3},
            progress=100,
        )

        response = self.client.get('/api/evaluations/results/summary/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('personal_rows', response.data)
        self.assertIn('team_average', response.data)
        self.assertIn('radar', response.data)

    def test_admin_can_download_csv_result(self):
        self.client.force_authenticate(user=self.admin)
        EvaluationResponse.objects.create(
            employee=self.employee,
            manager=self.manager,
            team=self.team,
            is_submitted=True,
            score_values={'1': 4, '2': 5, '3': 3},
            progress=100,
        )

        response = self.client.get('/api/evaluations/results/csv/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('사번', response.content.decode('utf-8'))
