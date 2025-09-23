from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Phrase(models.Model):
    id = models.AutoField(primary_key=True)
    translated_text = models.JSONField(default=dict)  # Stores translations as { "english": "How muchdsds is thisdd?", "french": "Combien ça coûte ?" }
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='phrases')

    def __str__(self):
        return f"Phrase {self.id} ({self.category.name})"