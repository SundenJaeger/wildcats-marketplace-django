from django.db import models
from marketplace.models import Resource
from users.models import User

# Create your models here.
class Report(models.Model):
    STATUS_CHOICES = (('open', 'Open'), ('in_progress', 'In Progress'), ('resolved', 'Resolved'))
    REPORT_REASON_CHOICES = (
        ('inappropriate_content', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('fraud', 'Fraud'),
        ('other', 'Other'),
    )

    report_id = models.AutoField(primary_key=True)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=REPORT_REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    date_reported = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'type': 'A'})

    def __str__(self): return f"Report #{self.report_id} - {self.resource.title}"
