#!/usr/bin/env python
# vim:fileencoding=utf-8:syntax=python:nomodified

# ninuXoo's JSON interface

import json
import time
from dbmanager import QueryMaker
from resources import Query

RESPONSE_OK = 200
RESPONSE_REQERROR = 400
RESPONSE_SERVERERROR = 500
RESPONSE_NOTIMPLEMENTED = 501

ERRORDICT = {
				RESPONSE_OK: "OK",
				RESPONSE_REQERROR: "Bad Request",
				RESPONSE_SERVERERROR: "Server Error",
				RESPONSE_NOTIMPLEMENTED: "Not Implemented"
}


class JSONError(Exception):
		"JSON API generic error"
		pass


class JSONSyntaxError(Exception):
		"JSON syntax error"
		pass

class Request(dict):
		def __init__(self, requestdict = {}):
				dict.__init__(self)
				self.update(requestdict)

class JsonResponse(dict):
		def __init__(self, responsen, description=None, responsedict = {}):
				dict.__init__(self)
				try:
						dict.__setitem__(self, 'responsen', responsen)
						if description:
								dict.__setitem__(self, 'response', description)
						else:
								dict.__setitem__(self, 'response', ERRORDICT[responsen])
						self.update(responsedict)
				except Exception, e:
						raise JSONError(str(e))

		def dumps(self):
				return json.dumps(self, skipkeys=True)
		

class JSONProcessor():
		"Process JSON requests and return JSON responses, through the process() function"
		def __init__(self):
				try:
						self.qm = QueryMaker('localhost','ninuu','ciaociao','ninuxuu') #FIXME
						self.initialized = True
				except Exception,e:
						self.qm = None
						self.initialized = False
		
		def process(self, requestdict):
				"select the appropriate handler for the request"
				if not self.initialized:
						response = JsonResponse(RESPONSE_SERVERERROR)
						return response.dumps()

				try:
						req = Request(requestdict)
				except Exception, e:
						response = JsonResponse(RESPONSE_REQERROR, "Bad Request [%s]" % str(e))
						return response.dumps()
				
				if not req.has_key('op') or (req['op'] == ''):
						response = JsonResponse(RESPONSE_REQERROR, "Bad Request [op field missing]")
						return response.dumps()
				
				# small python magic to call the method that has the same name of the request
				if req['op'] in self.__class__.__dict__:
						response = self.__class__.__dict__[req['op']](self, req)
				else:
						response = JsonResponse(RESPONSE_NOTIMPLEMENTED)

				return response.dumps()

		def resourcestats(self, request):
				"return the number of resources indexed by the search engine"
				try:
						res = self.qm.getResourceStats()
						response = JsonResponse(RESPONSE_OK, None, {'result': res})
				except Exception, e:
						response = JsonResponse(RESPONSE_SERVERERROR)
				return response

		def serverstats(self, request):
				"return the number of servers indexed by the search engine"
				try:
						res = self.qm.getServerStats()
						response = JsonResponse(RESPONSE_OK, None, {'result': res})
				except Exception, e:
						response = JsonResponse(RESPONSE_SERVERERROR)
				return response

		def __fillresponse(self, resp, searchtime, q=""):
				finallist = list()
				for res1 in resp.resultlistlist:
						resourcetrie = res1.getTrie()
						resourcetrie.prune()
						res1dict = {
										'resultlabel': res1.label,
										'exactresult': res1.exactresult,
										'nresults': len(res1.resultlist),
										'resourcetrie': resourcetrie.dictify()
									}
						finallist.append(res1dict)

				response = JsonResponse(RESPONSE_OK, None, {
						'q': q,
						'nresults': resp.getLen(), 
						'nlabels': len(resp.getLabels()),
						'searchtime': searchtime, 
						'results': finallist
						})

				return response
		def query(self, request):
				try:
						if not request.has_key('q'):
								response = JsonResponse(RESPONSE_REQERROR, "Bad request: search term(s) missing")
								return response
						req = request['q']
								
						if request.has_key('nresults'):
								try: 
										nres = int(request['nresults'])
								except Exception, e:
										response = JsonResponse(RESPONSE_REQERROR, "Bad request [%s]" % str(e))
										return response
						else:
								nres = 200 #FIXME

						q = Query(req)

						if request.has_key('ip'):
								q.server = request['ip']

						if request.has_key('filetype'):
								q.filetype = request['filetype'].upper()

						tsta = time.time()
						resp = self.qm.query(q, nres)
						tend = time.time()
						searchtime = tend - tsta

						response = self.__fillresponse(resp, searchtime, req)

				except Exception, e:
						response = JsonResponse(RESPONSE_SERVERERROR, "Error [%s]" % str(e))

				return response

		def exactquery(self, request):
				try:
						if not request.has_key('q'):
								response = JsonResponse(RESPONSE_REQERROR, "Bad request: search term(s) missing")
								return response
						req = request['q']
								
						q = Query(req)

						if request.has_key('ip'):
								q.server = request['ip']

						if request.has_key('filetype'):
								q.filetype = request['filetype'].upper()

						tsta = time.time()
						resp = self.qm.exactquery(q)
						tend = time.time()
						searchtime = tend - tsta

						response = self.__fillresponse(resp, searchtime, req)

				except Exception, e:
						response = JsonResponse(RESPONSE_SERVERERROR, "Error [%s]" % str(e))

				return response

		def orquery(self, request):
				try:
						if not request.has_key('q'):
								response = JsonResponse(RESPONSE_REQERROR, "Bad request: search term(s) missing")
								return response
						req = request['q']

						q = Query(req)

						if request.has_key('ip'):
								q.server = request['ip']

						if request.has_key('filetype'):
								q.filetype = request['filetype'].upper()

						tsta = time.time()
						resp = self.qm.orquery(q)
						tend = time.time()
						searchtime = tend - tsta
						
						response = self.__fillresponse(resp, searchtime, req)

				except Exception, e:
						response = JsonResponse(RESPONSE_SERVERERROR, "Error [%s]" % str(e))

				return response

		def likequery(self, request):
				try:
						if not request.has_key('q'):
								response = JsonResponse(RESPONSE_REQERROR, "Bad request: search term(s) missing")
								return response
						req = request['q']
						
						if request.has_key('words'):
								try: 
										limit = int(request['words'])
								except Exception, e:
										response = JsonResponse(RESPONSE_REQERROR, "Bad request [%s]" % str(e))
										return response
						else:
								limit = 3 #FIXME
								
						q = Query(req)

						if request.has_key('ip'):
								q.server = request['ip']

						if request.has_key('filetype'):
								q.filetype = request['filetype'].upper()

						tsta = time.time()
						resp = self.qm.likequery(q, limit)
						tend = time.time()
						searchtime = tend - tsta
						response = self.__fillresponse(resp, searchtime, req)

				except Exception, e:
						response = JsonResponse(RESPONSE_SERVERERROR, "Error [%s]" % str(e))

				return response

		def whatsnew(self, request):
				try:
						if request.has_key('nresults'):
								try: 
										nres = int(request['nresults'])
								except Exception, e:
										response = JsonResponse(RESPONSE_REQERROR, "Bad request [%s]" % str(e))
										return response
						else:
								nres = 200 #FIXME
								
						tsta = time.time()
						resp = self.qm.getNewFiles(nres)
						tend = time.time()
						searchtime = tend - tsta
						
						response = self.__fillresponse(resp, searchtime, "")

				except Exception, e:
						response = JsonResponse(RESPONSE_SERVERERROR, "Error [%s]" % str(e))

				return response

