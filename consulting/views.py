from django.shortcuts import render
from django.http import JsonResponse
from django.db import connections
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.db import connections
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import  datetime

def company_code_check(company_code_value):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.company_code != company_code_value:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator



@login_required
@company_code_check("consulting")
@require_http_methods(["GET", "DELETE"])
def consulting(request):
    if request.method == "GET":

        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_user ORDER BY join_date DESC LIMIT 4")
            user_list = cursor.fetchall()

        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM accounts_user")
            total_users = cursor.fetchone()[0]

        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_teammembership ORDER BY id DESC LIMIT 4")
            membership_list = cursor.fetchall()
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_service_members ORDER BY id DESC LIMIT 4")
            service_teammembership_list = cursor.fetchall()

        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_service ORDER BY id DESC LIMIT 4")
            services= cursor.fetchall()

        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_conversation ORDER BY id DESC LIMIT 4")
            conversations = cursor.fetchall()

        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_contactmessage ORDER BY id DESC LIMIT 4")
            messages = cursor.fetchall()

        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_comment ORDER BY id DESC LIMIT 4")
            comments = cursor.fetchall()

        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_blogpost ORDER BY id DESC LIMIT 4")
            blogposts = cursor.fetchall()

        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM accounts_blogpost")
            total_blogpost = cursor.fetchone()[0]

        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM accounts_requesthistory")
            total_request=cursor.fetchone()[0]

        user=request.user
        current_time = datetime.now()
        received_messages=user.received_messages.all().order_by('-sent_at')





        return render(request, 'consulting.html',
        {'users': user_list, 'memberships': membership_list,'current_time':current_time,
         'servicememberships': service_teammembership_list,'services': services,'conversations': conversations,
         'messages': messages, 'comments': comments,'blogposts': blogposts,'totalusers':total_users,'totalblogposts':total_blogpost,
         'received_messages':received_messages,'total_request':total_request})

    elif request.method == "DELETE":

        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'user':
                    cursor.execute("DELETE FROM accounts_user WHERE id = %s", [entity_id])
                elif entity_type == 'member':
                    cursor.execute("DELETE FROM accounts_teammembership WHERE id = %s", [entity_id])
                elif entity_type == 'servicemember':
                    cursor.execute("DELETE FROM accounts_service_members WHERE id = %s", [entity_id])
                elif entity_type == 'service':
                    cursor.execute("DELETE FROM accounts_service WHERE id = %s", [entity_id])
                elif entity_type == 'conversation':
                    cursor.execute("DELETE FROM accounts_conversation WHERE id = %s", [entity_id])
                elif entity_type == 'message':
                    cursor.execute("DELETE FROM accounts_contactmessage WHERE id = %s", [entity_id])
                elif entity_type == 'comment':
                    cursor.execute("DELETE FROM accounts_comment WHERE id = %s", [entity_id])
                elif entity_type == 'blogpost':
                    cursor.execute("DELETE FROM accounts_blogpost WHERE id = %s", [entity_id])
                else:
                    return JsonResponse({'success': False, 'error': 'Invalid entity type'})

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@login_required
@company_code_check("consulting")
def consuseradd(request):
    if request.method == "POST":
        try:
            # Foydalanuvchidan kelayotgan POST so'rovidagi ma'lumotlarni olish
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            profile_picture = request.POST.get('profile_picture', None)
            is_superuser = request.POST.get('is_superuser') == 'on'  # Checkbox dan keladigan qiymatni olish
            is_staff = request.POST.get('is_staff') == 'on'  # Checkbox dan keladigan qiymat

            # Foydalanuvchini ma'lumotlar bazasiga qo'shish
            with connections['consulting'].cursor() as cursor:
                cursor.execute("""
                    INSERT INTO accounts_user
                    (first_name, last_name, email, phone_number, profile_picture, is_superuser, is_staff, join_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, [first_name, last_name, email, phone_number, profile_picture, is_superuser, is_staff])

            return render(request,'consulting.html')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'cons_add_staff.html')



@login_required
@company_code_check("consulting")
@require_http_methods(["GET", "POST"])


def consusers(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_user ORDER BY id DESC")
            user_list = cursor.fetchall()

        return render(request, 'cons_users.html', {'users': user_list})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'user':
                    cursor.execute("DELETE FROM accounts_user WHERE id = %s", [entity_id])

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            new_status = data.get('new_status') == 'true'

            with connections['consulting'].cursor() as cursor:
                cursor.execute("UPDATE accounts_user SET is_staff = %s WHERE id = %s", [new_status, user_id])

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})





@login_required
@company_code_check("consulting")
def conschatrequests(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_chatrequest ORDER BY id DESC")
            requests = cursor.fetchall()

        return render(request, 'cons_chatrequests.html', {'abouts': requests})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'request':
                    cursor.execute("DELETE FROM chatrequest WHERE id = %s", [entity_id])
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# @login_required
# @company_code_check("consulting")
# def consteammembership(request):
#     if request.method == "GET":
#         with connections['consulting'].cursor() as cursor:
#             cursor.execute("SELECT * FROM accounts_teammembership ORDER BY id DESC")
#             teammemberships = cursor.fetchall()

#         return render(request,'cons_teammemberships.html',{'memberships': teammemberships})

#     elif request.method == "DELETE":
#         entity_type = request.GET.get('type')
#         entity_id = request.GET.get('id')

#         try:
#             with connections['consulting'].cursor() as cursor:
#                 if entity_type == 'member':
#                     cursor.execute("DELETE FROM accounts_teammembership WHERE id = %s", [entity_id])

#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})




@login_required
@company_code_check("consulting")
def consteammembership(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_teammembership ORDER BY id DESC")
            teammemberships = cursor.fetchall()
        return render(request, 'cons_teammemberships.html', {'memberships': teammemberships})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'member':
                    cursor.execute("DELETE FROM accounts_teammembership WHERE id = %s", [entity_id])
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == "PUT":
        entity_id = request.GET.get('id')
        try:
            data = json.loads(request.body.decode('utf-8'))
            role = data.get('role')
            description = data.get('description')
            instagram = data.get('instagram')
            twitter = data.get('twitter')
            facebook = data.get('facebook')
            youtube = data.get('youtube')
            linkedin = data.get('linkedin')

            with connections['consulting'].cursor() as cursor:
                cursor.execute("""
                    UPDATE accounts_teammembership
                    SET  role = %s, description = %s, instagram = %s,
                        twitter = %s, facebook = %s, youtube = %s, linkedin = %s
                    WHERE id = %s
                """, [ role, description, instagram, twitter, facebook, youtube, linkedin, entity_id])
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)








@login_required
@company_code_check("consulting")
def servicememberships(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_service_teammembership ORDER BY id DESC")
            service_teammembership = cursor.fetchall()

        return render(request,'cons_servicememberships.html',{'servicememberships': service_teammembership})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'servicemember':
                    cursor.execute("DELETE FROM accounts_service_teammembership WHERE id = %s", [entity_id])

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})



# @login_required
# @company_code_check("consulting")
# def consservices(request):
#     if request.method == "GET":
#         with connections['consulting'].cursor() as cursor:
#             cursor.execute("SELECT * FROM accounts_service ORDER BY id DESC")
#             services = cursor.fetchall()

#         return render(request,'cons_services.html',{'services': services})

#     elif request.method == "DELETE":
#         entity_type = request.GET.get('type')
#         entity_id = request.GET.get('id')

#         try:
#             with connections['consulting'].cursor() as cursor:
#                 if entity_type == 'service':
#                     cursor.execute("DELETE FROM accounts_service WHERE id = %s", [entity_id])

#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})




@login_required
@company_code_check("consulting")
def consservices(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_service ORDER BY id DESC")
            services = cursor.fetchall()
        return render(request, 'cons_services.html', {'services': services})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'service':
                    cursor.execute("DELETE FROM accounts_service WHERE id = %s", [entity_id])
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == "PUT":
        entity_id = request.GET.get('id')
        try:
            data = json.loads(request.body.decode('utf-8'))  # JSON formatda kelgan ma'lumotni o'qish
            name = data.get('name')
            description = data.get('description')

            with connections['consulting'].cursor() as cursor:
                cursor.execute(
                    "UPDATE accounts_service SET name = %s, description = %s WHERE id = %s",
                    [name, description, entity_id]
                )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)








@login_required
@company_code_check("consulting")
def consconversation(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_conversation ORDER BY id DESC")
            conversations = cursor.fetchall()

        return render(request,'cons_conversation.html',{'conversations': conversations})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'conversation':
                    cursor.execute("DELETE FROM accounts_conversation WHERE id = %s", [entity_id])

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})





@login_required
@company_code_check("consulting")
def conscontactmessage(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_contactmessage ORDER BY id DESC")
            messages = cursor.fetchall()

        return render(request,'cons_contactmessage.html',{'messages': messages})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'message':
                    cursor.execute("DELETE FROM accounts_contactmessage WHERE id = %s", [entity_id])

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@login_required
@company_code_check("consulting")
def conscomments(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_comment ORDER BY id DESC")
            comments = cursor.fetchall()

        return render(request,'cons_comments.html',{'comments': comments})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'comment':
                    cursor.execute("DELETE FROM accounts_comment WHERE id = %s", [entity_id])

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@login_required
@company_code_check("consulting")
def consblogpost(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_blogpost ORDER BY id DESC")
            blogposts = cursor.fetchall()

        return render(request,'cons_blogposts.html',{'blogposts': blogposts})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'blogpost':
                    cursor.execute("DELETE FROM accounts_blogpost WHERE id = %s", [entity_id])

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})




@login_required
@company_code_check("consulting")
def conshistory(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_requesthistory ORDER BY id DESC")
            histories = cursor.fetchall()

        return render(request,'cons_history.html',{'histories': histories})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'history':
                    cursor.execute("DELETE FROM accounts_requesthistory WHERE id = %s", [entity_id])

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@login_required
@company_code_check("consulting")
def telegrammessage(request):
    if request.method == "GET":
        with connections['consulting'].cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_accounts_telegramusermessage ORDER BY id DESC")
            telegrams = cursor.fetchall()

        return render(request,'cons_telegram.html',{'telegrams': telegrams})

    elif request.method == "DELETE":
        entity_type = request.GET.get('type')
        entity_id = request.GET.get('id')

        try:
            with connections['consulting'].cursor() as cursor:
                if entity_type == 'history':
                    cursor.execute("DELETE FROM accounts_telegramusermessage WHERE id = %s", [entity_id])

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})



@login_required
@company_code_check("consulting")
def add_teammembership(request):
    with connections['consulting'].cursor() as cursor:
        cursor.execute('SELECT id, email FROM accounts_user')
        users = cursor.fetchall()


    if request.method == "POST":
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        description = request.POST.get('description')
        instagram = request.POST.get('instagram')
        twitter = request.POST.get('twitter')
        facebook = request.POST.get('facebook')
        youtube = request.POST.get('youtube')
        linkedin = request.POST.get('linkedin')

        try:
            with connections['consulting'].cursor() as cursor:
                cursor.execute("""
                    INSERT INTO accounts_teammembership (user_id, role, description, instagram, twitter, facebook, youtube, linkedin)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, [user_id, role, description, instagram, twitter, facebook, youtube, linkedin])
            return redirect('consteammemberships')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'cons_add_teammembership.html', {'users': users})



@login_required
@company_code_check("consulting")
def add_service(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')

        try:
            with connections['consulting'].cursor() as cursor:
                cursor.execute("""
                    INSERT INTO accounts_service (name, description, created_at)
                    VALUES (%s, %s, NOW())
                """, [name, description])
            return redirect('consservices')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'cons_add_service.html')


















