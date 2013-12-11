from django import forms
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from calculator.models import *
from . import templater


################################################################
###   Main calculator page functionality

def process_request(request):
  '''View (action) method for /calculator/calculator.html'''
  # set up the form
  calc = None
  form = CalculatorForm()
  if request.method == 'POST':
    form = CalculatorForm(request.POST)
    if form.is_valid():
      calc = Calculation()
      calc.num1 = form.cleaned_data['num1']
      calc.num2 = form.cleaned_data['num2']
      calc.operation = '+'  # hard coding this for now
      calc.result = calc.num1 + calc.num2
      calc.save()
      
  # example of the url params
  first_two = request.urlparams[0] + request.urlparams[1]
  # now do something with first_two variable
  
  # render the template for this page
  template_vars = {
    'form': form, 
    'calc': calc,
  }
  return templater.render_to_response(request, 'calc.html', template_vars)



class CalculatorForm(forms.Form):
  '''A simple example form that adds two numbers'''
  num1 = forms.IntegerField()
  num2 = forms.IntegerField()
  
  # cleaning methods would normally go here
    
  
  
#################################################################
###   Ajax call to get the log.  This is an example of how
###   you can have multiple view functions per file.  This
###   view is called with /calculator/calc__loadlog.html:
###      - calculator is the app
###      - calc.py is the module
###      - process_request__loadlog() is the function
###   Although you'd normally have one function per module (called
###   process_request), this ability allows you to group Ajax calls
###   together.

def process_request__loadlog(request):
  '''View method for /calculator/calc__loadlog.html'''
  return templater.render_to_response(request, 'calc__loadlog.html', {
    'calculations': Calculation.objects.order_by('log_date')
  })
  
  
  
  
################################################################
###   Ajax call to delete the log.  See process_request__loadlog
###   above for an explanation of how this gets called.

def process_request__deletelog(request):
  '''View method for /calculator/calc__deletelog.html'''
  # delete the calculations
  for c in Calculation.objects.all():
    c.delete()
    
  # normally we'd call a template here, but this really don't have much to send back.
  # it's a great example of returning the html directly from the view 
  return HttpResponse('The log is empty.')

  