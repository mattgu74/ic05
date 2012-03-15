
import urllib.request




node = {'url': 'http://www.google.fr/index.php'}
req = str(node).replace("'", '"')

r = urllib.request.urlopen("http://localhost:8080/_rest_/add_page", req.encode())
print(r.read())


node = {'source' : 'http://www.bonjour.fr/index.php', 'target': 'http://www.hello.com'}
req = str(node).replace("'", '"')

r = urllib.request.urlopen("http://localhost:8080/_rest_/add_link", req.encode())
print(r.read())

url = {'url': "http://www.google.fr/index.php"}
req = str(url).replace("'",'"')
r = urllib.request.urlopen("http://localhost:8080/_rest_/url_need_a_visit", req.encode())
print(r.read())

url = {'url': "http://www.ahahah.fr/index.php"}
req = str(url).replace("'",'"')
r = urllib.request.urlopen("http://localhost:8080/_rest_/url_need_a_visit", req.encode())
print(r.read())

req = str({'nb_max':45}).replace("'",'"')
r = urllib.request.urlopen("http://localhost:8080/_rest_/get_urls_to_visit", req.encode())
print(r.read())

