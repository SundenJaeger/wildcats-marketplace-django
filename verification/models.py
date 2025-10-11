from django.db import models
from users.models import Student

# Create your models here.
from django.db import models
from users.models import Student

class InstructionalRecords(models.Model):
    ENROLLMENT_STATUS = (('active', 'Active'), ('inactive', 'Inactive'), ('graduated', 'Graduated'))
    YEAR_LEVEL = (('1', 'First Year'), ('2', 'Second Year'), ('3', 'Third Year'), ('4', 'Fourth Year'))

    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    enrollment_status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS)
    program = models.CharField(max_length=200)
    year_level = models.CharField(max_length=1, choices=YEAR_LEVEL)

    def __str__(self): return f"{self.student.user.first_name} - {self.program}"


class VerificationRequest(models.Model):
    STATUS_CHOICES = (('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'))
    verification_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)

    def __str__(self): return f"Verification #{self.verification_id}"
