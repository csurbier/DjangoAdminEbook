from django.db import models


class Author(models.Model):
	name = models.CharField(max_length=200)
	createdDate = models.DateTimeField(auto_now_add=True)
	updatedDate = models.DateTimeField(auto_now=True)
	class Meta:
		verbose_name_plural = "The Authors"

	def __str__(self):
		return u'%s' % (self.name)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    refAuthor = models.ForeignKey(Author, on_delete=models.CASCADE)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "The Questions"
    def __str__(self):
        return u'[%s] : %s' % (self.refAuthor, self.question_text)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "The Choices"
    def __str__(self):
        return u'%s : %s' % (self.question, self.choice_text)