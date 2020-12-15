from django.shortcuts import render
from django.http import JsonResponse
from backoffice.models import Question
import datetime

def getPublishedDate(request):
    lastQuestion = Question.objects.all().order_by("-pub_date")[0]
    if lastQuestion:
       data = {"status": "OK","nextDate":(lastQuestion.pub_date+datetime.timedelta(days=1)).strftime("%Y-%m-%d")}
    else:
        data = {"status":"KO"}
    return JsonResponse(data)
