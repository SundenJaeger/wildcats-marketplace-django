from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import Report

def map_django_to_react_status(django_status):
    if django_status == 'open':
        return 'PENDING'
    if django_status == 'in_progress':
        return 'UNDER_REVIEW'
    if django_status == 'resolved':
        return 'RESOLVED'
    return 'PENDING'

def map_react_to_django_status(react_status):
    if react_status == 'PENDING':
        return 'open'
    if react_status == 'UNDER_REVIEW':
        return 'in_progress'
    if react_status == 'RESOLVED':
        return 'resolved'
    if react_status == 'DISMISSED':
        return 'open'
    return 'open'


def serialize_report(report):

    resource_data = None
    if report.resource:
        resource_data = {
            'resourceId': report.resource.resource_id,
            'title': report.resource.title,

        }

    student_data = None
    if report.admin:
        student_data = {
            'studentId': report.admin.user_id,
            'firstName': report.admin.first_name,
            'lastName': report.admin.last_name,
            'email': report.admin.email,
        }

    return {
        'reportId': report.report_id,
        'resourceId': report.resource_id,
        'reason': report.reason,
        'description': report.description,
        'status': map_django_to_react_status(report.status),

        'dateReported': report.date_reported.isoformat() if report.date_reported else None,
        'dateResolved': report.date_resolved.isoformat() if report.date_resolved else None,

        'resource': resource_data,
        'student': student_data,
    }

@csrf_exempt
def report_list(request):
    if request.method != 'GET':
        return HttpResponse(status=405)

    reports_queryset = Report.objects.all().select_related('resource', 'admin').order_by('-date_reported')

    filter_status = request.GET.get('status')
    if filter_status and filter_status != 'All Reports':
        django_status = map_react_to_django_status(filter_status)
        reports_queryset = reports_queryset.filter(status=django_status)

    reports_data = [serialize_report(report) for report in reports_queryset]

    return JsonResponse(reports_data, safe=False)


@csrf_exempt
def report_status_update(request, report_id):
    if request.method != 'PATCH':
        return HttpResponse(status=405)

    report = get_object_or_404(Report, pk=report_id)

    try:
        data = json.loads(request.body)
        new_status_react = data.get('status')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not new_status_react:
        return JsonResponse({'error': 'Status field is required.'}, status=400)

    new_status_django = map_react_to_django_status(new_status_react)

    report.status = new_status_django

    if new_status_react == 'RESOLVED' and not report.date_resolved:
        report.date_resolved = timezone.now()
    elif new_status_react != 'RESOLVED':
        report.date_resolved = None

    report.save()

    return JsonResponse(serialize_report(report), status=200)


@csrf_exempt
def report_delete(request, report_id):
    if request.method != 'DELETE':
        return HttpResponse(status=405)

    report = get_object_or_404(Report, pk=report_id)
    report.delete()

    return HttpResponse(status=204)