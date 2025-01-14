import datetime
import mistune
import random

from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField

from jsonfield import JSONField
from collections import OrderedDict
from system.utils import *
from system.expressions import Parser
from weasyprint import HTML


class Variable(models.Model):
    '''A variable model allowing different options'''

    name = models.CharField(_('name'), max_length=64, unique=True, validators=[RegexValidator(r'^[^ ]+$',
                                                                                              _('No spaces allowed'))])
    display_name = models.CharField(_('display name'), max_length=64, blank=True, default='')

    admin_note = models.TextField(_('admin note'), blank=True)
    program = models.ForeignKey('Program', verbose_name=_(
        'program'), null=True, on_delete=models.CASCADE)
    value = models.CharField(
        _('initial value'), max_length=32, blank=True, default='')
    user_editable = models.BooleanField(_('user editable'), default=False)
    RANDOM_TYPES = (
        ('boolean', _('boolean')),
        ('numeric', _('numeric')),
        ('string', _('string')),
    )
    random_type = models.CharField(
        _('randomization type'), max_length=16, choices=RANDOM_TYPES, null=True, blank=True)
    randomize_once = models.BooleanField(_('randomize once'), default=False)
    range_min = models.IntegerField(
        _('range min (inclusive)'), null=True, blank=True)
    range_max = models.IntegerField(
        _('range max (inclusive)'), null=True, blank=True)
    random_set = models.TextField(_('random string set'), blank=True)
    is_array = models.BooleanField('is array', default=False)
    optional_values = models.CharField(
        _('optional values'), max_length=512, null=True, blank=True)

    class Meta(object):
        verbose_name = _('variable')
        verbose_name_plural = _('variables')
        ordering = ('display_name', 'name', 'value')

    def __str__(self):
        return self.name

    def get_value(self):
        if self.random_type == 'boolean':
            return random.choice([True, False])

        elif self.random_type == 'numeric':
            range_min = self.range_min or 0
            range_max = self.range_max or 0
            return random.randint(range_min, range_max)

        elif self.random_type == 'string':
            try:
                random_set = [item.strip()
                              for item in self.random_set.split(',')]
                return random.choice(random_set)
            except:
                return ''
        else:
            return self.value

    @staticmethod
    def is_array_variable(variable_name):
        try:
            obj = Variable.objects.get(name=variable_name)
            return obj.is_array
        except Variable.DoesNotExist:
            return False

    @staticmethod
    def display_name_by_name(variable_name):
        try:
            obj = Variable.objects.get(name=variable_name)
            if obj.display_name:
                return obj.display_name
            else:
                return variable_name
        except Variable.DoesNotExist:
            return variable_name

    def clean(self):
        Program.clean_is_lock(self.program)


class Program(models.Model):
    '''A top level model for a separate Program, having one or more sessions'''

    title = models.CharField(_('title'), max_length=64, unique=True)
    display_title = models.CharField(_('display title'), max_length=64)
    about = models.TextField(_('about'), null=True, blank=True)
    cover_image = FilerImageField(verbose_name=_('cover image'), related_name="program_cover_images",
                                  null=True, blank=True, on_delete=models.SET_NULL)
    site = models.ForeignKey(Site, verbose_name=_('site'), null=True, blank=True, on_delete=models.SET_NULL)
    style = models.CharField(_('stylesheet'), choices=settings.STYLESHEET_CHOICES, null=True, blank=True,
                             max_length=128)
    from_email = models.CharField(_('from email'), null=True, blank=True, max_length=128)
    admin_note = models.TextField(_('admin note'), blank=True)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('users'), through='ProgramUserAccess')

    is_lock = models.BooleanField(_('is program lock'), default=False)

    def __str__(self):
        return self.title

    class Meta(object):
        verbose_name = _('program')
        verbose_name_plural = _('programs')

    def enroll(self, user, start_time=None, time_factor=None):
        ProgramUserAccess.objects.create(
            program=self,
            user=user,
            start_time=start_time or timezone.now(),
            time_factor=time_factor or 1.0
        )
        return True

    def leave(self, user):
        self.programuseraccess_set.filter(user=user).delete()
        return True

    @property
    def is_rtl(self):
        return self.style is not None and '-rtl.css' in self.style

    @staticmethod
    def clean_is_lock(program):
        if program is not None and program.is_lock:
            raise ValidationError(_('Program is locked. Could not save.'))


