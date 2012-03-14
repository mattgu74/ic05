
import urllib.request




node = {'url': 'http://www.google.fr'}
req = str(node).replace("'", '"')

r = urllib.request.urlopen("http://localhost:8080/_rest_/add_page", req.encode())
print(r.read())


node = {'source' : 'http://www.utc.fr/index.php', 'target': 'http://www.bidon.com'}
req = str(node).replace("'", '"')

r = urllib.request.urlopen("http://localhost:8080/_rest_/add_link", req.encode())
print(r.read())



