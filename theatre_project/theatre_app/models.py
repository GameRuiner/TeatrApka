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
    title = models.CharField(max_length=300)
    # theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE, related_name='performances')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, null=True)
    description = models.TextField(blank=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.theatre.name} ({self.date} {self.time})"
    
    @property
    def is_available(self):
        return self.status == 'KUP BILET' and self.date >= timezone.now().date()
    
    class Meta:
        ordering = ['date', 'time']
        unique_together = ['title', 'theatre', 'date', 'time']

class Review(models.Model):
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, related_name='reviews')
    author_name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.performance.title} - {self.rating}/5 by {self.author_name}"
    
    class Meta:
        ordering = ['-created_at']