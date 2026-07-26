from django.test import TestCase

from accounts.models import User
from .models import Course, CourseChapter, CourseLesson, Favorite, Income, Order, TeacherProfile


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

# Create your tests here.
