from rest_framework import serializers
from .models import Category, Phrase

class PhraseLanguageSerializer(serializers.ModelSerializer):
    lang1 = serializers.SerializerMethodField()
    lang2 = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Phrase
        fields = ['id', 'lang1', 'lang2', 'category']

    def __init__(self, *args, **kwargs):
        self.lang1_key = kwargs.pop('lang1_key', 'lan1')
        self.lang2_key = kwargs.pop('lang2_key', 'lan2')
        super().__init__(*args, **kwargs)

    def get_lang1(self, obj):
        return obj.translated_text.get(self.lang1_key)

    def get_lang2(self, obj):
        return obj.translated_text.get(self.lang2_key)

    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        # Rename lang1 and lang2 to the dynamic language keys
        return {
            'id': representation['id'],
            self.lang1_key: representation['lang1'],
            self.lang2_key: representation['lang2'],
            'category': representation['category']
        }

class PhraseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phrase
        fields = ['id', 'translated_text', 'category']
        read_only_fields = ['id', 'translated_text']

    def to_internal_value(self, data):
        # Extract category and other fields dynamically
        category_id = data.get('category')
        translated_text = {key: value for key, value in data.items() if key not in ('category',)}

        # Validate category
        if not category_id:
            raise serializers.ValidationError({"category": "This field is required."})

        # Convert category_id to Category instance
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise serializers.ValidationError({"category": f"Category with id {category_id} does not exist."})

        # Validate that at least one translation field is provided
        if not translated_text:
            raise serializers.ValidationError("At least one translation field (e.g., lan1, lan2) is required.")

        return {
            'category': category,
            'translated_text': translated_text
        }

    def create(self, validated_data):
        # Create a new Phrase instance
        translated_text = validated_data.pop('translated_text', {})
        category = validated_data.get('category')

        # Directly create a new Phrase
        phrase = Phrase.objects.create(
            category=category,
            translated_text=translated_text
        )

        return phrase

    def update(self, instance, validated_data):
        translated_text = validated_data.pop('translated_text', {})
        instance.translated_text.update(translated_text)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance

class CategorySerializer(serializers.ModelSerializer):
    phrases = PhraseSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'phrases']
        read_only_fields = ['id', 'phrases']

    def validate_icon(self, value):
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Icon must be a valid URL.")
        return value

class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon']

    def validate_icon(self, value):
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Icon must be a valid URL.")
        return value