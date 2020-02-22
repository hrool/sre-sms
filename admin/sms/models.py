from django.db import models
from django.utils.html import format_html


# 项目.
class Project(models.Model):
    name = models.CharField(verbose_name='名称', max_length=20, unique=True)
    enable = models.BooleanField(default=True, verbose_name='启用开关')
    note = models.TextField(verbose_name='备注', null=True, blank=True)
    timeout_retry = models.BooleanField(default=False, verbose_name='超时重试开关', help_text='仅事务类型短信生效')
    timeout = models.PositiveIntegerField(default=120, verbose_name='超时时间', help_text='仅timeout_retry=True有效')
    fail_retry = models.BooleanField(default=True, verbose_name='失败重试开关', help_text='失败后立即重试')
    strong_valid = models.BooleanField(default=True, verbose_name='手机号强校验开关', help_text='强校验,国家和地区,以及运营商号码段')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "项目"
        verbose_name_plural = verbose_name


# 用于发送的api用户
class ApiUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    username = models.CharField(max_length=100, verbose_name='用户名', unique=True)
    password = models.CharField(max_length=100, verbose_name='密码')
    enable = models.BooleanField(default=True, verbose_name='启用开关')
    note = models.TextField(verbose_name='备注', null=True, blank=True)

    def __str__(self):
        return "%s(%s)" % (self.project.name, self.username)

    class Meta:
        verbose_name = "api用户"
        verbose_name_plural = verbose_name


class Sms(models.Model):
    api_user = models.ForeignKey(ApiUser, verbose_name='api用户', on_delete=models.PROTECT)
    mock = models.BooleanField(verbose_name='是否mock', default=False, help_text='mock为True,不会真正发送')
    SMS_TYPE_CHOICES = (
        ('promotional', '营销'),
        ('transactional', '事务'),
    )
    sms_type = models.CharField(max_length=20, choices=SMS_TYPE_CHOICES,
                                verbose_name='短信类型',
                                help_text='''只有两种短信类型: promotional(营销) transactional(事务)
                                事务类型的短信, 优先保证达到率,
                                批量发送的营销类短信, 禁止使用事务类型, 避免影响事务短信的到达率,
                                ''',
                                default='transactional')
    create_time = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    to = models.CharField(max_length=40, db_index=True)
    subject = models.CharField(max_length=60, help_text='短信主题', null=True, blank=True)  # 主题
    content = models.TextField(help_text='短信内容, html格式')
    STATUS_CHOICES = (
        ('create', '创建成功'),
        ('sent', '发送成功'),
        ('send_fail', '发送失败'),
        ('deliver_fail', '到达失败'),
        ('deliver', '到达成功'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='状态', editable=False)
    update_time = models.DateTimeField(auto_now_add=True, verbose_name='状态更新时间', editable=False, db_index=True)
    def colored_status_property(self):
        if self.status in ['create', 'sent', 'deliver']:
            color_code = 'green'
        else:
            color_code = 'red'
        return format_html('<span style="color: {};">{}</span>', color_code, self.status)
    colored_status_property.short_description = '状态'
    colored_status = property(colored_status_property)


    def __str__(self):
        return "%s : %s" % (self.api_user, self.subject)

    class Meta:
        verbose_name = "短信"
        verbose_name_plural = verbose_name


# sms service providers
class Ssp(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    SSP_TYPE_CHOICES = (
        ('sendcloud', 'sendcloud'),
        ('sea_253', '253国际'),
        ('twilio', 'twilio'),
    )
    ssp_type = models.CharField(max_length=10, choices=SSP_TYPE_CHOICES, default='sendcloud')
    auth_user = models.CharField(max_length=100, verbose_name='认证用户名', default='api')
    auth_password = models.CharField(max_length=100, verbose_name='认证密码')
    is_enable = models.BooleanField(default=True, verbose_name='是否启用')  # 是否启用

    def __str__(self):
        return "%s:%s" % (self.project.name, self.ssp_type)

    class Meta:
        verbose_name = "短信发送商ssp"
        verbose_name_plural = verbose_name
        unique_together = ('project', 'ssp_type')


class SspRule(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)


class SmsEvent(models.Model):
    sms_id = models.PositiveIntegerField(editable=False, db_index=True)
    project = models.ForeignKey(Project, verbose_name='项目', on_delete=models.PROTECT, editable=False)
    ssp = models.ForeignKey(Ssp, verbose_name='发信Ssp', editable=False,
                            null=True, blank=True,
                            on_delete=models.PROTECT)
    ssp_sms_id = models.CharField(max_length=100, null=True, blank=True, editable=False, db_index=True)
    to = models.CharField(max_length=40, db_index=True)
    subject = models.CharField(max_length=60, verbose_name='短信主题', null=True, blank=True, editable=False)
    create_time = models.DateTimeField(editable=False, null=True, blank=True, db_index=True)
    sent_time = models.DateTimeField(editable=False, null=True, blank=True)
    ssp_sent_time = models.DateTimeField(editable=False, null=True, blank=True)
    event_time = models.DateTimeField(editable=False, null=True, blank=True)
    EVENT_TYPE_CHOICES = (
        ('create', '创建成功'),
        ('sent', '发送成功'),
        ('send_fail', '发送失败'),
        ('deliver', '到达成功'),
        ('workererror', '处理失败'),
        ('delivererror', '发送失败'),
        ('reply', '用户回复'),
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, verbose_name='事件类型', editable=False)
    event_msg = models.TextField(editable=False)

    class Meta:
        verbose_name = "短信事件"
        verbose_name_plural = verbose_name
