from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from myproject.accounts.views import signup, SignUpView

app_name = 'accounts'


urlpatterns = [
    path(
        'login/',
        LoginView.as_view(template_name='accounts/login.html'),
        name='login'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('signup/', signup, name='signup'),
    path('signup/', SignUpView.as_view(), name='signup'),
]
