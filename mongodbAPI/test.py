

import pymongo
import datetime

connection = pymongo.Connection()#'mongodb-mattgu74.dotcloud.com', 80)
db = connection['test']
collection = db['posts']

new_posts = [
	{"title": "heyho"},
	{"title": "helo"},
	{"title": "TAHOUUUUU"}
]

#try:
r = collection.insert(new_posts, continue_on_error=True)#, upsert=True)#, upsert=True)#continue_on_error=True)
"""except Exception as ex:
	print(ex)
else:
	print(r)"""
print(r)
#help(collection.insert)
