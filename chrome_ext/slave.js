


function Slave(host) {
	this.host = host;	// hostname du serveur

	this.running = false;
	this.url = "";				// url à analyser
	this.raw_links = [];		// liens trouvés sur cette page (non-normalizés)
	this.links = []; 			// liens trouvés sur cette page (normalizé)
	this.d_normalize = [];
}

Slave.prototype.start = function() {
	if (!this.running) {
		this.running = true;
		this.get_urls();
	}
}

Slave.prototype.stop = function() {
	this.running = false;
}


/**
 * Demander une url à explorer au serveur
 * @return {string} url
 */
Slave.prototype.get_urls = function() {
	var s = this;
	$.get(
		this.host + "get_urls",
		function (data) {
			//alert("hello" + data);
			t = data;
			s.set_url(data[0]);
			s.process();
		},
		"json"
	);
}

/**
 * Fixer l'url à visiter
 */
Slave.prototype.set_url = function(url) {
	this.url = url;
	this.parsed_url = parseUri(url);
}

/**
 * Récupérerle contenu de la page et l'analyser, pour ensuite renvoyer le résultat au serveur
 */
Slave.prototype.process = function() {
	var slave = this;
	$.get(this.url, function(data,textStatus,jqXHR) {
		slave.links = slave.get_links(data);
		slave.return_result(slave.url, slave.links);
	},
	"html");
}

/**
 * Récupérer les liens brut d'une page html
 * @param {string} html
 * @return {list(string)} une liste d'urls non-normalizées
 */
Slave.prototype.get_raw_links = function(html) {
	var raw_links = [];
	var jk = $(html);
	// [href]
	jk.find('[href]').each(
		function(index, value) {
			raw_links.push($(value).attr('href'));
		}
	);
	// [src]
	/*jk.find('[src]').each(
		function(index, value) {
			raw_links.push($(value).attr('src'));
		}
	);*/

	return raw_links;
}

/**
 * Récupérer les liens clean d'une page html (le liens relatifs sont remplacés
 * par des liens absolus
 * @param {string} html
 * @return {list(string)} une liste d'urls normalizées
 */
Slave.prototype.get_links = function(html) {
	raw_links = this.get_raw_links(html);
	var links = [];
	
	for (i in raw_links) {
		var link = raw_links[i];
		var normalize = this.normalize_link(link);
		if (normalize!="") {
			links.push(normalize);
		}
	}

	this.raw_links = raw_links;
	
	return links;
}

/**
 * Normaliser un lien
 * 	- lien rel -> lien abs
 * 	-> lien sans scheme -> scheme=http
 * @param {string} lien
 * @return {string} lien normalizée
 */
Slave.prototype.normalize_link = function(link) {
	var parse = parseUri(link.toLowerCase());
	var url_normalized = "";
	var base = this.parsed_url.protocol + "://" +
		this.parsed_url.authority;

	// url normale
	// http://www.bidon.com...
	if (parse.protocol=="http" || parse.protocol=="https") {
		url_normalized = parse.protocol + "://"
			+ parse.authority + parse.path;
	}
	else if (parse.protocol=="") {
		// /unDossier/unFichier
		if (parse.host=="") {
			url_normalized = base + parse.path;
		}
		// ./unDossier/unFichier
		else if (parse.host==".") {
			url_normalized = base + parse.path;
		}
		else if (parse.host==this.parsed_url.host) {
			// un.autre.host/hello.php
			if (s.indexOf('.') != -1) {
				url_normalized = "http://" + parse.authority + parse.path;
			}
			// un/lien/relatif
			else {
				url_normalized = base + parse.authority + parse.path;
			}
		}
	}
	
	this.d_normalize.push(url_normalized + " (" + link + ")");

	return url_normalized;
}



/**
 * Envoyer le résultat au serveur
 */
Slave.prototype.return_result = function(url, links) {
	var s = this;
	data = {
		url: url,
		links: links,
	};
	$.ajax({
		type: 'POST',
		url: this.host + "add_liens",
		data: JSON.stringify(data),
		success: function(data) {
			//alert("received return result");
			if (this.running) {
				s.get_urls();
			}
		},
		dataType: "json",
		processData: false,
	});
}


