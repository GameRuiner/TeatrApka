from django.db import models
from django.utils import timezone

class Theatre(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Performance(models.Model):
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE, related_name='performances')    
    title = models.CharField(max_length=300)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - ({self.date} {self.time})"
    
    class Meta:
        ordering = ['date', 'time']
        unique_together = ['theatre', 'title', 'date', 'time']

# class Review(models.Model):
#     performance = models.ForeignKey(Performance, on_delete=models.CASCADE, related_name='reviews')
#     author_name = models.CharField(max_length=100)
#     rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
#     comment = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.performance.title} - {self.rating}/5 by {self.author_name}"
    
#     class Meta:
#         ordering = ['-created_at']