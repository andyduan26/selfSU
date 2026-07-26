from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from decimal import Decimal


class TimeStampedModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True


class TeacherApplication(TimeStampedModel):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, '待审核'),
        (STATUS_APPROVED, '已通过'),
        (STATUS_REJECTED, '已拒绝'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='申请用户', on_delete=models.CASCADE, related_name='teacher_applications')
    real_name = models.CharField('真实姓名', max_length=50)
    phone = models.CharField('联系电话', max_length=20)
    email = models.EmailField('联系邮箱')
    bio = models.TextField('申请说明', blank=True)
    certificate_file = models.FileField('资质文件', upload_to='teacher/certificates/', blank=True)
    status = models.CharField('审核状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    review_note = models.TextField('审核备注', blank=True)

    class Meta:
        verbose_name = '教师认证申请'
        verbose_name_plural = '教师认证申请'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.real_name} - {self.get_status_display()}'

    def approve(self, review_note=''):
        self.status = self.STATUS_APPROVED
        self.review_note = review_note
        self.save(update_fields=['status', 'review_note', 'updated_at'])
        TeacherProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'application': self,
                'display_name': self.user.nickname or self.real_name,
                'bio': self.bio,
            },
        )
        self.send_review_email('东方知识库教师认证审核通过', '您的教师认证申请已审核通过。')

    def reject(self, review_note=''):
        self.status = self.STATUS_REJECTED
        self.review_note = review_note
        self.save(update_fields=['status', 'review_note', 'updated_at'])
        self.send_review_email('东方知识库教师认证审核未通过', f'您的教师认证申请未通过。原因：{review_note or "请补充完整资料后再次提交。"}')

    def send_review_email(self, subject, message):
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email], fail_silently=True)


