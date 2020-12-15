import csv
import json
from datetime import datetime, timedelta

from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.forms import BaseInlineFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from backoffice.models import *
from django.contrib import admin
from backoffice.models import *
from django.contrib.admin import AdminSite

# Custom admin site
class MyUltimateAdminSite(AdminSite):
	site_header = 'My Django Admin ultimate guide'
	site_title = 'My Django Admin ultimate guide Administration'
	index_title = 'Welcome to my backoffice'
	index_template = 'backoffice/templates/admin/my_index.html'
	login_template = 'backoffice/templates/admin/login.html'

	def get_urls(self):
		urls = super(MyUltimateAdminSite, self).get_urls()
		custom_urls = [
			path('my_view/', self.admin_view(self.my_view), name="my_view"),
		]
		return urls + custom_urls

	def my_view(self, request):
		# your business code
		context = dict(
			self.each_context(request),
			welcome="Welcome to my new view",
		)
		return TemplateResponse(request, "admin/backoffice/custom_view.html", context)

	"""
	def get_app_list(self, request):
		# Return a sorted list of our models
		ordering = {"The Choices": 1, "The Questions": 2, "The Authors": 3}
		app_dict = self._build_app_dict(request)
		app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
		for app in app_list:
			app['models'].sort(key=lambda x: ordering[x['name']])
		return app_list
	"""
site = MyUltimateAdminSite()

class QuestionFormSet(BaseInlineFormSet):

	def clean(self):
		super(QuestionFormSet, self).clean()

		for form in self.forms:
			if not form.is_valid():
				return
			if form.cleaned_data and not form.cleaned_data.get('DELETE'):
				pub_date = form.cleaned_data['pub_date']
				from datetime import date
				if pub_date.date() <= date.today():
					raise ValidationError(
						"The publication date should be in the future %s" % form.cleaned_data["pub_date"])

class QuestionInline(admin.TabularInline):
	model = Question
	formset = QuestionFormSet

	def get_formset(self, request, obj=None, **kwargs):
		formset = super(QuestionInline, self).get_formset(request, obj, **kwargs)
		initial = []
		for x in range(0,self.extra):
			initial.append({
				'question_text': '',
				'pub_date': datetime.now(),
				'refAuthor': ''

			})
		from functools import partialmethod
		formset.__init__ = partialmethod(formset.__init__, initial=initial)
		return formset


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
	inlines = (QuestionInline,)
	empty_value_display = 'Unknown'
	fieldsets = [
		("Author information", {'fields': ['name', 'createdDate', 'updatedDate']}),
	]
	list_display = ('name','createdDate','updatedDate',)
	list_per_page = 50
	search_fields = ('name',)
	readonly_fields = ('createdDate', 'updatedDate',)

	def changelist_view(self, request, extra_context=None):
		# Aggregate new authors per day
		chart_data = (
			Author.objects.annotate(date=TruncDay("updatedDate"))
				.values("date")
				.annotate(y=Count("id"))
				.order_by("-date")
		)

		# Serialize and attach the chart data to the template context
		as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
		print("Json %s" % as_json)
		extra_context = extra_context or {"chart_data": as_json}
		# Call the superclass changelist_view to render the page
		return super().changelist_view(request, extra_context=extra_context)

	def change_view(self, request, object_id, form_url='', extra_context=None):
		nbQuestion = Question.objects.filter(refAuthor=object_id).count()
		response_data = [
			nbQuestion
		]
		extra_context = extra_context or {}
		# Serialize and attach the chart data to the template context
		as_json = json.dumps(response_data, cls=DjangoJSONEncoder)
		extra_context = extra_context or {"nbQuestion": as_json}
		return super().change_view(
			request, object_id, form_url,
			extra_context=extra_context, )

class QuestionPublishedListFilter(admin.SimpleListFilter):
	# Human-readable title which will be displayed in the
	# right admin sidebar just above the filter options.
	title = ('Published questions')
	# Parameter for the filter that will be used in the URL query.
	parameter_name = 'pub_date'
	def lookups(self, request, model_admin):
		"""
		Returns a list of tuples. The first element in each
		tuple is the coded value for the option that will
		appear in the URL query. The second element is the
		human-readable name for the option that will appear
		in the right sidebar.
		"""
		return (
			('Published', ('Published questions')),
			('Unpublished', ('Unpublished questions')),
		)

	def queryset(self, request, queryset):
		"""
		Returns the filtered queryset based on the value
		provided in the query string and retrievable via
		`self.value()`.
		"""
		if self.value() == 'Published':
			return queryset.filter(pub_date__lt=datetime.now())
		if self.value() == 'Unpublished':
			return queryset.filter(pub_date__gte=datetime.now())

