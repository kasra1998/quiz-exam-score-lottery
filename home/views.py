from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required


from .models import Question, UserProfile, Lottery
from .forms import SignupForm, LoginForm

import json
import random

@staff_member_required
def trigger_lottery(request):
    """Admin-triggered lottery from frontend"""
    users = UserProfile.objects.all()
    weighted_users = []
    for u in users:
        weighted_users += [u.user] * max(1, u.total_score)
    if not weighted_users:
        return JsonResponse({"status": False, "message": "No users available"})
    winner = random.choice(weighted_users)
    Lottery.objects.create(winner=winner)
    return JsonResponse({"status": True, "winner": winner.username})

def home(request):
    """Homepage with categories and total score (if logged in)."""
    total_score = 0
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        total_score = profile.total_score

    # Always define winner
    winner = None

    # Get latest lottery
    try:
        latest_lottery = Lottery.objects.order_by("-created_at").first()
        if latest_lottery and latest_lottery.winner:
            winner = latest_lottery.winner.username
    except Lottery.DoesNotExist:
        winner = None

    return render(request, "home/home.html", {
        "total_score": total_score,
        "lottery_winner": winner
        })


def signup_view(request):
    """User signup view."""
    if request.user.is_authenticated:
        return redirect("home:home")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home:home")
    else:
        form = SignupForm()

    return render(request, "home/signup.html", {"form": form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect("home:home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next") or "home:home"
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, "home/login.html", {"form": form})


def logout_view(request):
    """Logout user."""
    logout(request)
    return redirect("home:home")


@login_required
def quiz(request, category):
    """Render quiz page for a given category."""
    return render(request, "home/quiz.html", {"category": category})


def get_quiz(request, category):
    """Return randomized quiz questions in JSON."""
    try:
        questions = Question.objects.filter(gfg__gfg_name__iexact=category).all()
        questions = list(questions)
        random.shuffle(questions)
        questions = questions[:10]  # limit to 10

        data = []
        for q in questions:
            data.append({
                "uid": str(q.uid),
                "question": q.question,
                "marks": q.marks,
                "answer": q.get_answers(),
            })

        return JsonResponse({"status": True, "data": data})
    except Exception as e:
        return JsonResponse({"status": False, "error": str(e)})


@csrf_exempt
@login_required
@csrf_exempt
@login_required
def submit_quiz(request):
    """Check answers, update user score, return results including correct answers."""
    if request.method != "POST":
        return JsonResponse({"status": False, "error": "Invalid request"})

    try:
        data = json.loads(request.body.decode("utf-8"))
        answers = data.get("answers", {})

        score = 0
        correct_answers = {}  # uid -> True if correct

        for uid, selected_answer in answers.items():
            try:
                q = Question.objects.get(uid=uid)
                correct = q.answers.filter(is_correct=True).first()
                if correct and correct.answer == selected_answer:
                    score += q.marks
                    correct_answers[str(uid)] = True
            except Question.DoesNotExist:
                continue

        # Update user score
        profile = request.user.userprofile
        profile.total_score += score
        profile.save()

        return JsonResponse({
            "status": True,
            "score": score,
            "total_score": profile.total_score,
            "correct_answers": correct_answers,  # ✅ send correct answers
        })

    except Exception as e:
        return JsonResponse({"status": False, "error": str(e)})


def lottery_view(request):
    """Show latest lottery winner."""
    latest = Lottery.objects.order_by("-created_at").first()
    context = {"winner": latest.winner if latest else None}
    return render(request, "home/lottery.html", context)
