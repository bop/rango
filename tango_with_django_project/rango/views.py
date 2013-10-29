from django.template import RequestContext
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response


def index(request):
    context = RequestContext(request)
    context_dict = {'boldmessage': "I am from the context"}
    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    context = RequestContext(request)
    return render_to_response('rango/about.html', context)
