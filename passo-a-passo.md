# Passo a passo

```
git clone https://github.com/rg3915/django-auth-tutorial.git
cd django-auth-tutorial
git branch base origin/base
git checkout base

python3 -m venv .venv
source .venv/bin/activate

# Django==3.1.8 django-utils-six django-extensions python-decouple
cat requirements.txt

pip install -U pip
pip install -r requirements.txt
pip install ipdb

python contrib/env_gen.py

python manage.py migrate
python manage.py createsuperuser --username="admin" --email="admin@email.com"

python manage.py shell_plus
```

https://docs.djangoproject.com/en/3.1/ref/contrib/auth/#django.contrib.auth.models.UserManager.create_user


```python
python manage.py shell_plus

from django.contrib.auth.models import User

user = User.objects.create_user(
    username='regis', 
    email='regis@email.com', 
    password='demodemo',
    first_name='Regis',
    last_name='Santos',
    is_active=True
)
```

```
cat myproject/settings.py
```


```python
INSTALLED_APPS = [
    'myproject.accounts',  # <---
    'django.contrib.admin',
    'django.contrib.auth',
    ...
    'django_extensions',
    'widget_tweaks',
    'myproject.core',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
EMAIL_HOST = config('EMAIL_HOST', '0.0.0.0')  # localhost
EMAIL_PORT = config('EMAIL_PORT', 1025, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)


# LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'core:index'
LOGOUT_REDIRECT_URL = 'core:index'
```

## MailHog

