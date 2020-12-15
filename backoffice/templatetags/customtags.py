from django import template
from backoffice.models import *
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def displayQuestions(refAuthor):
    questions = Question.objects.filter(refAuthor=refAuthor).select_related("refAuthor")
    fullHtml=""
    for question in questions:
        html="<tr><td>"+question.question_text+"</td><td>"+str(question.pub_date)+"</td><td></td></tr>"
        fullHtml+=html
    return mark_safe(fullHtml)


@register.simple_tag
def number_of_authors(request):
	qs = Author.objects.all()
	return qs.count()


@register.simple_tag
def number_of_questions(request):
    qs = Question.objects.all().select_related("refAuthor")
    return qs.count()


@register.simple_tag
def number_of_choices(request):
    qs = Choice.objects.all().select_related("question")
    return qs.count()