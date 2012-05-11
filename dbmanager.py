#!/usr/bin/env python2
# vim: fileencoding=utf-8:nomodified

import MySQLdb
import threading
from resources import *

TIMEDIFF = 259200  #3 days

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

class FakeSilos():
		def getRes(self):
				print "getRes"
		def addRes(self, resource):
				print resource

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
				sserver = resource.server.strip().replace("'","\\'").encode('utf-8', errors='ignore')
				sprotocol =	resource.protocol.strip().replace("'","\\'").encode('utf-8', errors='ignore')
				spath = resource.path.strip().replace("'","\\'").encode('utf-8', errors='ignore')
				sfiletype = resource.filetype.strip().replace("'","\\'").encode('utf-8', errors='ignore')
				insertionstring = """
				INSERT INTO resources (
						uri, 
						server,
						protocol,
						path,
						filetype,
						firstseen
				) VALUES (
				'%s', '%s', '%s', '%s', '%s', NOW())
				ON DUPLICATE KEY UPDATE 
					server = '%s',
					protocol = '%s',
					path = '%s',
					filetype = '%s'
				""" % (
						resource.uri.strip().replace("'","\\'").encode('utf-8', errors='ignore'),
						sserver,
						sprotocol,
						spath,
						sfiletype,
						sserver,
						sprotocol,
						spath,
						sfiletype,
				)
				cursor.execute(insertionstring)
		def __insertTags(self, cursor, uri, tag):
				insertionstring = """
				REPLACE INTO tags (
						uri,
						tag
				) VALUES (
				'%s', '%s')""" % (
						uri.strip().replace("'","\\'").encode('utf-8', errors='ignore'),
						tag.encode('utf-8', errors='ignore')
				)
				cursor.execute(insertionstring)
		def run(self):
				while(True):
						r = self.silos.getRes()
						self.store(r)

class QueryResult1():
		def __init__(self, resultlist, exactresult, label):
				self.resultlist = resultlist
				self.exactresult = exactresult
				self.label = label
		def __len__(self):
				return len(self.resultlist)
		def getTrie(self):
				trie = ResourceTrie()
				for r in self.resultlist:
						trie.insert(r)
				return trie

class QueryResultS():
		def __init__(self):
				self.resultlistlist = list()
		def getLen(self):
				return sum([len(li.resultlist) for li in self.resultlistlist])
		def addResultList(self, reslist, taglist, boolword="AND", exactresult=False):
				if not reslist or not taglist:
						return
				label = taglist[0] 
				for tag in taglist[1:]:
						label += " %s %s" % (boolword, tag)
				qr1 = QueryResult1(reslist, exactresult, label)
				self.resultlistlist.append(qr1)
		def getLabels(self):
				return [li.label for li in self.resultlistlist]
		def getExactResults(self):
				return [li for li in self.resultlistlist if li.exactresult]
		def getOtherResults(self):
				return [li for li in self.resultlistlist if not li.exactresult]


