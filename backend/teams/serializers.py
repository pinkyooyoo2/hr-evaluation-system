from rest_framework import serializers

from teams.models import Team


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'manager', 'bonus_score']

    def validate_bonus_score(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError('팀 보너스 점수는 0~10 범위여야 합니다.')
        return value

    def validate_manager(self, value):
        if value is None:
            return value

        if value.role != 'manager':
            raise serializers.ValidationError('매니저 역할 사용자만 팀 매니저로 지정할 수 있습니다.')

        existing = Team.objects.filter(manager=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise serializers.ValidationError('이미 다른 팀에 배정된 매니저입니다.')

        return value
