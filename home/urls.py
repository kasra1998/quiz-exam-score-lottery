from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("lottery/", views.lottery_view, name="lottery"),

    # Quiz routes
    path("quiz/<str:category>/", views.quiz, name="quiz"),
    path("get-quiz/<str:category>/", views.get_quiz, name="get_quiz"),
    path("submit-quiz/", views.submit_quiz, name="submit_quiz"),
    path("trigger-lottery/", views.trigger_lottery, name="trigger_lottery"),

]
