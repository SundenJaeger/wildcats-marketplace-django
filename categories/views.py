from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Category
import json

# GET all categories / POST a new category
@csrf_exempt
def categories_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        data = []
        for cat in categories:
            data.append({
                'categoryId': cat.category_id,
                'categoryName': cat.category_name,
                'parentCategory': {'categoryId': cat.parent_category.category_id} if cat.parent_category else None,
                'description': cat.description,
                'isActive': cat.is_active
            })
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            parent_id = body.get('parentCategory', {}).get('categoryId') if body.get('parentCategory') else None
            parent = Category.objects.get(category_id=parent_id) if parent_id else None

            category = Category.objects.create(
                category_name=body['categoryName'],
                parent_category=parent,
                description=body.get('description', ''),
                is_active=body.get('isActive', True)
            )
            return JsonResponse({
                'categoryId': category.category_id,
                'categoryName': category.category_name,
                'parentCategory': {'categoryId': category.parent_category.category_id} if category.parent_category else None,
                'description': category.description,
                'isActive': category.is_active
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


# GET, PUT, DELETE a single category
@csrf_exempt
def category_detail(request, category_id):
    try:
        category = Category.objects.get(category_id=category_id)
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'categoryId': category.category_id,
            'categoryName': category.category_name,
            'parentCategory': {'categoryId': category.parent_category.category_id} if category.parent_category else None,
            'description': category.description,
            'isActive': category.is_active
        })

    elif request.method == 'PUT':
        try:
            body = json.loads(request.body)
            category.category_name = body.get('categoryName', category.category_name)
            category.description = body.get('description', category.description)
            category.is_active = body.get('isActive', category.is_active)

            parent_id = body.get('parentCategory', {}).get('categoryId') if body.get('parentCategory') else None
            category.parent_category = Category.objects.get(category_id=parent_id) if parent_id else None

            category.save()
            return JsonResponse({'message': 'Category updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        category.delete()
        return JsonResponse({'message': 'Category deleted successfully'})


from django.http import JsonResponse
from .models import Category


def categories_for_students(request):
    """
    Returns only active categories for the student site.
    Optional query params:
    - parent_only=true -> only return parent categories
    """
    categories = Category.objects.filter(is_active=True)

    if request.GET.get('parent_only') == 'true':
        categories = categories.filter(parent_category__isnull=True)

    data = [
        {
            'categoryId': cat.category_id,
            'categoryName': cat.category_name,
            'parentCategory': {'categoryId': cat.parent_category.category_id} if cat.parent_category else None,
        }
        for cat in categories
    ]

    return JsonResponse(data, safe=False)
def active_categories(request):
    categories = list(
        Category.objects.filter(is_active=True).values('category_id', 'category_name')
    )
    return JsonResponse(categories, safe=False)