Rodar [MailHog](https://github.com/mailhog/MailHog) via Docker.

```
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```


## Estrutura do projeto

```
tree
```

## Telas

### Login

![01_login.png](img/01_login.png)

### Cadastro

![02_signup.png](img/02_signup.png)

### Trocar senha

![03_change_password.png](img/03_change_password.png)

### Esqueci minha senha

![04_forgot_password.png](img/04_forgot_password.png)


Criando alguns arquivos

```
touch myproject/core/urls.py
touch myproject/accounts/urls.py
```



Editando `urls.py`

```python
# urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('myproject.core.urls', namespace='core')),
    # 
    # path('accounts/', include('myproject.accounts.urls')),  # sem namespace
    path('admin/', admin.site.urls),
]
```

Editando `core/urls.py`

```
touch myproject/core/urls.py
```


```python
# core/urls.py
from django.urls import path

from myproject.core import views as v

app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),
]
```

https://docs.djangoproject.com/en/3.1/topics/auth/default/#the-login-required-decorator

Editando `core/views.py`

```python
# core/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# @login_required
def index(request):
    template_name = 'index.html'
    return render(request, template_name)
```

> Rodar a aplicação.


### Login

![101_login_logout.png](img/101_login_logout.png)

https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.LoginView

https://github.com/django/django/blob/main/django/contrib/auth/views.py#L40

https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.LogoutView

Editando `accounts/urls.py`

```
touch myproject/accounts/urls.py
```


O template padrão é `registration/login.html`, mas vamos mudar

```python
# accounts/urls.py
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from myproject.accounts import views as v

# Se usar app_name vai dar erro de redirect em PasswordResetView.
# app_name = 'accounts'


urlpatterns = [
    path(
        'login/',
        LoginView.as_view(template_name='accounts/login.html'),
        name='login'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
]
```

Em `core/views.py` descomente `@login_required`.


Em `settings.py` descomente

```python
LOGIN_URL = 'login'
```

Em `myproject/urls.py` descomente

```
...
path('accounts/', include('myproject.accounts.urls')),  # sem namespace
...
```


Em `nav.html` corrija

```html
href="{% url 'logout' %}">Logout</a>
```



> Mostrar a aplicação rodando com login e logout.


### Cadastro

![102_signup.png](img/102_signup.png)

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html#basic-sign-up

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html#sign-up-with-confirmation-mail

https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordResetConfirmView

https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordResetCompleteView

https://github.com/django/django/blob/main/django/contrib/auth/urls.py#L18

Editando `accounts/urls.py`

```python
# accounts/urls.py
    ...
    path('signup/', v.signup, name='signup'),
    # path('signup/', v.SignUpView.as_view(), name='signup'),
    path('signup-email/', v.signup_email, name='signup_email'),
    path(
        'account-activation-done/',
        v.account_activation_done,
        name='account_activation_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        v.MyPasswordResetConfirm.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        v.MyPasswordResetComplete.as_view(),
        name='password_reset_complete'
    ),
    ...
```

Editando `accounts/tokens.py`

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html

```
touch myproject/accounts/tokens.py
```


```python
# accounts/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp)
        )


account_activation_token = AccountActivationTokenGenerator()
```


Editando `accounts/views.py`

```python
# accounts/views.py
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView
)
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import CreateView

from myproject.accounts.forms import SignupEmailForm, SignupForm
from myproject.accounts.tokens import account_activation_token


def signup(request):
    form = SignupForm(request.POST or None)
    context = {'form': form}
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')

            # Autentica usuário
            user = authenticate(username=username, password=raw_password)

            # Faz login
            auth_login(request, user)
            return redirect(reverse_lazy('core:index'))

    return render(request, 'accounts/signup.html', context)


# Mostrar a aplicação rodando.

class SignUpView(CreateView):
    form_class = SignupForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'


# Mostrar a aplicação rodando.


def send_mail_to_user(request, user):
    current_site = get_current_site(request)
    use_https = request.is_secure()
    subject = 'Ative sua conta.'
    message = render_to_string('email/account_activation_email.html', {
        'user': user,
        'protocol': 'https' if use_https else 'http',
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    user.email_user(subject, message)


def signup_email(request):
    form = SignupEmailForm(request.POST or None)
    context = {'form': form}
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_mail_to_user(request, user)
            return redirect('account_activation_done')

    return render(request, 'accounts/signup_email_form.html', context)


def account_activation_done(request):
    return render(request, 'accounts/account_activation_done.html')


class MyPasswordResetConfirm(PasswordResetConfirmView):

    def form_valid(self, form):
        self.user.is_active = True
        self.user.save()
        return super(MyPasswordResetConfirm, self).form_valid(form)


class MyPasswordResetComplete(PasswordResetCompleteView):
    ...
```

https://github.com/django/django/blob/main/django/contrib/auth/forms.py#L75

Editando `accounts/forms.py`

```
touch myproject/accounts/forms.py
```

```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# from myproject.accounts.models import UserProfile


class SignupForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nome',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
    last_name = forms.CharField(label='Sobrenome', max_length=30, required=False)  # noqa E501
    username = forms.CharField(label='Usuário', max_length=150)
    email = forms.CharField(
        label='E-mail',
        max_length=254,
        help_text='Requerido. Informe um e-mail válido.',
    )
    # cpf = forms.CharField(label='CPF')

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2'
        )


class SignupEmailForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
    last_name = forms.CharField(label='Sobrenome', max_length=30, required=False)  # noqa E501
    username = forms.CharField(label='Usuário', max_length=150)
    email = forms.CharField(
        label='E-mail',
        max_length=254,
        help_text='Requerido. Informe um e-mail válido.',
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        )
```

Arrumar link em `accounts/login.html`

```html
href="{% url 'signup_email' %}">Cadastre-se</a>
```

Dar um `find` em todos templates e trocar

```html
href="{ url 'login' %}">Login</a>
```
por

```html
href="{% url 'login' %}">Login</a>
```

Arrumar o link em `email/account_activation_email.html`

```html
{{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}
```

Arrumar o link em `registration/password_reset_complete.html`

```html
href="{% url 'login' %}
```

Renomear a pasta `registration` para `temp`.

```
mv myproject/accounts/templates/registration myproject/accounts/templates/temp
```


> Mostrar a aplicação rodando com **cadastro normal** e **cadastro com senha.**

Renomear a pasta `temp` para `registration`.

```
mv myproject/accounts/templates/temp myproject/accounts/templates/registration
```


### Trocar senha

![103_change_password.png](img/103_change_password.png)

https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordChangeView

https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordChangeDoneView

https://github.com/django/django/blob/main/django/contrib/auth/views.py#L334

https://github.com/django/django/blob/main/django/views/generic/base.py#L157

Em `accounts/views.py`

```python
# accounts/views.py
class MyPasswordChange(PasswordChangeView):
    ...


class MyPasswordChangeDone(PasswordChangeDoneView):

    def get(self, request, *args, **kwargs):
        return redirect(reverse_lazy('login'))
```

Em `accounts/urls.py`

```python
# accounts/urls.py
    ...
    path(
        'password_change/',
        v.MyPasswordChange.as_view(),
        name='password_change'
    ),
    path(
        'password_change/done/',
        v.MyPasswordChangeDone.as_view(),
        name='password_change_done'
    ),
    ...
```

> Mostrar a aplicação rodando com a **troca de senha**.

Arrumar o link em `nav.html`

```html
<a class="nav-link" href="{% url 'password_change' %}">Trocar a senha</a>
```

### Esqueci minha senha

![104_reset_password.png](img/104_reset_password.png)

https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordResetView

https://github.com/django/django/blob/main/django/contrib/auth/views.py#L212

https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordResetDoneView

https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.forms.PasswordResetForm

https://github.com/django/django/blob/main/django/contrib/auth/forms.py#L238

https://github.com/django/django/blob/main/django/contrib/auth/urls.py


Em `accounts/views.py`

```python
# accounts/views.py

# Requer
# registration/password_reset_email.html
# registration/password_reset_subject.txt
class MyPasswordReset(PasswordResetView):
    ...


class MyPasswordResetDone(PasswordResetDoneView):
    ...


class MyPasswordResetConfirm(PasswordResetConfirmView):

    def form_valid(self, form):
        self.user.is_active = True
        self.user.save()
        return super(MyPasswordResetConfirm, self).form_valid(form)


class MyPasswordResetComplete(PasswordResetCompleteView):
    ...

```

Em `accounts/urls.py`

```python
# accounts/urls.py
    ...
    path(
        'password_reset/',
        v.MyPasswordReset.as_view(),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        v.MyPasswordResetDone.as_view(),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        v.MyPasswordResetConfirm.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        v.MyPasswordResetComplete.as_view(),
        name='password_reset_complete'
    ),
    ...
```

Arrumar o link em `login.html`

```html
<a class="btn btn-link px-0" href="{% url 'password_reset' %}">Esqueci minha senha</a>
```

Arrumar o link em `registration/password_reset_email.html`

```html
{{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}
```

---

Falar de `include('django.contrib.auth.urls')` include em `urls.py`

https://github.com/django/django/blob/main/django/contrib/auth/urls.py

```python
# urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # path('', include('django.contrib.auth.urls')),  # sem namespace
]
```

---

## Perfil

```python
# accounts/models.py
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    cpf = models.CharField('CPF', max_length=11, unique=True, null=True, blank=True)  # noqa E501
    rg = models.CharField('RG', max_length=20, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('cpf',)
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

    def __str__(self):
        if self.cpf:
            return self.cpf
        return self.user.username


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

```


```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    ...
    cpf = forms.CharField(label='CPF')
    rg = forms.CharField(label='RG', required=False)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'cpf',
            'rg',
            'username',
            'email',
            'password1',
            'password2'
        )


class SignupEmailForm(forms.ModelForm):
    ...
    cpf = forms.CharField(label='CPF')
    rg = forms.CharField(label='RG', required=False)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'cpf',
            'rg',
            'username',
            'email',
        )
```

```python
# accounts/admin.py
from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'rg')
```

```python
# accounts/views.py
def signup(request):
        ...
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()  # precisa salvar para rodar o signal.
            # carrega a instância do perfil criada pelo signal.
            user.refresh_from_db()
            user.profile.cpf = form.cleaned_data.get('cpf')
            user.profile.rg = form.cleaned_data.get('rg')
            user.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')

            # Autentica usuário
            user_auth = authenticate(username=username, password=raw_password)

            # Faz login
            auth_login(request, user_auth)
            return redirect(reverse_lazy('core:index'))

    return render(request, 'accounts/signup.html', context)


def signup_email(request):
        ...
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()  # precisa salvar para rodar o signal.
            # carrega a instância do perfil criada pelo signal.
            user.refresh_from_db()
            user.profile.cpf = form.cleaned_data.get('cpf')
            user.profile.rg = form.cleaned_data.get('rg')
            user.save()
            send_mail_to_user(request, user)
            return redirect('account_activation_done')

    return render(request, 'accounts/signup_email_form.html', context)

```

Corrigindo o erro `RelatedObjectDoesNotExist at /admin/login/ User has no profile`

```
user = User.objects.get(username='admin')
Profile.objects.create(user=user)
```
