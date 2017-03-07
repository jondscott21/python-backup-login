from django.shortcuts import render, redirect, HttpResponse
from .models import User, Book, Review, Author, AddBook
from django.contrib import messages
from django.db.models import Count

def index(request):
    if 'id' in request.session:
        return redirect('/books')
    return render(request, 'belt/index.html')


def process(request):
    if request.method == 'GET':
        return redirect('/')
    if request.method == 'POST':
        user_check = User.objects.reg(request.POST)
        print user_check
        if user_check['valid']:
            if 'id' not in request.session:
                new_user = User.objects.filter(email=request.POST['email'])[0]
                request.session['id'] = new_user.id
                messages.add_message(request, messages.INFO, 'Registration is successful')
                return redirect('/books')
        else:
            err_msg = user_check['msg']
            for val in err_msg:
                messages.add_message(request, messages.INFO, val)
            return redirect('/')


def log_in(request):
    if request.method == 'GET':
        return redirect('/')
    if request.method == 'POST':
        user_log = User.objects.log(request.POST)
        if user_log['valid']:
            if 'id' not in request.session:
                logged = User.objects.filter(email=request.POST['elog'])[0]
                request.session['id'] = logged.id
                return redirect('/books')
        else:
            log_err = user_log['msg']
            for val in log_err:
                messages.add_message(request, messages.INFO, val)
            return redirect('/')


def books(request):
    if 'id' not in request.session:
        messages.add_message(request, messages.INFO, "Must be logged in")
        return redirect('/')
    else:
        reviews = Review.objects.annotate(num_reviews=Count('review')).order_by('-created_at')[:3]
        context = {
            'reviews': reviews,
            'books': Book.objects.all(),
            'users': User.objects.get(id=request.session['id']),
        }
        return render(request, 'belt/books.html', context)


def book_id(request, id):
    book = Book.objects.get(id=id)
    reviews = Review.objects.filter(book=book)
    context = {
        'id': id,
        'book': book,
        'reviews': reviews
    }

    return render(request, 'belt/book_id.html', context)


def add(request):
    context = {
        'authors': Author.objects.all()
    }
    return render(request, 'belt/add.html', context)


def proc_book(request):
    if request.method == 'GET':
        return redirect('/')
    elif request.method == 'POST':
        user = User.objects.get(id=request.session['id'])
        addbook = AddBook()
        addbook.create_book(request.POST, user)
        if addbook.is_valid:
            return redirect('/books')
            pass
        else:
            for val in addbook.book_errors:
                messages.add_message(request, messages.INFO, val)
            return redirect('/add')


def proc_review(request, id):
    if request.method == 'GET':
        return redirect('/')
    elif request.method == 'POST':
        book = Book.objects.get(id=id)
        user = User.objects.get(id=request.session['id'])
        addbook = AddBook()
        addbook.a_review(request.POST, user, book)
        if addbook.is_valid:
            pass
        else:
            for val in addbook.book_errors:
                messages.add_message(request, messages.INFO, val)
        return redirect('/books/{}'.format(id))


def log_out(request):
    request.session.flush()
    return redirect('/')


def error(request):
    # print 'in side error'
    # messages.add_message(request, messages.INFO, "Page does not exist")
    return redirect('/')


def delete(request):

    pass


def user(request, id):
    user = User.objects.get(id=id)
    books = Book.objects.filter(review__user=user).distinct()
    context = {
        'user': user,
        'books': books
    }
    return render(request, 'belt/users.html', context)

    pass

