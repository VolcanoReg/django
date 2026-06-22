from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth.models import User
from .models import Course

from django.db.models import Count, Max, Min, Avg
from .models import Course, CourseMember

def testing_crud(request):
    response = {}

    # 1. CREATE / INSERT
    user, created = User.objects.get_or_create(
        username="usertesting",
        defaults={"email": "usertest@email.com"}
    )
    if created:
        user.set_password("sanditesting")
        user.save()
    response['create'] = "User created/fetched"

    # 2. READ (All & Get Single)
    all_users = User.objects.all()
    response['all_users'] = serializers.serialize('python', all_users)
    
    try:
        admin = User.objects.get(pk=1)
        response['admin'] = serializers.serialize('python', [admin])[0]
    except User.DoesNotExist:
        response['admin'] = "Admin not found"

    # 3. DELETE
    deleted, _ = User.objects.filter(username='usertesting').delete()
    response['delete'] = f"Deleted {deleted} user(s)"

    return JsonResponse(response, safe=False)

def allcourse(request):
    courses = Course.objects.select_related('teacher').all()
    result = []
    for c in courses:
        result.append({
            'id': c.id, 'name': c.name, 'price': c.price,
            'teacher': {
                'id': c.teacher.id,
                'username': c.teacher.username,
                'fullname': f"{c.teacher.first_name} {c.teacher.last_name}"
            }
        })
    return JsonResponse(result, safe=False)

def courseStatOld(request):
    stats = Course.objects.aggregate(
        max_price=Max('price'), min_price=Min('price'), avg_price=Avg('price')
    )
    return JsonResponse({'course_count': Course.objects.count(), 'stats': stats}, safe=False)

def courseMemberStat(request):
    # Filter course mengandung kata 'python' & hitung jumlah member
    courses = Course.objects.filter(description__icontains='python')\
                            .annotate(member_num=Count('coursemember'))
    data = [{'id': c.id, 'name': c.name, 'member_count': c.member_num} for c in courses]
    return JsonResponse({'data_count': len(data), 'data': data}, safe=False)

# ✅ TUGAS 7.2a: Course Statistik
def courseStat(request):
    courses = Course.objects.all()
    
    # 1. Agregasi harga
    stats = courses.aggregate(
        max_price=Max('price'),
        min_price=Min('price'),
        avg_price=Avg('price')
    )
    
    # 2. Course termurah & termahal
    cheapest = Course.objects.filter(price=stats['min_price'])
    expensive = Course.objects.filter(price=stats['max_price'])
    
    # 3. Course terpopuler & paling sepi (berdasarkan jumlah member)
    popular = Course.objects.annotate(member_count=Count('coursemember')) \
                            .order_by('-member_count')[:5]
    unpopular = Course.objects.annotate(member_count=Count('coursemember')) \
                              .order_by('member_count')[:5]

    return JsonResponse({
        'course_count': courses.count(),
        'courses': stats,
        'cheapest': serializers.serialize('python', cheapest),
        'expensive': serializers.serialize('python', expensive),
        'popular': serializers.serialize('python', popular),
        'unpopular': serializers.serialize('python', unpopular)
    }, safe=False)

# ✅ TUGAS 7.2b: User Statistik
def userStats(request):
    non_admin = User.objects.exclude(is_superuser=True)
    with_courses = User.objects.filter(course__isnull=False).distinct()
    without_courses = User.objects.filter(course__isnull=True).exclude(is_superuser=True)
    
    # Rata-rata course per pengajar
    total_courses = Course.objects.count()
    count_teachers = with_courses.count()
    avg_courses = round(total_courses / count_teachers, 2) if count_teachers > 0 else 0

    # Top User (pengajar dengan course terbanyak)
    top_user_qs = User.objects.filter(course__isnull=False) \
                              .annotate(num_courses=Count('course')) \
                              .order_by('-num_courses').first()
    
    top_user_data = None
    if top_user_qs:
        top_user_data = {
            "id": top_user_qs.id,
            "username": top_user_qs.username,
            "email": top_user_qs.email,
            "total_courses": top_user_qs.num_courses
        }

    return JsonResponse({
        "total_non_admin_users": non_admin.count(),
        "total_users_with_courses": with_courses.count(),
        "total_users_without_courses": without_courses.count(),
        "average_courses_per_user": avg_courses,
        "top_user": top_user_data,
        "users_no_courses": list(without_courses.values('id', 'username', 'email'))
    }, safe=False)