class ProgramUserAccess(models.Model):
    '''
    A relational model that allows Users to have access to a Program,
    with their own start time and time factor
    '''

    program = models.ForeignKey('Program', verbose_name=_('program'), on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)

    start_time = models.DateTimeField(_('start time'), default=timezone.now)
    time_factor = models.DecimalField(_('time factor'), default=1.0, max_digits=5, decimal_places=3)

    class Meta(object):
        verbose_name = _('user access')
        verbose_name_plural = _('user accesses')

    def __str__(self):
        return '%s: %s' % (self.program, self.user.__str__())


class Session(models.Model):
    '''A program Session, with layout and logic encoded in JSON'''

    title = models.CharField(_('title'), max_length=64, unique=True)
    display_title = models.CharField(_('display title'), max_length=64)
    route_slug = models.CharField(_('route slug'), max_length=64, null=True, unique=True, default=None)
    is_open = models.BooleanField(_('is open'), default=False)
    program = models.ForeignKey('Program', verbose_name=_('program'), on_delete=models.CASCADE)
    content = models.ManyToManyField('Content', verbose_name=_('content'), blank=True)
    admin_note = models.TextField(_('admin note'), blank=True)

    TIME_UNITS = (
        ('hours', _('hours')),
        ('days', _('days')),
    )
    start_time_delta = models.IntegerField(_('start time delta'), default=0)
    start_time_unit = models.CharField(_('start time unit'), max_length=32, choices=TIME_UNITS, default='hours')
    end_time_delta = models.IntegerField(_('end time delta'), default=0)
    end_time_unit = models.CharField(_('end time unit'), max_length=32, choices=TIME_UNITS, default='hours')
    start_time = models.DateTimeField(_('first start time'), null=True, blank=True)
    scheduled = models.BooleanField(_('scheduled'), default=False)
    interval = models.IntegerField(_('interval delta'), default=0)
    trigger_login = models.BooleanField(_('trigger login'), default=True)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default={"nodes": [], "edges": []})

    class Meta(object):
        verbose_name = _('session')
        verbose_name_plural = _('sessions')

    def __str__(self):
        return self.title or _('Session %s' % self.id)

    def get_absolute_url(self):
        return '%s?session_id=%i' % (
            reverse('content'),
            self.id,
        )

    def get_start_time(self, start_time, time_factor):
        kwargs = {
            self.start_time_unit: float(self.start_time_delta * time_factor)
        }
        timedelta = datetime.timedelta(**kwargs)
        return start_time + timedelta

    def get_end_time(self, start_time, time_factor):
        kwargs = {
            self.start_time_unit: float(self.end_time_delta * time_factor)
        }
        timedelta = datetime.timedelta(**kwargs)
        return start_time + timedelta

    def get_next_time(self, start_time, time_factor):
        if self.interval == 0:
            return start_time
        i = 1
        while True:
            kwargs = {
                self.start_time_unit: float(self.interval * time_factor) * i
            }
            timedelta = datetime.timedelta(**kwargs)
            if start_time + timedelta > timezone.now():
                return start_time + timedelta
            i += 1

    def clean(self):
        Program.clean_is_lock(self.program)

        if self.scheduled and self.end_time_delta > 0 and self.interval == 0:
            raise ValidationError({'interval': ValidationError(
                _('Interval must be greater than zero for reschedule session'))})

class Content(models.Model):
    '''An ordered collection of JSON content'''

    title = models.CharField(_('title'), max_length=64, unique=True)
    display_title = models.CharField(_('display title'), max_length=64)
    content_type = models.CharField(
        _('content type'), max_length=32, editable=False)
    admin_note = models.TextField(_('admin note'), blank=True)
    program = models.ForeignKey(Program, verbose_name=_('program'), blank=True, null=True,
                                help_text=_('Can optionally be bound to a specific program'),
                                on_delete=models.CASCADE)
    data = JSONField(
        load_kwargs={'object_pairs_hook': OrderedDict}, default=[])

    class Meta(object):
        verbose_name = _('content')
        verbose_name_plural = _('contents')

    def __str__(self):
        return self.title or '%s %s' % (self._meta.verbose_name, self.id)

    def get_absolute_url(self):
        return '%s?page_id=%i' % (
            reverse('content'),
            self.id,
        )

    def clean(self):
        Program.clean_is_lock(self.program)


class PageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(content_type='page')


class Page(Content):
    '''An ordered collection of JSON content to be shown together as a Page'''

    objects = PageManager()

    class Meta(object):
        proxy = True
        verbose_name = _('page')
        verbose_name_plural = _('pages')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_type = 'page'

    def check_value(self, user, value, field_type):
        if isinstance(value, list):
            # for some cases value=[] (always empty [] and can't be edited in page)
            return value

        value = variable_replace(user, value)
        if value == None or value.lower() == "none":
            value = ''

        if field_type == "numeric":
            is_num = False
            try:
                int(value)
                is_num = True
            except:
                try:
                    float(value)
                    is_num = True
                except:
                    is_num = False
            if not is_num:
                value = ''

        return value

    def update_html(self, user):
        for pagelet in self.data:
            if pagelet['content_type'] in ['text', 'toggle']:
                content = pagelet.get('content')
                content = remove_comments(content)
                content, pagelet['variables'] = live_variable_replace(
                    user, content)
                pagelet['content'] = mistune.markdown(content, escape=False)

                toggle = pagelet.get('toggle')
                if toggle:
                    toggle = variable_replace(user, toggle)
                    pagelet['toggle'] = toggle

            if pagelet['content_type'] in ['toggleset', 'togglesetmulti']:
                content = pagelet.get('content')
                variableName = content.get('variable_name')
                if 'label' in content:
                    label = content.get('label')
                    label = variable_replace(user, label)
                    content['label'] = label

                if 'value' in content:  # not really usefull-cannot be set with admin portalen!
                    value = content.get('value')
                    content['value'] = self.check_value(user, value, "")

                if 'alternatives' in content:
                    for alt in content['alternatives']:
                        if 'label' in alt:
                            label = alt.get('label')
                            label = variable_replace(user, label)
                            alt['label'] = label
                        if 'value' in alt:
                            value = alt.get('value')
                            alt['value'] = self.check_value(user, value, "")
                            # set previously selected value for togglesetmulti and toggleset
                            checked = is_it_checked(
                                user, variableName, alt['value'])
                            if pagelet['content_type'] == 'togglesetmulti':
                                alt['selected'] = checked
                            if checked:
                                if pagelet['content_type'] == 'toggleset':
                                    content['value'] = alt['value']
                                else:
                                    content['value'].append(alt['value'])
                        if 'text' in alt:
                            text = alt.get('text')
                            text = variable_replace(user, text)
                            alt['text'] = text

            if pagelet['content_type'] == 'form':
                for field in pagelet['content']:
                    if 'label' in field:
                        label = field.get('label')
                        label = variable_replace(user, label)
                        field['label'] = label

                    if 'alternatives' in field:  # for multipleselection and multiplechoice
                        for alt in field['alternatives']:
                            if 'label' in alt:
                                label = alt.get('label')
                                label = variable_replace(user, label)
                                alt['label'] = label
                            if 'value' in alt:
                                value = alt.get('value')
                                alt['value'] = self.check_value(
                                    user, value, "")
                                # set previously selected value for multiplechoice and multipleselection in form
                                checked = is_it_checked(
                                    user, field['variable_name'], alt['value'])
                                if field['field_type'] == 'multipleselection':
                                    alt['selected'] = checked
                                if checked:
                                    if field['field_type'] == 'multiplechoice':
                                        field['value'] = alt['value']
                                    else:
                                        field['value'].append(alt['value'])

                    if 'value' in field:
                        value = field.get('value')
                        field['value'] = self.check_value(
                            user, value, field["field_type"])

                    if 'lower_limit' in field:
                        lower_limit = field.get('lower_limit')
                        field['lower_limit'] = self.check_value(
                            user, lower_limit, field["field_type"])

                    if 'upper_limit' in field:
                        upper_limit = field.get('upper_limit')
                        field['upper_limit'] = self.check_value(
                            user, upper_limit, field["field_type"])

            if pagelet['content_type'] == 'quiz':
                content_array = pagelet.get('content')
                content = content_array[0]
                if 'question' in content:
                    question = content.get('question')
                    question = variable_replace(user, question)
                    content['question'] = question

                if 'alternatives' in content:
                    for alt in content['alternatives']:
                        if 'label' in alt:
                            label = alt.get('label')
                            label = variable_replace(user, label)
                            alt['label'] = label
                        if 'value' in alt:
                            value = alt.get('value')
                            alt['value'] = self.check_value(user, value, "")
                        if 'response' in alt:
                            response = alt.get('response')
                            response = variable_replace(user, response)
                            alt['response'] = response

            if pagelet['content_type'] == 'conditionalset':
                pagelet['variables'] = {}

                for text in pagelet['content']:

                    expression = text.get('expression')
                    parser = Parser(user_obj=user)
                    passed = parser.parse(expression)

                    if passed:
                        content = text.get('content')
                        content = remove_comments(content)
                        content, variables = live_variable_replace(
                            user, content)
                        pagelet['variables'].update(variables)
                        text['content'] = mistune.markdown(
                            content, escape=False)
                    else:
                        text['content'] = ''

            if pagelet['content_type'] in ['image', 'audio', 'file', 'video']:
                content = pagelet.get('content')
                if 'title' in content:
                    title = content.get('title')
                    title = variable_replace(user, title)
                    content['title'] = title
                if 'alt' in content:
                    alt = content.get('alt')
                    alt = variable_replace(user, alt)
                    content['alt'] = alt

    def simple_render(self):
        assert self.user is not None
        html = []
        for pagelet in self.data:
            if pagelet['content_type'] == 'text':
                content = pagelet.get('content')
                content = remove_comments(content)
                content = variable_replace(self.user, content)
                pagelet['content'] = mistune.markdown(content, escape=False)
                html.append(pagelet['content'])
        return '\n'.join(html)

    def generate_pdf(self, user):
        self.user = user

        current_site = Site.objects.get_current()
        base_url = '%(protocol)s://%(domain)s:8000' % {
            'protocol': 'https' if settings.USE_HTTPS else 'http',
            'domain': current_site.domain,
        }

        context = {
            'program': self.program,
            'page': self,
        }

        html = render_to_string('pdf.html', context=context)
        pdf = HTML(string=html, base_url=base_url).write_pdf()
        return pdf


class EmailManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(content_type='email')


class Email(Content):
    '''A model for e-mail content'''

    objects = EmailManager()

    class Meta(object):
        proxy = True
        verbose_name = _('e-mail')
        verbose_name_plural = _('e-mails')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_type = 'email'

    def send(self, user):
        message = self.data[0].get('content')
        message = process_email_links(user, message)
        message, pdfs = generate_pdfs(user, message)
        message = remove_comments(message)
        message = variable_replace(user, message)
        html_message = mistune.markdown(message, escape=False)
        if self.program and self.program.is_rtl:
            p_tag = '<p>'
            p_rtl_tag = '<p dir="rtl">'
            html_message = html_message.replace(p_tag, p_rtl_tag)

        user.send_email(
            subject=self.display_title,
            message=message,
            html_message=html_message,
            pdfs=pdfs
        )


class CodeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(content_type='code')


class Code(Content):
    '''A model for 'python code' content'''

    objects = CodeManager()

    class Meta(object):
        proxy = True
        verbose_name = _('code')
        verbose_name_plural = _('codes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_type = 'code'

    def execute(self, user):
        message = self.data[0].get('content')


class SMSManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(content_type='sms')


class SMS(Content):
    '''A model for SMS content'''

    objects = SMSManager()

    class Meta:
        proxy = True
        verbose_name = _('SMS')
        verbose_name_plural = _('SMSs')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_type = 'sms'
        self.display_title = ''

    def send(self, user, **kwargs):
        message = self.data[0].get('content')
        message = process_email_links(user, message)
        message = process_reply_variables(user, message, **kwargs)
        message = remove_comments(message)
        message = variable_replace(user, message)

        user.send_sms(
            message=message
        )

    def get_content(self, user, **kwargs):
        message = self.data[0].get('content')
        message = process_email_links(user, message)
        message = process_reply_variables(user, message, **kwargs)
        message = remove_comments(message)
        message = variable_replace(user, message)
        return message
