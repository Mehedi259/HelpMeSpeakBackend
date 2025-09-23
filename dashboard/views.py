from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Category, Phrase
from .serializers import CategorySerializer, PhraseSerializer, CategoryNameSerializer, PhraseLanguageSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class PhraseViewSet(viewsets.ModelViewSet):
    queryset = Phrase.objects.all()
    serializer_class = PhraseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

class CategoryNameViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryNameSerializer

class PhraseLanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Phrase.objects.all()
    serializer_class = PhraseLanguageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Get language keys from query parameters
        lang1_key = self.request.query_params.get('lang1', 'lan1')
        lang2_key = self.request.query_params.get('lang2', 'lan2')
        # Filter phrases where both lang1_key and lang2_key exist in translated_text
        queryset = queryset.filter(**{
            f'translated_text__{lang1_key}__isnull': False,
            f'translated_text__{lang2_key}__isnull': False
        })
        # Filter by category if provided
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def get_serializer(self, *args, **kwargs):
        # Get language keys from query parameters
        lang1_key = self.request.query_params.get('lang1', 'lan1')
        lang2_key = self.request.query_params.get('lang2', 'lan2')
        # Pass language keys to serializer
        kwargs['lang1_key'] = lang1_key
        kwargs['lang2_key'] = lang2_key
        return super().get_serializer(*args, **kwargs)