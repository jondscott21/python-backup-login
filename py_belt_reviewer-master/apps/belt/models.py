from __future__ import unicode_literals
from django.forms import extras
from django.db import models
from time import time, strftime, localtime
import re, bcrypt
EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
PASSWORD_REGEX = re.compile(r'((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,})', re.MULTILINE)
name_regex = re.compile(r'[a-zA-Z]+$', re.MULTILINE)

class Umanager(models.Manager):
    def reg(self, postData):
        status = {}
        msg = []
        name = postData['name']
        alias = postData['alias']
        email = postData['email']
        password = postData['password']
        confirm = postData['confirm']
        if len(name) < 2:
            msg.append("Name field cannot be blank, and must contain least 2 letters")
        elif not name_regex.match(name):
            msg.append("Name field can only contain letters")
        if len(alias) < 0:
            msg.append("Please enter an alias")
        if len(email) < 1:
            msg.append("Email fields cannot be blank")
        elif len(User.objects.filter(email=email)) > 0:
            msg.append("Email address already taken")
        elif not EMAIL_REGEX.match(email):
            msg.append("Invalid email format")
        if len(password) < 1:
            msg.append("Password field cannot be blank")
        elif len(password) < 8:
            msg.append("Password must be at least 8 characters")
        elif not PASSWORD_REGEX.match(password):
            msg.append("Password must contain: 1 uppercase letter, 1 lowercase letter, and 1 number")
        if not password == confirm:
            msg.append('Must match password')
        if not msg:
            valid = True
            pwhash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            User.objects.create(name=name, alias=alias, email=email, password=pwhash)
        else:
            valid = False
        status.update({'valid': valid, 'msg': msg})

        return status

    def log(self, postData):
        status = {}
        msg = []
        email = postData['elog']
        password = postData['plog']
        if len(email) < 1 or len(password) < 1:
            msg.append("Login fields cannot be blank.")
        else:
            user_info = User.objects.filter(email=email)
            if not user_info:
                msg.append("Invalid user. Please Register")
            elif not bcrypt.checkpw(password.encode(), user_info[0].password.encode()):
                msg.append("Invalid password. Please Register")
        if not msg:
            valid = True
            status.update({'user_id': user_info[0].id})
        else:
            valid = False
            status.update({'msg': msg})
        status.update({'valid': valid})
        return status


class User(models.Model):
    name = models.CharField(max_length=45)
    alias = models.CharField(max_length=45)
    email = models.EmailField(max_length=45, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = Umanager()

class Author(models.Model):
    author = models.CharField(max_length=45, null=True, blank=True, unique=True)
    objects = Umanager()


class Book(models.Model):
    title = models.CharField(max_length=45, null=True, blank=True)
    author = models.ForeignKey(Author, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = Umanager()


class Review(models.Model):
    review = models.TextField(max_length=100)
    rating = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    book = models.ForeignKey(Book, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = Umanager()


class AddBook(object):
    def __init__(self):
        self.book_errors = []
        self.is_valid = True
        pass

    def a_review(self, data, user, book):
        self.validate_review(data)
        if self.is_valid:
            Review.objects.create(review=data['review'], rating=data['rating'], user=user, book=book)

    def a_book(self, data, author, user):
        book = Book.objects.create(title=data['title'], author=author)
        self.a_review(data, user, book)
        # Book.objects.new(title=title, author=Author.objects.get(id=id))

    def create_book(self, postData, user):
        self.validate_book(postData)
        if postData['new_author'] != "" and self.is_valid:
            if Author.objects.filter(author=postData['new_author']).exists():
                author = Author.objects.get(author=postData['new_author'])
                self.a_book(postData, author, user)
            else:
                author = Author.objects.create(author=postData['new_author'])
                self.a_book(postData, author, user)
        elif postData['author'] != '' and self.is_valid:
            author = Author.objects.get(author=postData['author'])
            self.a_book(postData, author, user)

    def validate_book(self, data):
        if data['title'] == '':
            self.book_errors.append("You have to add a title")
            self.is_valid = False
        if data['author'] == '' and data['new_author'] == '':
            self.book_errors.append("You have to add, or select an author")
            self.is_valid = False
        self.validate_review(data)
        pass

    def validate_review(self, data):
        if data['rating'] == '':
            self.book_errors.append("You have to select a rating")
            self.is_valid = False
        if data['review'] == '':
            self.book_errors.append("You have to enter a review")
            self.is_valid = False
