


import sys
import traceback
import urllib.parse
import re
import threading

re_whiteblank = re.compile('\s+')

def get_traceback():
	tb = sys.exc_info()[2]
	return "\n".join(traceback.format_tb(tb))
	

def normalize_url(base_url, url):
	url = re_whiteblank.sub('',url)
	split = urllib.parse.urlsplit(url)
	if not split.hostname:
		if split.geturl().startswith('http'):
			lprint("ATTENTION URL MAL PARSE", split.geturl())
		url = urllib.parse.urljoin(base_url, split.geturl())
		split = urllib.parse.urlsplit(url)
	if not split.path:
		url += "/"
	return url.lower()


lock_print = threading.Lock()
def lprint(*args, **kwargs):
	lock_print.acquire()
	print(*args, **kwargs)
	lock_print.release()
