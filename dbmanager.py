#!/usr/bin/env python2
# vim: fileencoding=utf-8:nomodified

import MySQLdb
import threading
from resources import *

class MysqlConnectionManager():
		"given the right parameters connect to the database"
		def __init__(self, dbhost, dbuser, dbpassword, database):
				self.dbhost = dbhost
				self.dbuser = dbuser
				self.dbpassword = dbpassword
				self.database = database
				conn = MySQLdb.connect(
								host = self.dbhost, 
								user = self.dbuser, 
								passwd = self.dbpassword, 
								db = self.database
								)
				assert isinstance(conn, MySQLdb.connections.Connection)
				self.conn = conn

		def __del__(self):
				if self.conn:
						self.conn.close()

		def getMysqlConnection(self):
				return self.conn

class ResourceSilos():
		def __init__(self):
				self.__reslist = list()
				self.__reslock = threading.Condition()
		def getRes(self):
				self.__reslock.acquire()
				while len(self.__reslist) <= 0:
						self.__reslock.wait()
				result = self.__reslist.pop()
				self.__reslock.release()
				return result
		def addRes(self, resource):
				self.__reslock.acquire()
				self.__reslist.append(resource)
				self.__reslock.notify()
				self.__reslock.release()

class ResourceStorer(MysqlConnectionManager, threading.Thread):
		def __init__(self, dbhost, dbuser, dbpassword, database, silos):
				MysqlConnectionManager.__init__(self, dbhost, dbuser, dbpassword, database)
				threading.Thread.__init__(self)
				self.silos = silos
		def store(self, resource):
				resource.makeTags()
				print resource
				cursor = self.conn.cursor()
				self.__insertRes(cursor, resource)
				for tag in resource.tags:
						self.__insertTags(cursor, resource.uri, tag)
				self.conn.commit()
				cursor.close()
		def __insertRes(self, cursor, resource):
				insertionstring = """
				REPLACE INTO resources (
						uri, 
						server,
						filetype
				) VALUES (
				'%s', '%s', '%s')""" % (
						resource.uri.strip().replace("'","\\'"),
						resource.server,
						resource.filetype
				)
				cursor.execute(insertionstring)
		def __insertTags(self, cursor, uri, tag):
				insertionstring = """
				REPLACE INTO tags (
						uri,
						tag
				) VALUES (
				'%s', '%s')""" % (
						uri.strip().replace("'","\\'"),
						tag
				)
				cursor.execute(insertionstring)
		def run(self):
				while(True):
						r = self.silos.getRes()
						self.store(r)

class QueryMaker(MysqlConnectionManager):
		def query(self, query):
				query.makeTags()
				#print query
				andres = list()
				orres = list()
				cursor = self.conn.cursor()
				if len(query.tags) >= 2:
						andres += self.__andquery(cursor, list(query.tags))
				#TODO: orquery of each tags power subset?
				#TODO: query based on timestamp:
				#		first recent 
				#		then go back in time (last 24*7h, 24*7*4h, 24*7*4*12h)
				#
				if len(andres) < 50:
						orres += self.__orquery(cursor, list(query.tags))
				cursor.close()
				return [andres, orres]
		def __orquery(self, cursor, tags):
				if len(tags) <=0:
						return []
				selectionstring = """
				SELECT resources.uri, resources.server, resources.filetype 
				FROM resources JOIN tags ON resources.uri = tags.uri
				WHERE tags.tag = '%s'""" % tags[0]
				for tag in tags[1:]:
						selectionstring += "OR tags.tag = '%s'" % tag
				cursor.execute(selectionstring)
				r = [Resource(uri=e[0], server=e[1], filetype=[2]) for e in cursor.fetchall()]
				return r
		def __andquery(self, cursor, tags):
				if len(tags) <=0:
						return []
				selectionstring = """
				SELECT resources.uri, resources.server, resources.filetype 
				FROM resources JOIN tags AS t0 ON resources.uri = t0.uri """ 
				for i in range(1,len(tags)):
						selectionstring += "JOIN tags as t%d ON t%d.uri = t%d.uri " % (i, i-1, i)
				selectionstring += "WHERE t0.tag = '%s' " % tags[0]
				for i in range(1,len(tags)):
						selectionstring += "AND t%d.tag = '%s' " % (i, tags[i])
				cursor.execute(selectionstring)
				r = [Resource(uri=e[0], server=e[1], filetype=[2]) for e in cursor.fetchall()]
				return r


if __name__ == "__main__":
		rs = ResourceStorer('localhost','ninuu','ciaociao','ninuxuu')
		r = Resource(uri="test://just/a.test/right_now", comments="films", filetype=Filetype.VIDEO)
		#rs.store(r)
		qm = QueryMaker('localhost','ninuu','ciaociao','ninuxuu')
		q = Query("ninux etnica")
		r = qm.query(q)
		print r



