import pprint
import ajax
import load_json

lookup = {
	'printhello': ajax.printhello,
	'quit': ajax.quit,
	'leftcontent': ajax.leftcontent,
	'rightcontent': ajax.rightcontent,
	'setfooter': ajax.setfooter,
	'csvexport': ajax.csvexport,
	'filter': ajax.filter
}

def call(myfunc,*args):
	if lookup.has_key(myfunc):
                #print "\tAjax load :"+myfunc
		return lookup[myfunc](*args) 
	else:
		print "ERROR : Couldn't find python function ["+myfunc+"]"  
		return "Couldn't find ["+myfunc+"]"  

