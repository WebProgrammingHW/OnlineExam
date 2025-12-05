# accounts/management/commands/create_test_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from accounts.models import User
from questions.models import Exam, Question, Choice
from attempts.models import Attempt, Answer
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Creates test data for the Online Exam system'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')

        # Create Teachers
        teachers = []
        teacher_data = [
            {'username': 'teacher1', 'first_name': 'علی', 'last_name': 'محمدی', 'email': 'teacher1@test.com'},
            {'username': 'teacher2', 'first_name': 'مریم', 'last_name': 'احمدی', 'email': 'teacher2@test.com'},
        ]
        
        for data in teacher_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'role': 'teacher',
                    'phone_number': '09121234567'
                }
            )
            if created:
                user.set_password('test1234')
                user.save()
                self.stdout.write(f'  Created teacher: {user.username}')
            teachers.append(user)

        # Create Students
        students = []
        student_data = [
            {'username': 'student1', 'first_name': 'رضا', 'last_name': 'کریمی', 'email': 'student1@test.com'},
            {'username': 'student2', 'first_name': 'زهرا', 'last_name': 'حسینی', 'email': 'student2@test.com'},
            {'username': 'student3', 'first_name': 'محمد', 'last_name': 'رضایی', 'email': 'student3@test.com'},
            {'username': 'student4', 'first_name': 'فاطمه', 'last_name': 'علوی', 'email': 'student4@test.com'},
        ]
        
        for data in student_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'role': 'student',
                    'phone_number': '09351234567'
                }
            )
            if created:
                user.set_password('test1234')
                user.save()
                self.stdout.write(f'  Created student: {user.username}')
            students.append(user)

        # Create Exams
        exams_data = [
            {
                'title': 'آزمون میان‌ترم ریاضی ۱',
                'topic': 'ریاضی',
                'description': 'این آزمون شامل مباحث حد و پیوستگی می‌باشد.',
                'duration_minutes': 60,
                'total_score': 20,
                'teacher': teachers[0],
                'published': True,
                'start_at': timezone.now() - timedelta(days=1),
            },
            {
                'title': 'آزمون برنامه‌نویسی پایتون',
                'topic': 'برنامه‌نویسی',
                'description': 'آزمون مقدماتی پایتون شامل متغیرها، حلقه‌ها و توابع',
                'duration_minutes': 45,
                'total_score': 15,
                'teacher': teachers[0],
                'published': True,
                'start_at': timezone.now() - timedelta(hours=2),
            },
            {
                'title': 'آزمون پایان‌ترم فیزیک',
                'topic': 'فیزیک',
                'description': 'آزمون جامع فیزیک ۱',
                'duration_minutes': 90,
                'total_score': 20,
                'teacher': teachers[1],
                'published': True,
                'start_at': timezone.now() + timedelta(days=7),
            },
            {
                'title': 'آزمون آزمایشی شیمی',
                'topic': 'شیمی',
                'description': 'آزمون تمرینی فصل اول',
                'duration_minutes': 30,
                'total_score': 10,
                'teacher': teachers[1],
                'published': False,
                'start_at': timezone.now() + timedelta(days=14),
            },
        ]

        exams = []
        for data in exams_data:
            exam, created = Exam.objects.get_or_create(
                title=data['title'],
                teacher=data['teacher'],
                defaults={
                    'topic': data['topic'],
                    'description': data['description'],
                    'duration_minutes': data['duration_minutes'],
                    'total_score': data['total_score'],
                    'published': data['published'],
                    'start_at': data['start_at'],
                }
            )
            if created:
                self.stdout.write(f'  Created exam: {exam.title}')
            exams.append(exam)

        # Create Questions for first exam (Math)
        math_exam = exams[0]
        math_questions = [
            {
                'text': 'حد تابع f(x) = (x² - 1)/(x - 1) وقتی x به ۱ میل می‌کند چقدر است؟',
                'qtype': 'short',
                'max_score': 4,
                'auto_grade_regex': '2|۲|دو',
                'order': 1,
            },
            {
                'text': 'کدام گزینه در مورد پیوستگی تابع صحیح است؟',
                'qtype': 'mcq',
                'max_score': 4,
                'order': 2,
                'choices': [
                    {'text': 'تابع پیوسته در هر نقطه مشتق‌پذیر است', 'is_correct': False},
                    {'text': 'تابع مشتق‌پذیر در هر نقطه پیوسته است', 'is_correct': True},
                    {'text': 'پیوستگی و مشتق‌پذیری معادل هستند', 'is_correct': False},
                    {'text': 'هیچکدام', 'is_correct': False},
                ]
            },
            {
                'text': 'مشتق تابع f(x) = x³ + 2x را محاسبه کنید.',
                'qtype': 'short',
                'max_score': 4,
                'auto_grade_regex': '3x²\s*\+\s*2|3x\^2\s*\+\s*2|۳x².*۲',
                'order': 3,
            },
            {
                'text': 'انتگرال ∫2x dx برابر است با:',
                'qtype': 'mcq',
                'max_score': 4,
                'order': 4,
                'choices': [
                    {'text': 'x² + C', 'is_correct': True},
                    {'text': '2x² + C', 'is_correct': False},
                    {'text': 'x + C', 'is_correct': False},
                    {'text': '2 + C', 'is_correct': False},
                ]
            },
            {
                'text': 'فایل حل تمرین خود را آپلود کنید.',
                'qtype': 'file',
                'max_score': 4,
                'order': 5,
            },
        ]

        for q_data in math_questions:
            choices_data = q_data.pop('choices', [])
            question, created = Question.objects.get_or_create(
                exam=math_exam,
                text=q_data['text'],
                defaults=q_data
            )
            if created:
                self.stdout.write(f'    Created question: {question.text[:30]}...')
                for i, c_data in enumerate(choices_data):
                    Choice.objects.create(
                        question=question,
                        text=c_data['text'],
                        is_correct=c_data['is_correct'],
                        order=i
                    )

        # Create Questions for Python exam
        python_exam = exams[1]
        python_questions = [
            {
                'text': 'خروجی print(type(3.14)) چیست؟',
                'qtype': 'mcq',
                'max_score': 3,
                'order': 1,
                'choices': [
                    {'text': "<class 'int'>", 'is_correct': False},
                    {'text': "<class 'float'>", 'is_correct': True},
                    {'text': "<class 'str'>", 'is_correct': False},
                    {'text': "<class 'number'>", 'is_correct': False},
                ]
            },
            {
                'text': 'تابعی بنویسید که فاکتوریل یک عدد را محاسبه کند.',
                'qtype': 'short',
                'max_score': 5,
                'order': 2,
            },
            {
                'text': 'کدام کلمه کلیدی برای تعریف تابع استفاده می‌شود؟',
                'qtype': 'short',
                'max_score': 2,
                'auto_grade_regex': 'def',
                'order': 3,
            },
            {
                'text': 'لیست در پایتون تغییرپذیر (mutable) است.',
                'qtype': 'mcq',
                'max_score': 2,
                'order': 4,
                'choices': [
                    {'text': 'صحیح', 'is_correct': True},
                    {'text': 'غلط', 'is_correct': False},
                ]
            },
            {
                'text': 'کد خود را به صورت فایل .py آپلود کنید.',
                'qtype': 'file',
                'max_score': 3,
                'order': 5,
            },
        ]

        for q_data in python_questions:
            choices_data = q_data.pop('choices', [])
            question, created = Question.objects.get_or_create(
                exam=python_exam,
                text=q_data['text'],
                defaults=q_data
            )
            if created:
                self.stdout.write(f'    Created question: {question.text[:30]}...')
                for i, c_data in enumerate(choices_data):
                    Choice.objects.create(
                        question=question,
                        text=c_data['text'],
                        is_correct=c_data['is_correct'],
                        order=i
                    )

        # Create some Attempts
        # Student 1 completed math exam
        attempt1, created = Attempt.objects.get_or_create(
            student=students[0],
            exam=math_exam,
            defaults={
                'start_time': timezone.now() - timedelta(hours=5),
                'submitted_at': timezone.now() - timedelta(hours=4),
                'status': 'submitted',
            }
        )
        if created:
            self.stdout.write(f'  Created attempt: {students[0].username} - {math_exam.title}')
            # Create answers
            for question in math_exam.questions.all():
                answer = Answer.objects.create(
                    attempt=attempt1,
                    question=question,
                )
                if question.qtype == 'short':
                    answer.text_answer = '2' if question.order == 1 else '3x² + 2'
                    answer.save()
                elif question.qtype == 'mcq':
                    correct_choice = question.choices.filter(is_correct=True).first()
                    if correct_choice:
                        answer.selected_choice = correct_choice
                        answer.save()

        # Student 2 completed and graded python exam
        attempt2, created = Attempt.objects.get_or_create(
            student=students[1],
            exam=python_exam,
            defaults={
                'start_time': timezone.now() - timedelta(hours=3),
                'submitted_at': timezone.now() - timedelta(hours=2),
                'status': 'graded',
                'total_score': 12,
            }
        )
        if created:
            self.stdout.write(f'  Created attempt: {students[1].username} - {python_exam.title}')
            for question in python_exam.questions.all():
                answer = Answer.objects.create(
                    attempt=attempt2,
                    question=question,
                    score=question.max_score * 0.8,
                    is_auto_graded=True,
                    graded_at=timezone.now() - timedelta(hours=1),
                )
                if question.qtype == 'mcq':
                    correct_choice = question.choices.filter(is_correct=True).first()
                    if correct_choice:
                        answer.selected_choice = correct_choice
                        answer.save()

        # Create Notifications
        notifications_data = [
            {
                'user': students[1],
                'notif_type': 'score',
                'title': f'نمره آزمون {python_exam.title}',
                'message': f'نمره شما: 12 از 15',
            },
            {
                'user': students[0],
                'notif_type': 'system',
                'title': 'خوش آمدید!',
                'message': 'به سامانه آزمون آنلاین خوش آمدید.',
            },
        ]

        for n_data in notifications_data:
            Notification.objects.get_or_create(
                user=n_data['user'],
                title=n_data['title'],
                defaults={
                    'notif_type': n_data['notif_type'],
                    'message': n_data['message'],
                    'channel': 'in_app',
                }
            )

        self.stdout.write(self.style.SUCCESS('\n✅ Test data created successfully!'))
        self.stdout.write('\nTest Accounts:')
        self.stdout.write('  Teachers: teacher1, teacher2 (password: test1234)')
        self.stdout.write('  Students: student1, student2, student3, student4 (password: test1234)')