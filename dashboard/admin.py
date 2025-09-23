from django.contrib import admin
from .models import Category, Phrase

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'icon']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Phrase)
class PhraseAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_english', 'get_bangla', 'category']
    search_fields = ['translated_text__english', 'translated_text__bangla']
    list_filter = ['category']

    def get_english(self, obj):
        return obj.translated_text.get('english', 'N/A')
    get_english.short_description = 'English'

    def get_bangla(self, obj):
        return obj.translated_text.get('bangla', 'N/A')
    get_bangla.short_description = 'Bangla'