from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from .models import Alarm #model에서 알 모델을 갖고오는 기능
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required #데코레이터
def create_alarm(request, user_id, message):
    try:
        user = User.objects.get(id=user_id)  # 알림을 받을 사용자
        alarm = Alarm(user=user, message=message)
        alarm.save()

        return redirect('user_dashboard')  # 알람 생성 후 리디렉션
    except User.DoesNotExist:
        return redirect('error_page')
