from django.db import models
from django.core.validators import MinValueValidator
from categories.models import Category
from users.models import Student

class Resource(models.Model):
    CONDITION_CHOICES = (('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'))
    STATUS_CHOICES = (('available', 'Available'), ('sold', 'Sold'), ('pending', 'Pending'))

    resource_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    date_posted = models.DateTimeField(auto_now_add=True)
    date_sold = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self): return f"{self.title} - ${self.price}"


class ResourceImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='images')
    image_path = models.ImageField(upload_to='resources/')
    display_order = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    def __str__(self): return f"Image for {self.resource.title}"

#comments section
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    comment_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.user.username} on {self.resource.title}'