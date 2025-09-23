from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, PhraseViewSet, CategoryNameViewSet, PhraseLanguageViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'phrases', PhraseViewSet, basename='phrase')
router.register(r'category-names', CategoryNameViewSet, basename='category-name')
router.register(r'phrase-languages', PhraseLanguageViewSet, basename='phrase-language')

urlpatterns = [
    path('', include(router.urls)),  # Remove 'api/' prefix
]