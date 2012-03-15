


import sys
import traceback
import urllib.parse



def get_traceback():
	tb = sys.exc_info()[2]
	return "\n".join(traceback.format_tb(tb))

def normalize_url(base_url, url):
	split = urllib.parse.urlsplit(url)
	if not split.hostname:
		url = urllib.parse.urljoin(base_url, split.geturl())
		split = urllib.parse.urlsplit(url)
	if not split.path:
		url += "/"
	return url.lower()

	
