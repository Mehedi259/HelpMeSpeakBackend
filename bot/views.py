from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatRequestSerializer, ChatResponseSerializer, AllLanguagesResponseSerializer
from .translator import AITranslatorChatbot

class ChatView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chatbot = AITranslatorChatbot()

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if serializer.is_valid():
            user_input = serializer.validated_data['input']
            # Use handle_translation_request to process the input
            response_data = self.chatbot.handle_translation_request(user_input)
            
            if not response_data['success']:
                response_serializer = ChatResponseSerializer({
                    'is_translation_request': False,
                    'translated_text': None,
                    'conversational_response': response_data['conversational_response']
                })
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            
            if response_data['target_language'] == 'all':
                response_serializer = AllLanguagesResponseSerializer({
                    'translated_text': response_data['translated_text'],
                    'conversational_response': response_data['conversational_response']
                })
            else:
                response_serializer = ChatResponseSerializer({
                    'is_translation_request': True,
                    'translated_text': response_data['translated_text'],
                    'conversational_response': response_data['conversational_response']  # Only translated text
                })
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LanguagesView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chatbot = AITranslatorChatbot()

    def get(self, request):
        return Response(self.chatbot.supported_languages, status=status.HTTP_200_OK)