class QuestionsAuthorFilter(admin.SimpleListFilter):
	title = 'Author questions'
	parameter_name = 'refAuthor'
	def lookups(self, request, model_admin):
		if 'refAuthor__id__exact' in request.GET:
			id = request.GET['refAuthor__id__exact']
			questions = model_admin.model.objects.all().filter(refAuthor=id)
		else:
			questions = model_admin.model.objects.all()

		return [(question.id, question.question_text) for question in questions]

	def queryset(self, request, queryset):
		if self.value():
			return queryset.filter(id=self.value())

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

	fieldsets = (
		("Question information", {
			'fields': ('question_text',)
		}),
		("Date", {
			'fields': ('pub_date',)
		}),
		('The author', {
			'classes': ('collapse',),
			'fields': ('refAuthor',),
		}),
	)
	list_display = ('question_text', 'colored_question_text','goToChoices','refAuthor', 'has_been_published', 'pub_date',
					'createdDate', 'updatedDate',)
	list_display_links = ('refAuthor',)


	#list_editable = ('question_text',)
	search_fields = ('refAuthor__name',)
	ordering = ('-pub_date',)
	date_hierarchy = 'pub_date'
	list_filter = (QuestionPublishedListFilter,QuestionsAuthorFilter,'refAuthor',)
	list_select_related = ('refAuthor',)
	autocomplete_fields = ['refAuthor']

	def has_been_published(self, obj):
		present = datetime.now()
		return obj.pub_date.date() < present.date()

	has_been_published.boolean = True
	has_been_published.short_description = 'Published?'

	def colored_question_text(self, obj):
		return format_html(
			'<span style="color: #{};">{}</span>',
			"ff5733",
			obj.question_text,
		)

	colored_question_text.short_description = 'Color?'

	@mark_safe
	def goToChoices(self, obj):
		return format_html(
			'<a class="button" href="/admin/backoffice/choice/?question__id__exact=%s" target="blank">Choices</a>&nbsp;'% obj.pk)
	goToChoices.short_description = 'Choices'
	goToChoices.allow_tags = True

	def make_published(modeladmin, request, queryset):
		queryset.update(pub_date=datetime.now() - timedelta(days=1))

	make_published.short_description = "Mark selected questions as published"

	import csv
	from django.http import HttpResponse
	def export_to_csv(modeladmin, request, queryset):
		opts = modeladmin.model._meta
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; \
			filename={}.csv'.format(opts.verbose_name)
		writer = csv.writer(response)
		fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
		# Write a first row with header information
		writer.writerow([field.verbose_name for field in fields])
		# Write data rows
		for obj in queryset:
			data_row = []
			for field in fields:
				value = getattr(obj, field.name)
				if isinstance(value, datetime):
					value = value.strftime('%d/%m/%Y %H:%M')
				data_row.append(value)
			writer.writerow(data_row)
		return response

	export_to_csv.short_description = 'Export to CSV'

	def make_published_custom(self, request, queryset):
		if 'apply' in request.POST:
			# The user clicked submit on the intermediate form.
			# Perform our update action:
			queryset.update(pub_date=datetime.now() - timedelta(days=1))

			# Redirect to our admin view after our update has
			# completed with a nice little info message saying
			# our models have been updated:
			self.message_user(request,
							  "Changed to published on {} questions".format(queryset.count()))
			return HttpResponseRedirect(request.get_full_path())

		return render(request,
						  'admin/backoffice/custom_makepublished.html',
						  context={'questions': queryset})

	make_published_custom.short_description = "Custom make published"
	actions = [make_published,export_to_csv,make_published_custom]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
	list_display = ('question', 'choice_text','votes','createdDate', 'updatedDate',)
	#list_filter = ('question__refAuthor','question',)
	ordering = ('-createdDate',)
	list_select_related = ('question','question__refAuthor',)

	"""
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		try:
			if db_field.name == "question":
				kwargs["queryset"] = Question.objects.filter(refAuthor=1)
			return super(ChoiceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
		except Exception as e:
			print(e)
	"""
	def get_form(self, request, obj=None, **kwargs):
		form = super(ChoiceAdmin, self).get_form(request, obj=obj, **kwargs)
		firstQuestion = Question.objects.all().last()
		form.base_fields['question'].initial = firstQuestion
		form.base_fields['choice_text'].initial = "my custom text"
		return form

site.register(Author,AuthorAdmin)
site.register(Question,QuestionAdmin)
site.register(Choice,ChoiceAdmin)
site.register(User)
site.register(Group)