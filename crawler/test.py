

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


url = "http://www.google.fr"

#test_alchemy(url)
test_urllib(url)
