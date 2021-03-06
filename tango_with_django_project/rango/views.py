from django.template import RequestContext
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

from .models import Category, Page
from .forms import CategoryForm, PageForm, UserForm, UserProfileForm
from .bing_search import run_query


@login_required
def restricted(request):
    return HttpResponse("Texte pour utilisateur connecté à Rango.")



def encode_url(str):
    return str.replace(' ', '_')

def decode_url(str):
    return str.replace('_', ' ')

def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    for cat in cat_list:
        cat.url = encode_url(cat.name)
    
    return cat_list

def index(request):
    context = RequestContext(request)
    category_list = Category.objects.order_by('-likes')[:12]
    context_dict = {'categories': category_list}
    for category in category_list:
        category.url = category.name.replace(' ', '_')

    response = render_to_response('rango/index.html', context_dict, context)
    visits = int(request.COOKIES.get('visits', '0'))
    
    if request.COOKIES.has_key('last_visit'):
        last_visit = request.COOKIES['last_visit']
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - last_visit_time).days > 0:
            response.set_cookie('visits', visits+1)
            response.set_cookie('last_visit', datetime.now())
    else:
        response.set_cookie('last_visit', datetime.now())
    return response


def about(request):
    context = RequestContext(request)    
    return render_to_response('rango/about.html', context)



# def category(request, category_name_url):
    # Request our context
    #context = RequestContext(request)

    # Change underscores in the category name to spaces.
    # URL's don't handle spaces well, so we encode them as underscores.
    #category_name = decode_url(category_name_url)

    # Build up the dictionary we will use as out template context dictionary.
    #context_dict = {'category_name': category_name, 'category_name_url': category_name_url}

    #cat_list = get_category_list()
    #context_dict['cat_list'] = cat_list

    #try:
        # Find the category with the given name.
        # Raises an exception if the category doesn't exist.
        # We also do a case insensitive match.
        #category = Category.objects.get(name__iexact=category_name)
        #context_dict['category'] = category
        # Retrieve all the associated pages.
        # Note that filter returns >= 1 model instance.
        #pages = Page.objects.filter(category=category).order_by('-views')

        # Adds our results list to the template context under name pages.
        #context_dict['pages'] = pages
    #except Category.DoesNotExist:
        # We get here if the category does not exist.
        # Will trigger the template to display the 'no category' message.
        #pass

    #if request.method == 'POST':
        #query = request.POST.get('query')
        #if query:
            #query = query.strip()
            #result_list = run_query(query)
            #context_dict['result_list'] = result_list

    # Go render the response and return it to the client.
    #return render_to_response('rango/category.html', context_dict, context)

def category(request, category_name_url):
    context = RequestContext(request)
    cat_list = get_category_list()
    category_name = decode_url(category_name_url)
    
    context_dict = {'cat_list': cat_list, 'category_name': category_name}

    try:
        category = Category.objects.get(name=category_name)

        # Add category to the context so that we can access the id and likes
        context_dict['category'] = category

        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        pass

    return render_to_response('rango/category.html', context_dict, context)



def add_category(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render_to_response('rango/add_category.html', {'form': form}, context)


def add_page(request, category_name_url):
    context = RequestContext(request)
    
    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)
            cat = Category.objects.get(name=category_name)
            page.category = cat

            page.views = 0

            page.save()

            return category(request, category_name)
        else:
            print form.errors
    else:
        form = PageForm()
    return render_to_response('rango/add_page.html', {'category_name_url': category_name_url, 'category_name': category_name, 'form': form}, context)



def register(request):
    context = RequestContext(request)
    
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render_to_response(
        'rango/register.html',
        {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}, context)


def user_login(request):
    context = RequestContext(request)
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Votre compte Rango est inactif.")
        else:
            print "Détails d'enregistrement invalides: {0}, {1}".format(username, password)
            return HttpResponse("Le login fourni est invalide.")
    else:
        return render_to_response('rango/login.html', {}, context)



@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')



def search(request):
    context = RequestContext(request)
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)

    return render_to_response('rango/search.html', {'result_list': result_list}, context)



def get_category_list():
    cat_list = Category.objects.all()

    for cat in cat_list:
        cat.url = encode_url(cat.name)

    return cat_list



@login_required
def like_category(request):
    context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes)




def suggest_category(request):
        context = RequestContext(request)
        cat_list = []
        starts_with = ''
        if request.method == 'GET':
                starts_with = request.GET['suggestion']
        else:
                starts_with = request.POST['suggestion']

                cat_list = get_category_list(8, starts_with)

        return render_to_response('rango/category_list.html', {'cat_list': cat_list }, context)
