from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify


class Address(models.Model):
    """
    Author: Daking Rai (daking.rai@infodevelopers.com.np)
    Date: July 04, 2018
    Description: Address model that is used by company.
    """
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    zip_code = models.CharField(max_length=10, null=True)
    address1 = models.CharField(max_length=100, null=True)
    address2 = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'addresses'
        verbose_name_plural = 'addresses'

    def __str__(self):
        return '{},{}'.format(self.city, self.country)


class UserManager(BaseUserManager):
    """
    Author: Daking Rai (daking.rai@infodevelopers.com.np)
    Date: July 04, 2018
    Description: UserManager class is copy of default User model provided by Django. No modification
    is done in this class.
    """

    def _create_user(self,username, email, password, **extra_fields):
        if not email:
            raise ValueError('User must have email address')
        email = self.normalize_email(email)
        address = Address.objects.create()

        user = self.model(username=username, address= address, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Author: Daking Rai (daking.rai@infodevelopers.com.np)
    Date: July 04, 2018
    Description: User Class extends user model provided by django to add new column - email,address,
    is_restaurant_staff,website_staff.
    AUTH_USER_MODEL is also added in settings.py to tell the program to include this models in user model.
    """
    username = models.CharField(
        _('username'),
        max_length=150,
        blank=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that username already exists."),
            },
            )
    email = models.EmailField(_('email address'), unique=True, null=True)
    is_company = models.BooleanField(default=False)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
        )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
                'Designates whether this user should be treated as active. '
                'Unselect this instead of deleting accounts.'
            ),
        )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    recent_resume = models.FileField(blank=True, null=True)

    def get_full_name(self):
        full_name = '%s' %self.username
        return full_name.strip()

    def get_short_name(self):
        return self.email


class Company(models.Model):
    """
    Author: Daking Rai (daking.rai@infodevelopers.com.np)
    Date: July 04, 2018
    """
    description = models.TextField(null=True, blank=True)
    website = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'company'
        verbose_name_plural = 'companies'

    def __str__(self):
        return '{}'.format(self.user.username)

    def save(self, **kwargs):
        slug_str = "%s" % self.user.username
        self.slug = slugify(self, slug_str)
        super(Company, self).save(**kwargs)


class WorkExperience(models.Model):
    job_title = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    responsibilities = models.TextField()
    job_level = models.CharField(max_length=20, null=True, blank=True)

    from_date = models.DateField()
    to_date = models.DateField(blank=True, null=True)
    currently_working = models.BooleanField()

    def __str__(self):
        return self.job_title


class Education(models.Model):
    degree = models.CharField(max_length=100)

    program = models.CharField(max_length=100)
    school  = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    marks = models.CharField(max_length=20)

    location = models.CharField(max_length=100)
    start = models.CharField(max_length=10)
    end = models.CharField(max_length=10, )
    currently_studing = models.BooleanField()

    def __str__(self):
        return self.program


class Training(models.Model):
    name = models.CharField(max_length=255)
    institution = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class Skills(models.Model):
    skill = models.CharField(max_length=50)

    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.skill


class UserProfile(models.Model):
    
    GENDER_CHOICES = (
        (0, '---'),
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Prefer not to say'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)

    dob = models.DateField()

    gender = models.IntegerField(choices=GENDER_CHOICES, null=True, blank=True)

    mailing_address = models.EmailField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    contact = models.CharField(max_length=20)

    education = models.ManyToManyField(Education, blank=True)
    trainings = models.ManyToManyField(Training, blank=True)
    work_experience = models.ManyToManyField(WorkExperience, blank=True)
    skills = models.ManyToManyField(Skills, blank=True)

    def __str__(self):
        return self.user.username

    def profile_status(self):
        temp = 25
        if self.education.all():
            temp += 25

        if self.work_experience.all():
            temp += 25
        if self.trainings.all():
            temp += 10
        if self.skills.all():
            temp += 15
        return temp


class UserExtractedProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    education = models.CharField(max_length=255, null=True, blank=True)
    experience = models.CharField(max_length=255, null=True, blank=True)
    total_experience = models.CharField(max_length=255, null=True, blank=True)
    skills = models.CharField(max_length=255, null=True, blank=True)
    skills_present = models.CharField(max_length=255, null=True, blank=True)
    grad_degree = models.BooleanField(default=False)
    undergrad_degree = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)
