from ctypes import pointer
from email.policy import default
from importlib.resources import contents
from optparse import Option
from os import name
from random import choices
from secrets import choice
from select import select
import sys
from tabnanny import verbose
from typing import TYPE_CHECKING
from typing_extensions import Self
from unittest.util import _MAX_LENGTH
from wsgiref import validate
from wsgiref.validate import validator
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings
import uuid


# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username + "," + \
               self.occupation



# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=70, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + "," + \
               "Description: " + self.description


# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return "Title: " + self.title


# Enrollment model
# <HINT> Once a user enrolled a class, an enrollment entry should be created between the user and course
# And we could use the enrollment to track information such as exam submissions
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)

# <HINT> Create a Question Model with:
    # Used to persist question content for a course
    # Has a One-To-Many (or Many-To-Many if you want to reuse questions) relationship with course
    # Has a grade point for each question
    # Has question content
    # Other fields and methods you would like to design
#class Question(models.Model):
    # Foreign key to lesson
    # question text
    # question grade/mark

    # <HINT> A sample model method to calculate if learner get the score of the question
    #def is_get_score(self, selected_ids):
    #    all_answers = self.choice_set.filter(is_correct=True).count()
    #    selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
    #    if all_answers == selected_correct:
    #        return True
    #    else:
    #        return False
    
class Question(models.Model):
    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['id']

    lesson = models.ForeignKey(Course, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200, verbose_name=_("Title"))
    mark = models.IntegerField(default=1)

    def get_choice(self):
        choices = self.choice_set.filter(question=self)
        return choices

    def is_get_score(self, selected_ids):
        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        if all_answers == selected_correct:
            return True
        else:
            return False

    def __str__(self):
        return self.question_text

    #def is_get_score(self, selected_ids):
        #all_answers = self.choice_set.filter(is_correct=True).count()
        #selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        #if all_answers == selected_correct:
        #    return True
        #else:
        #    return False
    
    # Validate the score match match number of correct answer
    #def get_choice_mark(self):
      #  all_correct = self.prefetch_related(Prefetch('choice_set')).get().choice_set.filter(is_correct=True).count()
       # print(all_correct)
       # total_mark = self.mark
       # return total_mark / all_correct


#  <HINT> Create a Choice Model with:
    # Used to persist choice content for a question
    # One-To-Many (or Many-To-Many if you want to reuse choices) relationship with Question
    # Choice content
    # Indicate if this choice of the question is a correct one or not
    # Other fields and methods you would like to design
class Choice(models.Model):
    class Meta:
        verbose_name = _("Choice")
        verbose_name_plural = _("Choices")
        ordering = ['id']

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=225, verbose_name=_("Answer Text"))
    is_correct = models.BooleanField(default=False)
    #Update option: Give point for eacher corrected choices based on question's mark
    def __str__(self):
        return self.choice_text

# <HINT> The submission model
# One enrollment could have multiple submission
# One submission could have multiple choices
# One choice could belong to multiple submissions
class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
    questions = models.ManyToManyField(Question)

#class Submission(models.Model):
#    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
#    chocies = models.ManyToManyField(Choice)
#    Other fields and methods you would like to design