#!/usr/bin/env python2

import MySQLdb
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


class ResourceStorer(MysqlConnectionManager):
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
						filetype
				) VALUES (
				'%s', '%s')""" % (
						resource.uri,
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
						uri,
						tag
				)
				cursor.execute(insertionstring)

if __name__ == "__main__":
		rs = ResourceStorer('localhost','ninuu','ciaociao','ninuxuu')
		r = Resource(uri="test://just/a.test/right_now", comments="films", filetype=Filetype.VIDEO)
		rs.store(r)



