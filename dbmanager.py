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


class QueryResultS():
		def __init__(self):
				self.resultlist = list()
				self.labels = list()
		def getLen(self):
				return sum([len(li) for li in self.resultlist])
		def addResultList(self, reslist, taglist, boolword="AND" ):
				if not reslist or not taglist:
						return
				self.resultlist.append(reslist)
				label = taglist[0] 
				for tag in taglist[1:]:
						label += " %s %s" % (boolword, tag)
				self.labels.append(label)


class QueryMaker(MysqlConnectionManager):
		targetresults = 500
		likes = 5
		def query(self, query):
				query.makeTags()
				qr = QueryResultS()
				cursor = self.conn.cursor()
				# separate good from bad
				goodtags = []
				badtags = []
				alltags = list(query.tags)
				for tag in alltags:
						if self.__tagstat(cursor, tag) > 0:
								goodtags.append(tag)
						else:
								badtags.append(tag)
				if len(goodtags) >= 2:
						qr.addResultList(self.__andquery(cursor, goodtags), goodtags, "AND")
				usedtags = []
				if qr.getLen() < self.targetresults:
						qr.addResultList(self.__orquery(cursor, goodtags), goodtags, "OR")
						usedtags += goodtags
				if len(badtags) and qr.getLen() < self.targetresults:
						lim = self.likes / len(badtags) 
						liketags = []
						for bt in badtags:
								liketags += self.__taglike(cursor, bt, lim)
						liketags = list(set(liketags).difference(set(badtags)).difference(set(usedtags)))
						qr.addResultList(self.__orquery(cursor, liketags), liketags, "OR")
						usedtags += liketags
				if len(goodtags) and qr.getLen() < self.targetresults:
						lim = self.likes / len(goodtags) 
						liketags = []
						for gt in goodtags:
								liketags += self.__taglike(cursor, gt, lim)
						liketags = list(set(liketags).difference(set(goodtags)).difference(set(usedtags)))
						qr.addResultList(self.__orquery(cursor, liketags), liketags, "OR")
						usedtags += liketags
				for j in range(4):
						if qr.getLen() < self.targetresults:
								tmptags = [tag[:-j] for tag in alltags if len(tag[:-j]) > 1]
								if not len(tmptags):
										continue
								lim = self.likes / len(tmptags)
								liketags = []
								for tt in tmptags:
										liketags += self.__taglike(cursor, tt, lim)
								liketags = list(set(liketags).difference(set(tmptags)).difference(set(usedtags)))
								qr.addResultList(self.__orquery(cursor, liketags), liketags, "OR")
								usedtags += liketags

				cursor.close()
				return qr
		def __orquery(self, cursor, tags, timediff=2419200):
				if len(tags) <=0:
						return []
				selectionstring = """
				SELECT resources.uri, resources.server, resources.filetype 
				FROM resources JOIN tags ON resources.uri = tags.uri
				WHERE (resources.timestamp+0 >= NOW()+0 - %d) AND (tags.tag = '%s' """ % (timediff, tags[0])
				for tag in tags[1:]:
						selectionstring += "OR tags.tag = '%s'" % tag
				selectionstring += ") ORDER BY resources.uri DESC"
				cursor.execute(selectionstring)
				r = [Resource(uri=e[0], server=e[1], filetype=e[2]) for e in cursor.fetchall()]
				return r
		def __andquery(self, cursor, tags, timediff=2419200):
				if len(tags) <=0:
						return []
				selectionstring = """
				SELECT resources.uri, resources.server, resources.filetype 
				FROM resources JOIN tags AS t0 ON resources.uri = t0.uri """ 
				for i in range(1,len(tags)):
						selectionstring += "JOIN tags as t%d ON t%d.uri = t%d.uri " % (i, i-1, i)
				selectionstring += "WHERE (resources.timestamp+0 >= NOW()+0 - %d) AND t0.tag = '%s' " % (timediff, tags[0])
				for i in range(1,len(tags)):
						selectionstring += "AND t%d.tag = '%s' " % (i, tags[i])
				selectionstring += "ORDER BY resources.uri DESC"
				cursor.execute(selectionstring)
				r = [Resource(uri=e[0], server=e[1], filetype=e[2]) for e in cursor.fetchall()]
				return r
		def __tagstat(self, cursor, tag, timediff=2419200):
				selectionstring = """
				SELECT tag, count(tag) AS tagcount 
				FROM tags 
				WHERE tag='%s' AND tags.timestamp+0 >= (NOW()+0 - 31536000) 
				GROUP BY tag
				""" % tag
				cursor.execute(selectionstring)
				r = cursor.fetchone()
				if r:
						return int(r[1])
				else:
						return 0
		def __taglike(self, cursor, tag, limit=3, timediff=2419200):
				selectionstring = """
				SELECT tag
				FROM tags 
				WHERE tag LIKE '%%%s%%' AND tags.timestamp+0 >= (NOW()+0 - 31536000) 
				GROUP BY tag
				ORDER BY COUNT(tag) DESC
				LIMIT %d
				""" % (tag, limit)
				cursor.execute(selectionstring)
				return [e[0] for e in cursor.fetchall()]


if __name__ == "__main__":
		rs = ResourceStorer('localhost','ninuu','ciaociao','ninuxuu')
		r = Resource(uri="test://just/a.test/right_now", comments="films", filetype=Filetype.VIDEO)
		#rs.store(r)
		qm = QueryMaker('localhost','ninuu','ciaociao','ninuxuu')
		q = Query("ninux etnica")
		r = qm.query(q)
		print r



