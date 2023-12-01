'''Serializers for recipe API'''

from core.models import Recipe, Tag, Ingredient
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    '''Serializer for recipe tags'''

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientsSerializer(serializers.ModelSerializer):
    '''Serializer for ingredients'''

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    '''Serializer for recipes'''
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientsSerializer(many=True, required=False)
    chef_name = serializers.CharField(max_length=255, allow_blank=True, validators=[validators.RegexValidator(r'^[a-zA-Z]+$', 'Only alphabets are allowed.')])

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients', 'image', 'chef_name']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        '''Helper function for getting or creating tags as needed'''
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        '''Helper function for getting or creating ingredients as needed'''
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        chef_name = validated_data.pop('chef_name', None)
        recipe = Recipe.objects.create(**validated_data)
        if chef_name:
            recipe.chef_name = chef_name
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        '''Update recipe'''
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        chef_name = validated_data.pop('chef_name', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if chef_name:
            instance.chef_name = chef_name

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    '''Serializer for recipe detail view.'''

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'chef_name']


class RecipeImageSerializer(serializers.ModelSerializer):
    '''Serializer for recipe images'''

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']

        # extra_kwargs = {'image': {}}
