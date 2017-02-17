from django.http import HttpResponseForbidden
from django.shortcuts import render, render_to_response, redirect
from django.core.cache import cache

from django.utils.crypto import get_random_string

from users.models import User


def authenticated(request):
    session = request.session
    login_token = session.get('login_token', False)

    if login_token:
        if login_token == cache.get(session['user_email']):
            cache.set(session.get('user_email'), session.get('login_token'), nx=False)
            session['login_token'] = login_token
            request.session.set_expiry(300)
            return True
    return False


def signup(request):

    if request.method == 'POST':
        form = request.POST
        g = 0 if form['gender_info'] == "male" else 1
        month = '%02d' % int(form['birthday_month'])
        day = '%02d' % int(form['birthday_day'])

        if User.objects.filter(email=form['rinput-email']):
            return render(request, 'login/index.html', {'error': 'Email is already exist.'})

        user = User.objects.create(
            name = form['rinput-name'],
            email = form['rinput-email'],
            pwd = form['rinput-password'],
            gender = g,
            birth = form['birthday_year'] + month + day,
            address = "",
            friend_list = [],
            friend_request_list = [],
            arture_list = [],
            article_list = [],
        )
        user.save()

        login_token = get_random_string(length=32)
        cache.set(form['rinput-email'], login_token, nx=False)


        request.session['user_objectId'] = user.id
        request.session['user_email'] = form['rinput-email']
        request.session['user_name'] = form['rinput-name']
        request.session['login_token'] = login_token
        request.session.set_expiry(300)

    return redirect('/users/' + user.id + '/newsfeed')


def signin(request):
    if request.method == 'POST':
        form = request.POST

        if User.objects.filter(email=form['input-email']):

            user = User.objects.get(email=form['input-email']) # try User.objects.get
            user_name = user.name
            user_email = user.email
            user_pwd = user.pwd
            user_objectId = user.id

            if user_pwd != form['input-pswd']:
                return render(request, 'login/index.html', {'error': 'Wrong password'})

            login_token = get_random_string(length=32)
            cache.set(form['input-email'], login_token, nx=False)

            request.session['user_objectId'] = user_objectId
            request.session['user_email'] = user_email
            request.session['user_name'] = user_name
            request.session['login_token'] = login_token
            request.session.set_expiry(300)

            return redirect('/users/' + user.id + '/newsfeed')

        else:
            return render(request, 'login/index.html', {'error': 'Id does not exist'})

    else:
        return render(request, 'login/index.html', {})


def signout(request):
    request.session.flush()
    return redirect('/login/')