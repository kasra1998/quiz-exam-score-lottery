from django.db import models
from django.contrib.auth.models import User
import uuid
import random


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Types(BaseModel):
    gfg_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.gfg_name


class Question(BaseModel):
    gfg = models.ForeignKey(Types, related_name="questions", on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.question

    def get_answers(self):
        answer_objs = list(self.answers.all())
        random.shuffle(answer_objs)
        return [
            {"answer": ans.answer, "is_correct": ans.is_correct}
            for ans in answer_objs
        ]


class Answer(BaseModel):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    answer = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Lottery(models.Model):
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lottery {self.created_at.strftime('%Y-%m-%d')} - {self.winner}"
