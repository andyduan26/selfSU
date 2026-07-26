from django.test import TestCase
from django.core import mail

from accounts.models import User
from .models import Course, CourseChapter, CourseLesson, Favorite, Income, Order, TeacherApplication, TeacherProfile


class HealthCheckAPITests(TestCase):
    def test_health_check_returns_unified_json(self):
        response = self.client.get('/api/health/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'code': 0,
            'message': 'success',
            'data': {
                'service': '东方知识库 API',
                'status': 'ok',
            },
        })


class JWTEndpointTests(TestCase):
    def test_token_endpoint_is_mounted(self):
        response = self.client.post('/api/auth/token/', data={}, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.json())
        self.assertIn('password', response.json())


class CoreModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='teacher02',
            nickname='核心老师',
            email='teacher02@example.com',
            phone='13600136000',
            password='StrongPass123',
        )
        self.student = User.objects.create_user(
            username='student02',
            nickname='核心学员',
            email='student02@example.com',
            phone='13500135000',
            password='StrongPass123',
        )
        self.teacher = TeacherProfile.objects.create(user=self.user, display_name='核心老师')

    def test_course_chapter_lesson_order_income_and_favorite_models(self):
        course = Course.objects.create(
            teacher=self.teacher,
            title='东方美学入门',
            summary='课程简介',
            price='199.00',
            category='美学',
            audit_status=Course.AUDIT_APPROVED,
            publish_status=Course.PUBLISH_PUBLISHED,
            has_trial=True,
            sort_weight=10,
        )
        chapter = CourseChapter.objects.create(course=course, title='第一章', sort_order=1)
        lesson = CourseLesson.objects.create(chapter=chapter, title='试看小节', is_trial=True, sort_order=1)
        order = Order.objects.create(
            order_no='ORDER202607260001',
            user=self.student,
            course=course,
            amount='199.00',
            pay_status=Order.PAY_PAID,
            payment_method=Order.METHOD_ALIPAY,
        )
        income = Income.objects.create(
            teacher=self.teacher,
            course=course,
            order=order,
            gross_amount='199.00',
            platform_amount='39.80',
            teacher_amount='159.20',
        )
        favorite = Favorite.objects.create(user=self.student, course=course)

        self.assertIsInstance(course.id, int)
        self.assertTrue(course.created_at)
        self.assertEqual(course.chapters.first(), chapter)
        self.assertEqual(chapter.lessons.first(), lesson)
        self.assertEqual(order.pay_status, Order.PAY_PAID)
        self.assertEqual(str(income.platform_amount), '39.80')
        self.assertEqual(favorite.course, course)


class TeacherApplicationAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='applicant01',
            nickname='认证用户',
            email='applicant01@example.com',
            phone='13400134000',
            password='StrongPass123',
        )
        login_response = self.client.post('/api/auth/login/', data={
            'username': 'applicant01',
            'password': 'StrongPass123',
        }, content_type='application/json')
        self.client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {login_response.json()['data']['access']}"

    def test_user_can_submit_teacher_application_and_read_pending_status(self):
        response = self.client.post('/api/teacher/applications/', data={
            'real_name': '张老师',
            'phone': '13400134000',
            'email': 'teacher-result@example.com',
            'bio': '十年教学经验',
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['data']['status'], TeacherApplication.STATUS_PENDING)
        self.assertEqual(response.json()['data']['notice'], '耐心等待2-3个工作日，结果会邮箱通知。')

        status_response = self.client.get('/api/teacher/status/')
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()['data']['application_status'], TeacherApplication.STATUS_PENDING)
        self.assertFalse(status_response.json()['data']['is_teacher'])

    def test_approving_application_creates_teacher_profile_and_sends_email(self):
        application = TeacherApplication.objects.create(
            user=self.user,
            real_name='张老师',
            phone='13400134000',
            email='teacher-result@example.com',
            bio='十年教学经验',
        )

        application.approve('欢迎成为认证教师')

        self.assertTrue(TeacherProfile.objects.filter(user=self.user, application=application).exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('审核通过', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['teacher-result@example.com'])

    def test_rejecting_application_sends_email_without_creating_teacher_profile(self):
        application = TeacherApplication.objects.create(
            user=self.user,
            real_name='张老师',
            phone='13400134000',
            email='teacher-result@example.com',
        )

        application.reject('资料不完整')

        self.assertFalse(TeacherProfile.objects.filter(user=self.user).exists())
        self.assertEqual(application.status, TeacherApplication.STATUS_REJECTED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('审核未通过', mail.outbox[0].subject)

# Create your tests here.
