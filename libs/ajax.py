from jinja2 import Environment, FileSystemLoader
from os import curdir, sep, path
import os
import babel.dates
import pprint
from collections import OrderedDict

nofilter = "0" 
pp = pprint.PrettyPrinter(indent=4)
mypath = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(mypath, '../static/jinja')),
    trim_blocks=True)

def setfooter(args):
    out = args['json']['status']
    args['json']['status']['total'] = args['json']['status']['failures'] + args['json']['status']['ok'] + args['json']['status']['skipped'] +  args['json']['status']['unreachable']
    send = { "status" : args['json']['status'] }
    #print "left =", pp.pprint(send)
    data = readtemplate("footer.html",send)
    return data

def format_datetime(value, format='medium'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="y/MM/dd HH:mm:ss"
    return babel.dates.format_datetime(value, format)

TEMPLATE_ENVIRONMENT.filters['datetime'] = format_datetime

def filter(args):
  global nofilter
  out = args['filter'][0]
  nofilter = out
  return "done"

def csvexport(args):
    out = args['json']
    send = { "left" : args['json']['left'], "skipped" : args['json']['skipped'], "id" : args['json']['id'] }
    data = readtemplate("export.csv",send)
    return data

def leftcontent(args):
  global nofilter
  out = args['json']
    #print pp.pprint(out)
  send = { "left" : args['json']['left'], "skipped" : args['json']['skipped'], "id" : args['json']['id'] ,"filter" : nofilter }
    #print "left =", pp.pprint(send)
  data = readtemplate("leftcontent.html",send)
 # print "leftcontent = " + data
  return data

def rightcontent(args):
    server = args['server'][0]
    data = args['json']['servers'][server]
    data_sorted = OrderedDict(sorted(data.items(), key=lambda k: k[1]['epoch']))
    send = { "server" : args['server'] , "data" : data_sorted, "id" : args['json']['id'] }
    #print "right=", pp.pprint(send)
    data = readtemplate("rightcontent.html",send)
    return data

def readtemplate(template_filename, context):
    data = TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)
    return data

def quit(args):
    return "Quit"

def printhello(args):
    pp = pprint.PrettyPrinter(indent=4)
    return readtemplate("test.html") 
