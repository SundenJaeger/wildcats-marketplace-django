from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Resource, ResourceImage
from .models import Comment, Resource, Student
import json

# Keep this for the homepage
class HomePageView(View):
    template_name = 'index.html'

    def get(self, request):
        return render(request, self.template_name)


# API views
@method_decorator(csrf_exempt, name='dispatch')
class CreateResourceView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            title = data.get('title')
            description = data.get('description')
            price = data.get('price')
            condition = data.get('condition')
            status = data.get('status', 'available')
            category_id = data.get('category', {}).get('categoryId')
            student_id = data.get('student', {}).get('studentId')

            print("Received data:", data)  # <-- log incoming data
            print("Category ID:", category_id, "Student ID:", student_id)

            resource = Resource.objects.create(
                title=title,
                description=description,
                price=price,
                condition=condition.lower(),
                status=status.lower(),
                category_id=category_id,
                student_id=student_id
            )

            print("Resource created:", resource)

            return JsonResponse({
                'resourceId': resource.resource_id,
                'title': resource.title
            }, status=201)

        except Exception as e:
            import traceback
            print("Exception occurred:", str(e))
            traceback.print_exc()  # <-- print full traceback to console
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class UploadResourceImagesView(View):
    def post(self, request, resource_id):
        resource = Resource.objects.get(pk=resource_id)
        files = request.FILES.getlist('images')
        images = []
        for idx, file in enumerate(files):
            img = ResourceImage.objects.create(
                resource=resource,
                image_path=file,
                display_order=idx,
                is_primary=(idx==0)
            )
            images.append({
                'imageId': img.image_id,
                'url': img.image_path.url,
                'isPrimary': img.is_primary
            })
        return JsonResponse({'images': images}, status=201)
# @method_decorator(csrf_exempt, name='dispatch')
# class UploadResourceImagesView(View):
#     def post(self, request, resource_id):
#         resource = Resource.objects.get(pk=resource_id)
#         files = request.FILES.getlist('images')
#         images = []
#         for idx, file in enumerate(files):
#             img = ResourceImage.objects.create(
#                 resource=resource,
#                 image_path=file,
#                 display_order=idx,
#                 is_primary=(idx==0)
#             )
#             images.append({
#                 'imageId': img.image_id,
#                 'url': img.image_path.url,
#                 'isPrimary': img.is_primary
#             })
#         return JsonResponse({'images': images}, status=201)

class AvailableResourcesView(View):
    def get(self, request):
        resources = Resource.objects.filter(status='available') \
            .select_related('category', 'student__user') \
            .prefetch_related('images')

        data = []

        for r in resources:

            data.append({
                "resourceId": r.resource_id,
                "title": r.title,
                "description": r.description,
                "price": float(r.price),
                "condition": r.condition,
                "status": r.status,
                "datePosted": r.date_posted.isoformat(),
                "category": {
                    "categoryId": r.category.category_id,
                    "categoryName": r.category.category_name
                } if r.category else None,
                "student": {
                    "studentId": r.student.user_id,
                    "username": r.student.user.username
                } if r.student else None,
                "images": [
                    {
                        "imageId": img.image_id,
                        "imagePath": img.image_path.name,
                        "displayOrder": img.display_order
                    }
                    for img in r.images.all()
                ]
            })

        return JsonResponse(data, safe=False)
@method_decorator(csrf_exempt, name='dispatch')
class CommentsByResourceView(View):
    def get(self, request, resource_id):
        try:
            resource = Resource.objects.get(pk=resource_id)
            comments_qs = Comment.objects.filter(resource=resource, parent=None).order_by('-timestamp')

            comments = []
            for c in comments_qs:
                comments.append({
                    'commentId': c.comment_id,
                    'studentUsername': student_username,
                    'commentText': c.comment_text,
                    'timestamp': c.timestamp.isoformat(),
                    'replies': [
                        {
                            'commentId': r.comment_id,
                            'studentUsername': r.student.user.username,
                            'commentText': r.comment_text,
                            'timestamp': r.timestamp.isoformat()
                        } for r in c.replies.all().order_by('timestamp')
                    ]
                })

            return JsonResponse(comments, safe=False)
        except Resource.DoesNotExist:
            return JsonResponse({'error': 'Resource not found'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class AddCommentView(View):
    def post(self, request, student_id):
        try:
            data = json.loads(request.body)
            resource_id = data.get('resourceId')
            comment_text = data.get('commentText')
            parent_id = data.get('parentCommentId')

            student = Student.objects.get(pk=student_id)
            resource = Resource.objects.get(pk=resource_id)

            comment = Comment(student=student, resource=resource, comment_text=comment_text)
            if parent_id:
                parent_comment = Comment.objects.get(pk=parent_id)
                comment.parent = parent_comment

            comment.save()

            return JsonResponse({
                'commentId': comment.comment_id,
                'studentUsername': student.user.username,
                'commentText': comment.comment_text,
                'timestamp': comment.timestamp.isoformat(),
                'parentCommentId': parent_id
            }, status=201)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Resource.DoesNotExist:
            return JsonResponse({'error': 'Resource not found'}, status=404)
        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Parent comment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)