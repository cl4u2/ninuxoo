#!/usr/bin/env python2
# vim: fileencoding=utf-8:nomodified

import MySQLdb
import threading
import collections
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
				self.__reslist = collections.deque()
				self.__reslock = threading.Condition()
		def getRes(self):
				self.__reslock.acquire()
				while len(self.__reslist) <= 0:
						self.__reslock.wait()
				result = self.__reslist.popleft()
				self.__reslock.release()
				return result
		def addRes(self, resource):
				self.__reslock.acquire()
				self.__reslist.append(resource)
				self.__reslock.notify()
				self.__reslock.release()
		def moreToGo(self):
				self.__reslock.acquire()
				res = len(self.__reslist)
				self.__reslock.release()
				return res > 0

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
				self.alldone = False
				self.commitcounter = 0
		def store(self, resource, commitN=1):
				resource.makeTags()
				print resource
				cursor = self.conn.cursor()
				self.__insertRes(cursor, resource)
				self.commitcounter += 1
				for tag in resource.tags:
						self.__insertTags(cursor, resource.uri, tag)
						if self.commitcounter >= commitN:
								self.conn.commit()
								self.commitcounter = 0
						else:
								self.commitcounter += 1
				cursor.close()
		def commit(self):
				print "committing..."
				self.conn.commit()
		def __insertRes(self, cursor, resource):
				sserver = resource.server.strip().replace("'","\\'").encode('utf-8', errors='ignore')
				sprotocol =	resource.protocol.strip().replace("'","\\'").encode('utf-8', errors='ignore')
				spath = resource.path.strip().replace("'","\\'").encode('utf-8', errors='ignore')
				sshare = resource.getShare().strip().replace("'","\\'").encode('utf-8', errors='ignore')
				sfiletype = resource.filetype.strip().replace("'","\\'").encode('utf-8', errors='ignore')
				insertionstring = """
				INSERT INTO resources (
						uri, 
						server,
						share,
						protocol,
						path,
						filetype,
						firstseen,
						timestamp
				) VALUES (
				'%s', '%s', '%s', '%s', '%s', '%s', NOW(), NOW()
				) ON DUPLICATE KEY UPDATE 
					server = '%s',
					share = '%s',
					protocol = '%s',
					path = '%s',
					filetype = '%s',
					timestamp = NOW()
				""" % (
						resource.uri.strip().replace("'","\\'").encode('utf-8', errors='ignore'),
						sserver,
						sshare,
						sprotocol,
						spath,
						sfiletype,
						sserver,
						sshare,
						sprotocol,
						spath,
						sfiletype,
				)
				cursor.execute(insertionstring)
		def __insertTags(self, cursor, uri, tag):
				try:
						insertionstring = """
						REPLACE INTO tags (
								uri,
								tag
						) VALUES (
						'%s', '%s')""" % (
								uri.strip().replace("'","\\'").encode('utf-8', errors='ignore'),
								tag.encode('utf-8', errors='ignore')
						)
				except UnicodeDecodeError:
						return
				cursor.execute(insertionstring)
		def run(self):
				i = 0
				while (not self.alldone) or self.silos.moreToGo():
						r = self.silos.getRes()
						self.store(r, commitN=100)
						i += 1
				self.commit() #using a single final commit can save a lot of time but not sure if can handle single SQL errors
				print "%d insertions" % i
		def allFinished(self):
				self.alldone = True
		def __deleteOldResourceEntries(self, cursor, age):
				deletionstring = """
				DELETE FROM resources
				WHERE UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(timestamp) > %d
				""" % age
				cursor.execute(deletionstring)
		def __deleteOldTagEntries(self, cursor, age):
				deletionstring = """
				DELETE FROM tags
				WHERE UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(timestamp) > %d
				""" % age
				cursor.execute(deletionstring)
		def __del__(self):
				cursor = self.conn.cursor()
				self.__deleteOldTagEntries(cursor, TIMEDIFF)
				self.__deleteOldResourceEntries(cursor, TIMEDIFF)
				self.conn.commit()