class QueryMaker(MysqlConnectionManager):
		likes = 3
		stopliketags = ['SMB', 'FTP', 'HTTP']
		def query(self, query, targetresults=200):
				query.makeTags()
				qr = QueryResultS()
				cursor = self.conn.cursor()
				# separate the good from the bad
				goodtags = []
				badtags = []
				alltags = list(query.tags)
				tagstats = self.__tagstats(cursor, alltags)
				if len(tagstats) == 0:
						badtags = alltags[:]
				else:
						for tag in tagstats:
								if tagstats.has_key(tag) and tagstats[tag] > 0:
										goodtags.append(tag)
								else:
										badtags.append(tag)
				if len(goodtags) >= 2:
						qr.addResultList(self.__andquery(cursor, goodtags), goodtags, "+", True)
				usedtags = []
				if qr.getLen() < targetresults:
						for tag in goodtags:
								qr.addResultList(self.__orquery(cursor, [tag]), [tag], "/", len(goodtags) == 1)
						usedtags += goodtags
				if len(badtags) > 0 and qr.getLen() < targetresults:
						lim = 1 + self.likes / len(badtags) 
						liketags = []
						for bt in badtags:
								liketags += self.__taglike(cursor, bt, lim)
						liketags = list(set(liketags).difference(set(badtags)).difference(set(usedtags)))
						for tag in liketags:
								if qr.getLen() < targetresults:
										qr.addResultList(self.__orquery(cursor, [tag]), [tag], "OR", False)
										usedtags.append(tag)
				if len(goodtags) > 0 and qr.getLen() < targetresults:
						lim = 1 + self.likes / len(goodtags) 
						liketags = []
						for gt in goodtags:
								liketags += self.__taglike(cursor, gt, lim)
						liketags = list(set(liketags).difference(set(goodtags)).difference(set(usedtags)))
						for tag in liketags:
								if qr.getLen() < targetresults:
										qr.addResultList(self.__orquery(cursor, [tag]), [tag], "OR", False)
										usedtags.append(tag)
				for j in range(1,4):
						if qr.getLen() < targetresults:
								tmptags = [tag[:-j] for tag in alltags if len(tag[:-j]) > 1]
								if not len(tmptags):
										continue
								lim = self.likes / len(tmptags)
								liketags = []
								for tt in tmptags:
										liketags += self.__taglike(cursor, tt, lim)
								liketags = list(set(liketags).difference(set(tmptags)).difference(set(usedtags)))
								for tag in liketags:
										if qr.getLen() < targetresults:
												qr.addResultList(self.__orquery(cursor, [tag]), [tag], "OR", False)
										usedtags.append(tag)

				cursor.close()
				return qr
		def __orquery(self, cursor, tags, timediff=TIMEDIFF):
				if len(tags) <=0:
						return []
				selectionstring = """
				SELECT resources.uri, resources.server, resources.filetype 
				FROM resources JOIN tags ON resources.uri = tags.uri
				WHERE (UNIX_TIMESTAMP(resources.timestamp) >= UNIX_TIMESTAMP(NOW()) - %d) AND (tags.tag = '%s' """ % (timediff, tags[0])
				for tag in tags[1:]:
						selectionstring += "OR tags.tag = '%s'" % tag
				selectionstring += ") ORDER BY resources.uri DESC"
				cursor.execute(selectionstring)
				r = [Resource(uri=e[0], server=e[1], filetype=e[2]) for e in cursor.fetchall()]
				return r
		def __andquery(self, cursor, tags, timediff=TIMEDIFF):
				if len(tags) <=0:
						return []
				selectionstring = """
				SELECT resources.uri, resources.server, resources.filetype 
				FROM resources JOIN tags AS t0 ON resources.uri = t0.uri """ 
				for i in range(1,len(tags)):
						selectionstring += "JOIN tags as t%d ON t%d.uri = t%d.uri " % (i, i-1, i)
				selectionstring += "WHERE (UNIX_TIMESTAMP(resources.timestamp) >= UNIX_TIMESTAMP(NOW()) - %d) AND t0.tag = '%s' " % (timediff, tags[0])
				for i in range(1,len(tags)):
						selectionstring += "AND t%d.tag = '%s' " % (i, tags[i])
				selectionstring += "ORDER BY resources.uri DESC"
				cursor.execute(selectionstring)
				r = [Resource(uri=e[0], server=e[1], filetype=e[2]) for e in cursor.fetchall()]
				return r
		def __tagstats(self, cursor, taglist, timediff=TIMEDIFF):
				tagdict = {}
				if len(taglist) <= 0:
						return tagdict
				selectionstring = """
				SELECT tag, count(tag) AS tagcount 
				FROM tags 
				WHERE UNIX_TIMESTAMP(tags.timestamp) >= (UNIX_TIMESTAMP(NOW()) - %d) AND (tags.tag = '%s' """ % (timediff, taglist[0])
				for tag in taglist[1:]:
						selectionstring += "OR tags.tag = '%s'" % tag
				selectionstring += ") GROUP BY tag" 
				cursor.execute(selectionstring)
				r = cursor.fetchall()
				for row in r:
						tagdict.update({row[0]: row[1]})
				return tagdict
		def __taglike(self, cursor, tag, limit=3, timediff=TIMEDIFF):
				selectionstring = """
				SELECT tag
				FROM tags 
				WHERE tag LIKE '%s%%' AND UNIX_TIMESTAMP(tags.timestamp) >= (UNIX_TIMESTAMP(NOW()) - %d) 
				GROUP BY tag
				ORDER BY COUNT(tag) DESC
				LIMIT %d
				""" % (tag, timediff, limit)
				cursor.execute(selectionstring)
				return [e[0] for e in cursor.fetchall() if e[0] not in self.stopliketags]
		def getResourceStats(self):
				cursor = self.conn.cursor()
				return self.__resourcestats(cursor)
		def __resourcestats(self, cursor, timediff=TIMEDIFF):
				selectionstring = """
				SELECT count(uri) 
				FROM resources 
				WHERE UNIX_TIMESTAMP(timestamp) >= UNIX_TIMESTAMP(NOW()) - %d""" % timediff
				cursor.execute(selectionstring)
				return cursor.fetchone()[0]
		def getServerStats(self):
				cursor = self.conn.cursor()
				return self.__serverstats(cursor)
		def __serverstats(self, cursor, timediff=TIMEDIFF):
				selectionstring = """
				SELECT count(server) 
				FROM (
					SELECT server 
					FROM resources 
					WHERE UNIX_TIMESTAMP(timestamp) >= UNIX_TIMESTAMP(NOW()) - %d 
					GROUP by server) AS s """ % timediff
				cursor.execute(selectionstring)
				return cursor.fetchone()[0]
		def getNewFiles(self, n=50):
				qr = QueryResultS()
				cursor = self.conn.cursor()
				qr.addResultList(self.__getNewFiles(cursor, n), ['NOVIT&Agrave;'], True)
				return qr
		def __getNewFiles(self, cursor, n):
				selectionstring = """
				SELECT resources.uri, resources.server, resources.filetype, resources.firstseen
				FROM resources
				WHERE resources.firstseen != 0
				ORDER BY resources.firstseen DESC
				LIMIT %d
				""" % n
				cursor.execute(selectionstring)
				r = [Resource(uri=e[0], server=e[1], filetype=e[2], firstseen=e[3]) for e in cursor.fetchall()]
				return r


if __name__ == "__main__":
		rs = ResourceStorer('localhost','ninuu','ciaociao','ninuxuu')
		r = Resource(uri="test://just/a.test/right_now", comments="films", filetype=Filetype.VIDEO)
		rs.store(r)
		qm = QueryMaker('localhost','ninuu','ciaociao','ninuxuu')
		q = Query("right now")
		r = qm.query(q)
		print r
		r = Resource(uri="test://just/a.test/right_now", comments="films", filetype=Filetype.VIDEO)
		rs.store(r)