class TeacherProfile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='教师用户', on_delete=models.CASCADE, related_name='teacher_profile')
    application = models.OneToOneField(TeacherApplication, verbose_name='认证申请', on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_profile')
    display_name = models.CharField('展示名称', max_length=80)
    title = models.CharField('教师头衔', max_length=100, blank=True)
    bio = models.TextField('教师简介', blank=True)
    avatar = models.FileField('头像', upload_to='teacher/avatars/', blank=True)
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        verbose_name = '教师资料'
        verbose_name_plural = '教师资料'
        ordering = ['-created_at']

    def __str__(self):
        return self.display_name


class Course(TimeStampedModel):
    AUDIT_PENDING = 'pending'
    AUDIT_APPROVED = 'approved'
    AUDIT_REJECTED = 'rejected'
    AUDIT_STATUS_CHOICES = [
        (AUDIT_PENDING, '待审核'),
        (AUDIT_APPROVED, '已通过'),
        (AUDIT_REJECTED, '已拒绝'),
    ]

    PUBLISH_DRAFT = 'draft'
    PUBLISH_PUBLISHED = 'published'
    PUBLISH_OFFLINE = 'offline'
    PUBLISH_STATUS_CHOICES = [
        (PUBLISH_DRAFT, '草稿'),
        (PUBLISH_PUBLISHED, '已发布'),
        (PUBLISH_OFFLINE, '已下架'),
    ]

    teacher = models.ForeignKey(TeacherProfile, verbose_name='教师', on_delete=models.PROTECT, related_name='courses')
    cover = models.CharField('课程封面', max_length=500, blank=True)
    title = models.CharField('课程标题', max_length=120)
    summary = models.TextField('课程简介', blank=True)
    suitable_audience = models.TextField('适合人群', blank=True)
    price = models.DecimalField('课程价格', max_digits=10, decimal_places=2, default=0)
    category = models.CharField('课程分类', max_length=60)
    audit_status = models.CharField('审核状态', max_length=20, choices=AUDIT_STATUS_CHOICES, default=AUDIT_PENDING)
    audit_reject_reason = models.TextField('审核拒绝原因', blank=True)
    publish_status = models.CharField('发布状态', max_length=20, choices=PUBLISH_STATUS_CHOICES, default=PUBLISH_DRAFT)
    has_trial = models.BooleanField('支持试看', default=False)
    sort_weight = models.IntegerField('排序权重', default=0)
    view_count = models.PositiveIntegerField('点播量', default=0)

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程'
        ordering = ['-sort_weight', '-created_at']

    def __str__(self):
        return self.title

    def approve(self):
        self.audit_status = self.AUDIT_APPROVED
        self.publish_status = self.PUBLISH_PUBLISHED
        self.audit_reject_reason = ''
        self.save(update_fields=['audit_status', 'publish_status', 'audit_reject_reason', 'updated_at'])

    def reject(self):
        if not self.audit_reject_reason:
            raise ValueError('审核拒绝需要填写原因')
        self.audit_status = self.AUDIT_REJECTED
        self.publish_status = self.PUBLISH_DRAFT
        self.save(update_fields=['audit_status', 'publish_status', 'updated_at'])


class CourseChapter(TimeStampedModel):
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField('章节标题', max_length=120)
    summary = models.TextField('章节简介', blank=True)
    sort_order = models.PositiveIntegerField('排序', default=0)

    class Meta:
        verbose_name = '课程章节'
        verbose_name_plural = '课程章节'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title


class CourseLesson(TimeStampedModel):
    TRANSCODE_PENDING = 'pending'
    TRANSCODE_PROCESSING = 'processing'
    TRANSCODE_READY = 'ready'
    TRANSCODE_FAILED = 'failed'
    TRANSCODE_STATUS_CHOICES = [
        (TRANSCODE_PENDING, '待转码'),
        (TRANSCODE_PROCESSING, '转码中'),
        (TRANSCODE_READY, '已完成'),
        (TRANSCODE_FAILED, '转码失败'),
    ]

    chapter = models.ForeignKey(CourseChapter, verbose_name='章节', on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField('小节标题', max_length=120)
    video_file = models.CharField('视频文件', max_length=500, blank=True)
    hls_url = models.CharField('HLS地址', max_length=500, blank=True)
    duration = models.PositiveIntegerField('视频时长秒数', default=0)
    resolution = models.CharField('视频分辨率', max_length=50, blank=True)
    transcode_status = models.CharField('转码状态', max_length=20, choices=TRANSCODE_STATUS_CHOICES, default=TRANSCODE_PENDING)
    duration_seconds = models.PositiveIntegerField('视频时长秒数', default=0)
    is_trial = models.BooleanField('是否试看', default=False)
    sort_order = models.PositiveIntegerField('排序', default=0)

    class Meta:
        verbose_name = '课程小节'
        verbose_name_plural = '课程小节'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title


class Order(TimeStampedModel):
    PAY_PENDING = 'pending'
    PAY_PAID = 'paid'
    PAY_CLOSED = 'closed'
    PAY_REFUNDED = 'refunded'
    PAY_STATUS_CHOICES = [
        (PAY_PENDING, '待支付'),
        (PAY_PAID, '已支付'),
        (PAY_CLOSED, '已关闭'),
        (PAY_REFUNDED, '已退款'),
    ]

    METHOD_ALIPAY = 'alipay'
    METHOD_WECHAT = 'wechat'
    METHOD_CHOICES = [
        (METHOD_ALIPAY, '支付宝'),
        (METHOD_WECHAT, '微信'),
    ]

    order_no = models.CharField('订单号', max_length=64, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='购买用户', on_delete=models.PROTECT, related_name='orders')
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.PROTECT, related_name='orders')
    amount = models.DecimalField('订单金额', max_digits=10, decimal_places=2)
    pay_status = models.CharField('支付状态', max_length=20, choices=PAY_STATUS_CHOICES, default=PAY_PENDING)
    payment_method = models.CharField('支付方式', max_length=20, choices=METHOD_CHOICES, blank=True)
    paid_at = models.DateTimeField('支付时间', null=True, blank=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no

    def mark_paid(self):
        self.pay_status = self.PAY_PAID
        self.paid_at = timezone.now()
        self.save(update_fields=['pay_status', 'paid_at', 'updated_at'])
        platform_amount = (self.amount * Decimal('0.20')).quantize(Decimal('0.01'))
        Income.objects.get_or_create(
            order=self,
            defaults={
                'teacher': self.course.teacher,
                'course': self.course,
                'gross_amount': self.amount,
                'platform_amount': platform_amount,
                'teacher_amount': self.amount - platform_amount,
            },
        )


class Income(TimeStampedModel):
    STATUS_PENDING = 'pending'
    STATUS_SETTLED = 'settled'
    STATUS_CHOICES = [
        (STATUS_PENDING, '待结算'),
        (STATUS_SETTLED, '已结算'),
    ]

    teacher = models.ForeignKey(TeacherProfile, verbose_name='教师', on_delete=models.PROTECT, related_name='incomes')
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.PROTECT, related_name='incomes')
    order = models.OneToOneField(Order, verbose_name='订单', on_delete=models.PROTECT, related_name='income')
    gross_amount = models.DecimalField('总收入', max_digits=10, decimal_places=2)
    platform_amount = models.DecimalField('平台分成', max_digits=10, decimal_places=2)
    teacher_amount = models.DecimalField('教师分成', max_digits=10, decimal_places=2)
    status = models.CharField('结算状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    class Meta:
        verbose_name = '收益'
        verbose_name_plural = '收益'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.teacher} - {self.teacher_amount}'


class Withdraw(TimeStampedModel):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_PAID = 'paid'
    STATUS_CHOICES = [
        (STATUS_PENDING, '待审核'),
        (STATUS_APPROVED, '已通过'),
        (STATUS_REJECTED, '已拒绝'),
        (STATUS_PAID, '已打款'),
    ]

    teacher = models.ForeignKey(TeacherProfile, verbose_name='教师', on_delete=models.PROTECT, related_name='withdraws')
    amount = models.DecimalField('提现金额', max_digits=10, decimal_places=2)
    account_name = models.CharField('收款人', max_length=80)
    account_no = models.CharField('收款账号', max_length=120)
    status = models.CharField('提现状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    review_note = models.TextField('审核备注', blank=True)
    paid_at = models.DateTimeField('打款时间', null=True, blank=True)

    class Meta:
        verbose_name = '提现'
        verbose_name_plural = '提现'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.teacher} - {self.amount}'

    def approve(self, review_note=''):
        self.status = self.STATUS_APPROVED
        self.review_note = review_note
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'review_note', 'paid_at', 'updated_at'])

    def reject(self, review_note=''):
        self.status = self.STATUS_REJECTED
        self.review_note = review_note
        self.save(update_fields=['status', 'review_note', 'updated_at'])


class Comment(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='用户', on_delete=models.CASCADE, related_name='comments')
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE, related_name='comments')
    lesson = models.ForeignKey(CourseLesson, verbose_name='小节', on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    content = models.TextField('评论内容')
    rating = models.PositiveSmallIntegerField('评分', default=5)
    is_visible = models.BooleanField('是否显示', default=True)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']

    def __str__(self):
        return self.content[:30]


class Favorite(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='用户', on_delete=models.CASCADE, related_name='favorites')
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE, related_name='favorites')

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_favorite'),
        ]

    def __str__(self):
        return f'{self.user} - {self.course}'

# Create your models here.
