# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
import django.contrib.auth as auth
from facepy import GraphAPI
from os import urandom
from base64 import urlsafe_b64encode

# Create your views here.
def login(request):


    if 'token' not in request.GET:
        redirect('/user/login')

    access_token = request.GET['token']
    graph = GraphAPI(access_token)

    info = graph.get('me?fields=name,email,verified')
    name = info['name']
    verified = info['verified']
    email = info['email']

    print '[FB info]:', name, verified, email

    if not verified:
        return render(request, 'login.html', {'error': 'FB 帳號未驗證'})

    try:
        user = User.objects.get(username=email)
        password = access_token
        user.set_password(password)
        user.save()
        user = auth.authenticate(username=email, password=password)

        if user.is_active:
            auth.login(request, user)

    except User.DoesNotExist:
        print 'email not found, add new user'
        user = User()
        user.username = email
        user.email = email
        user.last_name = name
        password = urlsafe_b64encode(urandom(16))[:-2]
        user.set_password(password)
        user.is_active = True
        user.save()
        user = auth.authenticate(username=email, password=password)

        print user
        if user.is_active:
            auth.login(request, user)

    return redirect('/')


