from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import VerificationRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import Student
import json


@csrf_exempt
def verification_requests_list(request):
    # This line MUST be the first line of logic
    if request.method == 'GET':
        status = request.GET.get('status')

        requests_queryset = VerificationRequest.objects.select_related('student').order_by('-request_date')

        if status:
            status = status.upper()
        VALID_STATUSES = ['PENDING', 'APPROVED', 'REJECTED']
        if status in VALID_STATUSES:
            requests_queryset = requests_queryset.filter(status=status)
        data = []
        for vr in requests_queryset:
            user_obj = vr.student

            data.append({
                'verificationId': vr.verification_id,
                'student': {
                    'user': {
                        'firstName': user_obj.first_name,
                        'lastName': user_obj.last_name,
                        'email': user_obj.email,
                    }
                },
                'status': vr.status,
                'requestDate': vr.request_date.isoformat(),
                'responseDate': vr.response_date.isoformat() if vr.response_date else None,
                'adminNotes': vr.admin_notes,
                'rejectionReason': vr.rejection_reason
            })

        return JsonResponse(data, safe=False)

    return HttpResponse(status=405)

@csrf_exempt
def verification_request_detail(request, verification_id):
    try:
        # 1. FIX: Use select_related('student') for efficiency
        #    and get the VerificationRequest object (vr)
        vr = VerificationRequest.objects.select_related('student').get(verification_id=verification_id)

        # 2. Access the related User object for name/email fields
        user_obj = vr.student

        # 3. Access the related Student Profile object for the verification flag
        student_profile_obj = Student.objects.get(user=user_obj)


    except VerificationRequest.DoesNotExist:

        return JsonResponse({'error': 'Verification request not found'}, status=404)

    except Student.DoesNotExist:

        return JsonResponse({'error': 'Associated student profile not found'}, status=404)
    # The rest of your logic here is correct
    if request.method == 'GET':
        # ... (Your existing GET logic) ...
        return JsonResponse({
            'verificationId': vr.verification_id,
            'student': {
                'user': {
                    'firstName': user_obj.first_name,
                    'lastName': user_obj.last_name,
                    'email': user_obj.email,
                }
            },
            'status': vr.status,
            'requestDate': vr.request_date.isoformat(),
            'responseDate': vr.response_date.isoformat() if vr.response_date else None,
            'adminNotes': vr.admin_notes,
            'rejectionReason': vr.rejection_reason
        })


    elif request.method == 'PATCH':

        try:

            if vr.status != 'PENDING':
                return JsonResponse({'error': 'Request is already processed.'}, status=400)

            body = json.loads(request.body)

            new_status = body.get('status', vr.status).upper()

            admin_notes = body.get('adminNotes', vr.admin_notes)

            rejection_reason = body.get('rejectionReason')

            # Validation

            VALID_STATUSES = [choice[0] for choice in VerificationRequest.STATUS_CHOICES]

            if new_status not in VALID_STATUSES:
                return JsonResponse({'error': f"Invalid status: {new_status}"}, status=400)

            # Apply updates

            vr.status = new_status
            vr.admin_notes = admin_notes

            if new_status == 'APPROVED':
                vr.rejection_reason = ''  # Set to None, or '' if your DB field cannot be null
            else:
                vr.rejection_reason = rejection_reason
            # Update response date and student profile

            if new_status in ['APPROVED', 'REJECTED'] and vr.response_date is None:

                vr.response_date = timezone.now()

                # Update Student's verified status if approved

                if new_status == 'APPROVED':
                    student_profile_obj.is_verified = True
                    student_profile_obj.save()  # <-- This now saves the Student object

            vr.save()  # <-- This saves the VerificationRequest object

            return JsonResponse({'message': f'Verification request updated to {new_status} successfully.'})


        except json.JSONDecodeError:

            return JsonResponse({'error': 'Invalid JSON body'}, status=400)


        except Exception as e:

            # Added a more descriptive error return for debugging

            print(f"Error during PATCH: {e}")

            return JsonResponse({'error': str(e)}, status=400)

        # --- Fallthrough ---

    return HttpResponse(status=405)


def student_verification_status(request, student_id):
    try:
        vr = VerificationRequest.objects.filter(student_id=student_id).latest('request_date')
        return JsonResponse({
            'status': vr.status,
            'requestDate': vr.request_date,
            'responseDate': vr.response_date
        })
    except VerificationRequest.DoesNotExist:
        return JsonResponse({'status': 'not_requested'})
