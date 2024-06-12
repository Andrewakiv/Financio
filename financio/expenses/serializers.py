from rest_framework import serializers

from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='first_name'
    )
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Expense
        fields = ['title', 'price', 'datetime', 'category', 'user']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        return super().create(validated_data)
