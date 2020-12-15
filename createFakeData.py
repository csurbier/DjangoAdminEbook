import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoAdmin.settings")
import django
django.setup()

from faker import factory,Faker
from backoffice.models import *
from model_bakery.recipe import Recipe,foreign_key

fake = Faker()
########### First 100 random Authors,Questions and choices

for _ in range(100):
    author = Recipe(
        Author,
        name = fake.name(),
        createdDate = fake.future_datetime(end_date="+30d", tzinfo=None),
        updatedDate = fake.future_datetime(end_date="+30d", tzinfo=None),
    )

    # create question
    question = Recipe(Question,
                question_text = fake.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None),
                pub_date =fake.future_datetime(end_date="+30d", tzinfo=None),
                refAuthor=foreign_key(author),
                createdDate=fake.future_datetime(end_date="+30d", tzinfo=None),
                updatedDate=fake.future_datetime(end_date="+30d", tzinfo=None),
            )

    # create Choices
    choice = Recipe(Choice,
                    question=foreign_key(question),
                    choice_text = fake.sentence(nb_words=1, variable_nb_words=True, ext_word_list=None),
                    createdDate=fake.future_datetime(end_date="+30d", tzinfo=None),
                    updatedDate=fake.future_datetime(end_date="+30d", tzinfo=None),
            )
    choice.make()