from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from teams.models import Team
from users.models import User


class DefaultAdminTests(TestCase):
    def test_create_default_admin_command(self):
        call_command('create_default_admin')

        user = User.objects.filter(username='ADMIN').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'ADMIN')
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.check_password('admin1234!'))


class LoginApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='EMP001',
            password='secret123!',
            name='홍길동',
            role='employee',
        )

    def test_login_success(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'EMP001', 'password': 'secret123!'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'EMP001')
        self.assertEqual(response.data['user']['role'], 'employee')

    def test_login_failed_with_wrong_password(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'EMP001', 'password': 'wrong-password'},
            format='json',
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.data)


class AdminManagementApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='ADMIN',
            password='admin1234!',
            name='ADMIN',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )
        self.manager = User.objects.create_user(
            username='MGR001',
            password='manager123!',
            name='김매니저',
            role='manager',
        )
        self.client.force_authenticate(user=self.admin)

    def test_can_create_team_with_manager(self):
        response = self.client.post('/api/teams/', {'name': '개발팀', 'manager': self.manager.id}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], '개발팀')
        self.assertEqual(response.data['manager'], self.manager.id)

    def test_can_create_user_with_team(self):
        team = Team.objects.create(name='개발팀', manager=self.manager)
        response = self.client.post(
            '/api/users/',
            {'username': 'EMP001', 'name': '이직원', 'role': 'employee', 'team': team.id},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], 'EMP001')
        self.assertEqual(response.data['team'], team.id)

    def test_evaluation_item_weight_total_must_be_100(self):
        response = self.client.post(
            '/api/evaluation-items/',
            [
                {'name': '업무 수행', 'weight': 60, 'description': 'A'},
                {'name': '협업', 'weight': 50, 'description': 'B'},
            ],
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('weight', response.data)
