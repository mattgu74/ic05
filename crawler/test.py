


def test_alchemy(url):
	import AlchemyAPI

	alchemy = AlchemyAPI.AlchemyAPI()
	alchemy.loadAPIKey("api_key.txt")

	params = AlchemyAPI.AlchemyAPI_KeywordParams()
	params.setMaxRetrieve(20)
	params.setKeywordExtractMode('strict')
	params.setOutputMode("json")

	result = alchemy.URLGetRankedKeywords(url, params)
	s = result.decode()
	json = eval(s)
	print(json)

def test_urllib(url):
	import urllib.request
	req = urllib.request.Request(url)
	req.add_header('User-agent', 'Galopa')
	stream = urllib.request.urlopen(req)
	s = stream.read()
	print(s)

def test_redirection(url):
	import urllib.request
	opener = urllib.request.FancyURLopener()
	opener.addheader('User-agent', 'Galopa')
	try:
		stream = opener.open(url)
	except Exception as ex:
		print(ex)
		return
	s = stream.read()
	print(s)

def test_urlparse():
	import urllib.parse as up
	import re
	url = "http: //www.hello.com"
	url = re.sub('\s','',url)
	p = up.urlsplit(url)
	print(p)
	print(p.geturl())

url = "http://www.google.fr"

#test_alchemy(url)
#test_urllib(url)
#test_redirection("http://www.cr-picardie.fr/spip.php?article709")
test_urlparse()