#TODO: move to resources?
class QueryResult1(): 
		def __init__(self, resultlist, exactresult, label):
				self.resultlist = resultlist
				self.exactresult = exactresult
				self.label = label
		def getTrie(self):
				trie = ResourceTrie()
				for r in self.resultlist:
						trie.insert(r)
				return trie
		def __len__(self):
				return len(self.resultlist)
		def __eq__(self, other):
				return self.getTrie() == other.getTrie()
		def __ne__(self, other):
				return not self.__eq__(other)

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
						qr.addResultList(self.__andquery(cursor, goodtags, server=query.server, filetype=query.filetype), goodtags, "+", True)
				usedtags = []
				if qr.getLen() < targetresults:
						for tag in goodtags:
								qr.addResultList(self.__orquery(cursor, [tag], server=query.server, filetype=query.filetype), [tag], "/", len(goodtags) == 1)
						usedtags += goodtags
				if len(badtags) > 0 and qr.getLen() < targetresults:
						lim = 1 + self.likes / len(badtags) 
						liketags = []
						for bt in badtags:
								liketags += self.__taglike(cursor, bt, lim)
						liketags = list(set(liketags).difference(set(badtags)).difference(set(usedtags)))
						for tag in liketags:
								if qr.getLen() < targetresults:
										qr.addResultList(self.__orquery(cursor, [tag], server=query.server, filetype=query.filetype), [tag], "OR", False)
										usedtags.append(tag)
				if len(goodtags) > 0 and qr.getLen() < targetresults:
						lim = 1 + self.likes / len(goodtags) 
						liketags = []
						for gt in goodtags:
								liketags += self.__taglike(cursor, gt, lim)
						liketags = list(set(liketags).difference(set(goodtags)).difference(set(usedtags)))
						for tag in liketags:
								if qr.getLen() < targetresults:
										qr.addResultList(self.__orquery(cursor, [tag], server=query.server, filetype=query.filetype), [tag], "OR", False)
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
												qr.addResultList(self.__orquery(cursor, [tag], server=query.server, filetype=query.filetype), [tag], "OR", False)
										usedtags.append(tag)

				cursor.close()
				return qr
		def __orquery(self, cursor, tags, server=None, filetype=None, timediff=TIMEDIFF):
				if len(tags) <=0:
						return []
				selectionstring = """
				SELECT resources.uri, resources.server, resources.filetype 
				FROM resources JOIN tags ON resources.uri = tags.uri
				WHERE (UNIX_TIMESTAMP(resources.timestamp) >= UNIX_TIMESTAMP(NOW()) - %d) """ % timediff
				if server:
						selectionstring += " AND resources.server = '%s' " % server
				if filetype:
						selectionstring += " AND resources.filetype = '%s' " % filetype
				selectionstring += " AND (tags.tag = '%s' " % tags[0]
				for tag in tags[1:]:
						selectionstring += " OR tags.tag = '%s' " % tag
				selectionstring += ") ORDER BY resources.uri DESC"
				cursor.execute(selectionstring)
				r = [Resource(uri=e[0], server=e[1], filetype=e[2]) for e in cursor.fetchall()]
				return r
		def __andquery(self, cursor, tags, server=None, filetype=None, timediff=TIMEDIFF):
				if len(tags) <=0:
						return []
				selectionstring = """
				SELECT resources.uri, resources.server, resources.filetype 
				FROM resources JOIN tags AS t0 ON resources.uri = t0.uri """ 
				for i in range(1,len(tags)):
						selectionstring += "JOIN tags as t%d ON t%d.uri = t%d.uri " % (i, i-1, i)
				selectionstring += " WHERE (UNIX_TIMESTAMP(resources.timestamp) >= UNIX_TIMESTAMP(NOW()) - %d) " % timediff
				if server:
						selectionstring += " AND resources.server = '%s' " % server
				if filetype:
						selectionstring += " AND resources.filetype = '%s' " % filetype
				selectionstring += " AND t0.tag = '%s' " % tags[0]
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

		def exactquery(self, query):
				query.makeTags()
				qr = QueryResultS()
				cursor = self.conn.cursor()
				alltags = list(query.tags)
				qr.addResultList(self.__andquery(cursor, alltags, server=query.server, filetype=query.filetype), alltags, "+", True)
				cursor.close()
				return qr

		def orquery(self, query):
				query.makeTags()
				qr = QueryResultS()
				cursor = self.conn.cursor()
				alltags = list(query.tags)
				qr.addResultList(self.__orquery(cursor, alltags, server=query.server, filetype=query.filetype), alltags, "/", True)
				cursor.close()
				return qr
		
		def likequery(self, query, limit=3):
				query.makeTags()
				qr = QueryResultS()
				cursor = self.conn.cursor()
				alltags = list(query.tags)
				liketags = list()
				for t in alltags:
						liketags += self.__taglike(cursor, t, limit/len(alltags))
				liketags = list(set(liketags).difference(set(alltags)))
				for t in liketags:
						qr.addResultList(self.__orquery(cursor, [t], server=query.server, filetype=query.filetype), [t], "/", False)
				cursor.close()
				return qr

		def __getServerList(self, cursor, timediff=TIMEDIFF):
				selectionstring = """
				SELECT resources.server
				FROM resources
				WHERE UNIX_TIMESTAMP(resources.timestamp) >= UNIX_TIMESTAMP(NOW()) - %d
				GROUP BY resources.server""" % timediff
				cursor.execute(selectionstring)
				r = [e[0] for e in cursor.fetchall()]
				return r
		def getServerList(self):
				qr = QueryResultS()
				cursor = self.conn.cursor()
				return self.__getServerList(cursor)

		def __getShares(self, cursor, timediff=TIMEDIFF):
				selectionstring = """
				SELECT resources.server, resources.share
				FROM resources
				WHERE UNIX_TIMESTAMP(resources.timestamp) >= UNIX_TIMESTAMP(NOW()) - %d AND resources.share != "NULL" and length(resources.share) > 0 
				GROUP BY resources.server, resources.share
				ORDER BY resources.server
				""" % timediff
				cursor.execute(selectionstring)
				r = [(e[0], e[1]) for e in cursor.fetchall()]
				return r
		def getShares(self):
				qr = QueryResultS()
				cursor = self.conn.cursor()
				return self.__getShares(cursor)


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



