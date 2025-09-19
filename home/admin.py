from django.contrib import admin
from .models import Types, Question, Answer, UserProfile, Lottery
import random

class AnswerInline(admin.StackedInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

admin.site.register(Types)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(UserProfile)

@admin.register(Lottery)
class LotteryAdmin(admin.ModelAdmin):
    list_display = ("winner", "created_at")
    actions = ["pick_winner"]

    def pick_winner(self, request, queryset):
        users = UserProfile.objects.all()
        weighted_users = []
        for u in users:
            weighted_users += [u.user] * max(1, u.total_score)

        if not weighted_users:
            self.message_user(request, "No users available for lottery")
            return

        winner = random.choice(weighted_users)
        Lottery.objects.create(winner=winner)
        self.message_user(request, f"Winner selected: {winner.username}")
