import os
import sys
import csv
import django

# Setup Django Environment
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simplelms.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Course, CourseMember

def import_data():
    print("🚀 Starting CSV Import...")

    # 1. Import Users
    with open('./csv_data/user-data.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not User.objects.filter(username=row['username']).exists():
                User.objects.create_user(
                    username=row['username'],
                    email=row['email'],
                    password=row['password']
                )
                print(f"✅ User created: {row['username']}")

    # 2. Import Courses
    with open('./csv_data/course-data.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not Course.objects.filter(name=row['name']).exists():
                teacher = User.objects.get(pk=int(row['teacher']))
                Course.objects.create(
                    name=row['name'],
                    description=row['description'],
                    price=int(row['price']),
                    teacher=teacher
                )
                print(f"✅ Course created: {row['name']}")

    # 3. Import Members
    with open('./csv_data/member-data.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not CourseMember.objects.filter(
                course_id_id=int(row['course_id']),
                user_id_id=int(row['user_id'])
            ).exists():
                CourseMember.objects.create(
                    course_id=Course.objects.get(pk=int(row['course_id'])),
                    user_id=User.objects.get(pk=int(row['user_id'])),
                    roles=row['roles']
                )
                print(f"✅ Member added: Course {row['course_id']} -> User {row['user_id']}")

    print("🎉 CSV Import Finished!")

if __name__ == "__main__":
    import_data()