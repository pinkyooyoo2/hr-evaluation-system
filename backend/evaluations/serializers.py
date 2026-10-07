from django.utils import timezone
from rest_framework import serializers

from evaluations.models import EvaluationItem, EvaluationResponse
from users.models import User


class EvaluationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationItem
        fields = ['id', 'name', 'weight', 'description']

    def validate(self, attrs):
        total = 0
        if self.instance:
            total += sum(item.weight for item in EvaluationItem.objects.exclude(pk=self.instance.pk))
        else:
            total += sum(item.weight for item in EvaluationItem.objects.all())

        total += attrs.get('weight', self.instance.weight if self.instance else 0)

        if total != 100:
            raise serializers.ValidationError({'weight': '평가 항목 가중치 합계는 100이어야 합니다.'})

        return attrs


class EvaluationResponseSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    manager = serializers.PrimaryKeyRelatedField(read_only=True)
    team = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = EvaluationResponse
        fields = [
            'id',
            'employee',
            'manager',
            'team',
            'is_submitted',
            'submitted_at',
            'score_values',
            'temporary_save',
            'progress',
        ]
        read_only_fields = ['manager', 'team', 'submitted_at', 'progress']

    def validate_score_values(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError('점수는 항목별 딕셔너리 형식이어야 합니다.')

        for item_id, score in value.items():
            try:
                numeric_score = int(score)
            except (TypeError, ValueError):
                raise serializers.ValidationError('점수는 1~5 사이의 정수여야 합니다.')
            if numeric_score < 1 or numeric_score > 5:
                raise serializers.ValidationError('점수는 1~5 사이여야 합니다.')

        return value

    def validate(self, attrs):
        request = self.context.get('request')
        employee = attrs.get('employee', getattr(self.instance, 'employee', None))

        if employee and employee.team and request and request.user.role == 'manager':
            if employee.team.manager_id != request.user.id:
                raise serializers.ValidationError({'employee': '본인 팀 직원만 평가할 수 있습니다.'})

        if self.instance and self.instance.is_submitted:
            raise serializers.ValidationError({'detail': '제출된 평가는 수정할 수 없습니다.'})

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        employee = validated_data['employee']
        team = employee.team

        if not team or team.manager_id != request.user.id:
            raise serializers.ValidationError({'employee': '본인 팀 직원만 평가할 수 있습니다.'})

        response, created = EvaluationResponse.objects.get_or_create(
            employee=employee,
            manager=request.user,
            team=team,
            defaults={
                'score_values': {},
                'temporary_save': {},
                'progress': 0,
            },
        )

        if response.is_submitted:
            raise serializers.ValidationError({'detail': '제출된 평가는 수정할 수 없습니다.'})

        response.score_values = validated_data.get('score_values', response.score_values)
        response.temporary_save = validated_data.get('temporary_save', response.temporary_save)
        response.is_submitted = validated_data.get('is_submitted', False)
        if response.is_submitted:
            response.submitted_at = timezone.now()
        else:
            response.submitted_at = None

        total_items = EvaluationItem.objects.count()
        answered_count = 0
        values = response.score_values if isinstance(response.score_values, dict) else {}
        for value in values.values():
            try:
                if 1 <= int(value) <= 5:
                    answered_count += 1
            except (TypeError, ValueError):
                continue
        response.progress = 0 if total_items == 0 else int(round((answered_count / total_items) * 100))
        response.save()
        return response
