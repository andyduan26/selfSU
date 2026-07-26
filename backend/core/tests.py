from django.test import TestCase
from django.core import mail
from django.utils import timezone
from unittest.mock import patch
from django.test import override_settings

from accounts.models import User
from .models import Course, CourseChapter, CourseLesson, Favorite, Income, Order, TeacherApplication, TeacherProfile, Withdraw


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


class TeacherCourseAPITests(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(
            username='course_teacher',
            nickname='课程老师',
            email='course_teacher@example.com',
            phone='13200132000',
            password='StrongPass123',
        )
        self.other_user = User.objects.create_user(
            username='other_teacher',
            nickname='其他老师',
            email='other_teacher@example.com',
            phone='13100131000',
            password='StrongPass123',
        )
        self.student = User.objects.create_user(
            username='course_student',
            nickname='课程学员',
            email='course_student@example.com',
            phone='13000130000',
            password='StrongPass123',
        )
        self.teacher = TeacherProfile.objects.create(user=self.teacher_user, display_name='课程老师')
        self.other_teacher = TeacherProfile.objects.create(user=self.other_user, display_name='其他老师')

    def authenticate(self, username):
        response = self.client.post('/api/auth/login/', data={
            'username': username,
            'password': 'StrongPass123',
        }, content_type='application/json')
        self.client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {response.json()['data']['access']}"

    def test_only_certified_teacher_can_create_nested_course_pending_review(self):
        self.authenticate('course_student')
        denied_response = self.client.post('/api/teacher/courses/', data={}, content_type='application/json')
        self.assertEqual(denied_response.status_code, 403)

        self.authenticate('course_teacher')
        response = self.client.post('/api/teacher/courses/', data={
            'title': '东方器物课',
            'category': '美学',
            'price': '299.00',
            'summary': '从器物理解东方审美',
            'suitable_audience': '设计师、品牌主理人',
            'chapters': [
                {
                    'title': '第一章',
                    'sort_order': 1,
                    'lessons': [
                        {'title': '试看导论', 'is_trial': True, 'sort_order': 1},
                        {'title': '正式课程', 'is_trial': False, 'sort_order': 2},
                    ],
                },
            ],
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        data = response.json()['data']
        self.assertEqual(data['audit_status'], Course.AUDIT_PENDING)
        self.assertEqual(data['publish_status'], Course.PUBLISH_DRAFT)
        self.assertEqual(data['chapters'][0]['lessons'][0]['title'], '试看导论')
        self.assertEqual(Course.objects.get(id=data['id']).teacher, self.teacher)

    def test_teacher_can_list_update_and_delete_only_own_courses(self):
        own_course = Course.objects.create(
            teacher=self.teacher,
            title='自己的课',
            category='美学',
            price='99.00',
            suitable_audience='普通用户',
        )
        other_course = Course.objects.create(
            teacher=self.other_teacher,
            title='别人的课',
            category='美学',
            price='99.00',
            suitable_audience='普通用户',
        )

        self.authenticate('course_teacher')
        list_response = self.client.get('/api/teacher/courses/')
        self.assertEqual([item['title'] for item in list_response.json()['data']], ['自己的课'])

        update_response = self.client.put(f'/api/teacher/courses/{own_course.id}/', data={
            'title': '更新后的课',
            'category': '文化',
            'price': '129.00',
            'summary': '更新简介',
            'suitable_audience': '进阶用户',
            'chapters': [
                {'title': '更新章节', 'sort_order': 1, 'lessons': [{'title': '更新小节', 'sort_order': 1, 'is_trial': True}]},
            ],
        }, content_type='application/json')
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(Course.objects.get(id=own_course.id).chapters.count(), 1)

        forbidden_response = self.client.delete(f'/api/teacher/courses/{other_course.id}/')
        self.assertEqual(forbidden_response.status_code, 404)

        delete_response = self.client.delete(f'/api/teacher/courses/{own_course.id}/')
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Course.objects.filter(id=own_course.id).exists())

    def test_public_courses_only_returns_admin_approved_published_courses(self):
        approved = Course.objects.create(
            teacher=self.teacher,
            title='已通过课程',
            category='美学',
            price='99.00',
            suitable_audience='普通用户',
            audit_status=Course.AUDIT_APPROVED,
            publish_status=Course.PUBLISH_PUBLISHED,
        )
        Course.objects.create(
            teacher=self.teacher,
            title='待审核课程',
            category='美学',
            price='99.00',
            suitable_audience='普通用户',
        )

        response = self.client.get('/api/courses/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.json()['data']], [approved.id])

    def test_public_course_detail_teacher_page_and_play_permission(self):
        course = Course.objects.create(
            teacher=self.teacher,
            title='公开视频课',
            cover='r2://covers/public.jpg',
            category='美学',
            price='99.00',
            suitable_audience='普通用户',
            audit_status=Course.AUDIT_APPROVED,
            publish_status=Course.PUBLISH_PUBLISHED,
        )
        chapter = CourseChapter.objects.create(course=course, title='第一章', sort_order=1)
        trial = CourseLesson.objects.create(chapter=chapter, title='试看', video_file='r2://trial.mp4', is_trial=True, sort_order=1)
        paid = CourseLesson.objects.create(chapter=chapter, title='正课', video_file='r2://paid.mp4', is_trial=False, sort_order=2)

        detail_response = self.client.get(f'/api/courses/{course.id}/')
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()['data']['teacher']['display_name'], '课程老师')
        self.assertEqual(detail_response.json()['data']['chapters'][0]['lessons'][1]['can_play'], False)

        teacher_response = self.client.get(f'/api/teachers/{self.teacher.id}/')
        self.assertEqual(teacher_response.status_code, 200)
        self.assertEqual(teacher_response.json()['data']['courses'][0]['id'], course.id)

        trial_response = self.client.get(f'/api/lessons/{trial.id}/play/')
        self.assertEqual(trial_response.status_code, 200)
        self.assertTrue(trial_response.json()['data']['can_play'])

        paid_denied_response = self.client.get(f'/api/lessons/{paid.id}/play/')
        self.assertEqual(paid_denied_response.status_code, 403)

        Order.objects.create(
            order_no='PLAY202607260001',
            user=self.student,
            course=course,
            amount='99.00',
            pay_status=Order.PAY_PAID,
            payment_method=Order.METHOD_ALIPAY,
            paid_at=timezone.now(),
        )
        self.authenticate('course_student')
        paid_allowed_response = self.client.get(f'/api/lessons/{paid.id}/play/')
        self.assertEqual(paid_allowed_response.status_code, 200)
        self.assertEqual(paid_allowed_response.json()['data']['video_file'], 'r2://paid.mp4')

    @patch('core.views.create_r2_presigned_upload')
    def test_certified_teacher_can_request_r2_presigned_upload(self, mock_presign):
        mock_presign.return_value = {
            'upload_url': 'https://r2.example.com/upload',
            'public_url': 'https://cdn.example.com/covers/demo.jpg',
            'object_key': 'course-covers/demo.jpg',
        }
        self.authenticate('course_teacher')

        response = self.client.post('/api/uploads/r2/presign/', data={
            'filename': 'demo.jpg',
            'content_type': 'image/jpeg',
            'folder': 'course-covers',
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['public_url'], 'https://cdn.example.com/covers/demo.jpg')
        mock_presign.assert_called_once()

    def test_lesson_play_response_includes_reserved_media_fields(self):
        course = Course.objects.create(
            teacher=self.teacher,
            title='媒体字段课程',
            cover='https://cdn.example.com/cover.jpg',
            category='美学',
            price='99.00',
            suitable_audience='普通用户',
            audit_status=Course.AUDIT_APPROVED,
            publish_status=Course.PUBLISH_PUBLISHED,
        )
        chapter = CourseChapter.objects.create(course=course, title='第一章', sort_order=1)
        lesson = CourseLesson.objects.create(
            chapter=chapter,
            title='试看',
            video_file='https://cdn.example.com/video.mp4',
            hls_url='https://cdn.example.com/video/index.m3u8',
            duration=120,
            resolution='1080p',
            transcode_status=CourseLesson.TRANSCODE_READY,
            is_trial=True,
            sort_order=1,
        )

        response = self.client.get(f'/api/lessons/{lesson.id}/play/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['hls_url'], 'https://cdn.example.com/video/index.m3u8')
        self.assertEqual(response.json()['data']['duration'], 120)
        self.assertEqual(response.json()['data']['resolution'], '1080p')
        self.assertEqual(response.json()['data']['transcode_status'], CourseLesson.TRANSCODE_READY)


class CourseOrderAPITests(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(
            username='order_teacher',
            nickname='订单老师',
            email='order_teacher@example.com',
            phone='12600126000',
            password='StrongPass123',
        )
        self.student = User.objects.create_user(
            username='order_student',
            nickname='订单学员',
            email='order_student@example.com',
            phone='12500125000',
            password='StrongPass123',
        )
        self.teacher = TeacherProfile.objects.create(user=self.teacher_user, display_name='订单老师')

    def authenticate(self, username):
        response = self.client.post('/api/auth/login/', data={
            'username': username,
            'password': 'StrongPass123',
        }, content_type='application/json')
        self.client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {response.json()['data']['access']}"

    def create_course_with_lessons(self, price):
        course = Course.objects.create(
            teacher=self.teacher,
            title=f'{price}课程',
            category='订单',
            price=price,
            suitable_audience='学员',
            audit_status=Course.AUDIT_APPROVED,
            publish_status=Course.PUBLISH_PUBLISHED,
        )
        chapter = CourseChapter.objects.create(course=course, title='第一章', sort_order=1)
        trial = CourseLesson.objects.create(chapter=chapter, title='试看', is_trial=True, sort_order=1)
        paid = CourseLesson.objects.create(chapter=chapter, title='正课', is_trial=False, sort_order=2)
        return course, trial, paid

    def test_buying_free_course_creates_paid_order_and_unlocks_full_lessons(self):
        course, trial, paid = self.create_course_with_lessons('0.00')
        self.authenticate('order_student')

        response = self.client.post(f'/api/courses/{course.id}/orders/', data={
            'payment_method': Order.METHOD_ALIPAY,
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['data']['pay_status'], Order.PAY_PAID)
        self.assertEqual(response.json()['data']['amount'], '0.00')
        self.assertTrue(response.json()['data']['order_no'])

        play_response = self.client.get(f'/api/lessons/{paid.id}/play/')
        self.assertEqual(play_response.status_code, 200)
        self.assertTrue(play_response.json()['data']['can_play'])

    def test_buying_paid_course_creates_pending_order_until_payment_succeeds(self):
        course, trial, paid = self.create_course_with_lessons('199.00')
        self.authenticate('order_student')

        response = self.client.post(f'/api/courses/{course.id}/orders/', data={
            'payment_method': Order.METHOD_WECHAT,
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['data']['pay_status'], Order.PAY_PENDING)
        self.assertEqual(response.json()['data']['payment_method'], Order.METHOD_WECHAT)
        denied_response = self.client.get(f'/api/lessons/{paid.id}/play/')
        self.assertEqual(denied_response.status_code, 403)

        order = Order.objects.get(order_no=response.json()['data']['order_no'])
        order.mark_paid()
        allowed_response = self.client.get(f'/api/lessons/{paid.id}/play/')
        self.assertEqual(allowed_response.status_code, 200)
        income = Income.objects.get(order=order)
        self.assertEqual(str(income.gross_amount), '199.00')
        self.assertEqual(str(income.platform_amount), '39.80')
        self.assertEqual(str(income.teacher_amount), '159.20')

    def test_teacher_income_summary_counts_total_available_and_withdrawn_amounts(self):
        course, trial, paid = self.create_course_with_lessons('199.00')
        paid_order = Order.objects.create(
            order_no='INCOMEORDER202607270001',
            user=self.student,
            course=course,
            amount='199.00',
            pay_status=Order.PAY_PAID,
            payment_method=Order.METHOD_ALIPAY,
            paid_at=timezone.now(),
        )
        Income.objects.create(
            teacher=self.teacher,
            course=course,
            order=paid_order,
            gross_amount='199.00',
            platform_amount='39.80',
            teacher_amount='159.20',
        )
        Withdraw.objects.create(
            teacher=self.teacher,
            amount='59.20',
            account_name='订单老师',
            account_no='teacher@example.com',
            status=Withdraw.STATUS_APPROVED,
            paid_at=timezone.now(),
        )

        self.authenticate('order_teacher')
        response = self.client.get('/api/teacher/income/summary/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['total_income'], '159.20')
        self.assertEqual(response.json()['data']['withdrawn_amount'], '59.20')
        self.assertEqual(response.json()['data']['available_amount'], '100.00')

    def test_teacher_can_create_withdraw_request_within_available_balance(self):
        course, trial, paid = self.create_course_with_lessons('199.00')
        paid_order = Order.objects.create(
            order_no='WITHDRAWORDER202607270001',
            user=self.student,
            course=course,
            amount='199.00',
            pay_status=Order.PAY_PAID,
            payment_method=Order.METHOD_ALIPAY,
            paid_at=timezone.now(),
        )
        Income.objects.create(
            teacher=self.teacher,
            course=course,
            order=paid_order,
            gross_amount='199.00',
            platform_amount='39.80',
            teacher_amount='159.20',
        )

        self.authenticate('order_teacher')
        response = self.client.post('/api/teacher/withdraws/', data={
            'amount': '100.00',
            'account_name': '订单老师',
            'account_no': 'teacher@example.com',
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['data']['status'], Withdraw.STATUS_PENDING)
        self.assertEqual(Withdraw.objects.get().amount, 100)

    def test_teacher_cannot_withdraw_more_than_available_balance(self):
        self.authenticate('order_teacher')
        response = self.client.post('/api/teacher/withdraws/', data={
            'amount': '100.00',
            'account_name': '订单老师',
            'account_no': 'teacher@example.com',
        }, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('可提现余额不足', response.json()['message'])

    def test_user_and_teacher_can_read_their_order_lists(self):
        course, trial, paid = self.create_course_with_lessons('99.00')
        other_teacher_user = User.objects.create_user(
            username='other_order_teacher',
            nickname='其他订单老师',
            email='other_order_teacher@example.com',
            phone='12400124000',
            password='StrongPass123',
        )
        other_teacher = TeacherProfile.objects.create(user=other_teacher_user, display_name='其他订单老师')
        other_course = Course.objects.create(
            teacher=other_teacher,
            title='别人的订单课程',
            category='订单',
            price='99.00',
            audit_status=Course.AUDIT_APPROVED,
            publish_status=Course.PUBLISH_PUBLISHED,
        )
        order = Order.objects.create(
            order_no='MYORDER202607260001',
            user=self.student,
            course=course,
            amount='99.00',
            pay_status=Order.PAY_PAID,
            payment_method=Order.METHOD_ALIPAY,
            paid_at=timezone.now(),
        )
        Order.objects.create(
            order_no='OTHERORDER202607260001',
            user=self.student,
            course=other_course,
            amount='99.00',
            pay_status=Order.PAY_PAID,
            payment_method=Order.METHOD_ALIPAY,
            paid_at=timezone.now(),
        )

        self.authenticate('order_student')
        my_orders_response = self.client.get('/api/orders/')
        self.assertEqual(my_orders_response.status_code, 200)
        self.assertEqual(len(my_orders_response.json()['data']), 2)

        self.authenticate('order_teacher')
        teacher_orders_response = self.client.get('/api/teacher/orders/')
        self.assertEqual(teacher_orders_response.status_code, 200)
        self.assertEqual([item['order_no'] for item in teacher_orders_response.json()['data']], [order.order_no])

    @patch('core.views.create_alipay_precreate')
    def test_alipay_precreate_returns_qr_code_for_pending_order(self, mock_precreate):
        course, trial, paid = self.create_course_with_lessons('199.00')
        self.authenticate('order_student')
        order_response = self.client.post(f'/api/courses/{course.id}/orders/', data={
            'payment_method': Order.METHOD_ALIPAY,
        }, content_type='application/json')
        order_no = order_response.json()['data']['order_no']
        mock_precreate.return_value = {'qr_code': 'https://qr.alipay.com/test', 'out_trade_no': order_no}

        response = self.client.post(f'/api/orders/{order_no}/alipay/precreate/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['qr_code'], 'https://qr.alipay.com/test')
        mock_precreate.assert_called_once()

    @override_settings(ALIPAY_APP_ID='')
    def test_alipay_precreate_returns_clear_error_when_env_missing(self):
        course, trial, paid = self.create_course_with_lessons('199.00')
        self.authenticate('order_student')
        order_response = self.client.post(f'/api/courses/{course.id}/orders/', data={
            'payment_method': Order.METHOD_ALIPAY,
        }, content_type='application/json')
        order_no = order_response.json()['data']['order_no']

        response = self.client.post(f'/api/orders/{order_no}/alipay/precreate/')

        self.assertEqual(response.status_code, 500)
        self.assertIn('支付宝环境变量未配置完整', response.json()['message'])

    def test_order_status_polling_returns_latest_payment_status(self):
        course, trial, paid = self.create_course_with_lessons('199.00')
        self.authenticate('order_student')
        order_response = self.client.post(f'/api/courses/{course.id}/orders/', data={
            'payment_method': Order.METHOD_ALIPAY,
        }, content_type='application/json')
        order = Order.objects.get(order_no=order_response.json()['data']['order_no'])

        pending_response = self.client.get(f'/api/orders/{order.order_no}/status/')
        self.assertEqual(pending_response.json()['data']['pay_status'], Order.PAY_PENDING)

        order.mark_paid()
        paid_response = self.client.get(f'/api/orders/{order.order_no}/status/')
        self.assertEqual(paid_response.json()['data']['pay_status'], Order.PAY_PAID)

    @patch('core.views.verify_alipay_notify')
    def test_alipay_notify_marks_order_paid_after_signature_verified(self, mock_verify):
        mock_verify.return_value = True
        course, trial, paid = self.create_course_with_lessons('199.00')
        self.authenticate('order_student')
        order_response = self.client.post(f'/api/courses/{course.id}/orders/', data={
            'payment_method': Order.METHOD_ALIPAY,
        }, content_type='application/json')
        order_no = order_response.json()['data']['order_no']

        notify_response = self.client.post('/api/alipay/notify/', data={
            'out_trade_no': order_no,
            'trade_status': 'TRADE_SUCCESS',
            'sign': 'mock-signature',
            'sign_type': 'RSA2',
        })

        self.assertEqual(notify_response.status_code, 200)
        self.assertEqual(notify_response.content.decode(), 'success')
        self.assertEqual(Order.objects.get(order_no=order_no).pay_status, Order.PAY_PAID)

# Create your tests here.
