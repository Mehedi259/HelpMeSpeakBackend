from rest_framework import serializers

class TranslationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    translated_text = serializers.CharField(allow_null=True)
    source_language = serializers.CharField(allow_null=True)
    same_language = serializers.BooleanField(required=False)
    error = serializers.CharField(allow_null=True)
    target_lang_code = serializers.CharField(allow_null=True)

class ChatRequestSerializer(serializers.Serializer):
    input = serializers.CharField()  # No max_length to allow any size

class ChatResponseSerializer(serializers.Serializer):
    is_translation_request = serializers.BooleanField()
    translated_text = serializers.CharField(allow_null=True)
    conversational_response = serializers.CharField()
    translation_result = TranslationResponseSerializer(required=False)

class AllLanguagesResponseSerializer(serializers.Serializer):
    translations = serializers.DictField(child=TranslationResponseSerializer())
    conversational_response = serializers.CharField()