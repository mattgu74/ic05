






function page_export() {
	html = <h1>Export gephi</h1>
	<div id=#forumlaire>
		<input id=#gephi_host value="localhost"/>
		<input id=#gephi_port value="8081"/>
		<button onclick={onclick_send}>Send</button>
	</div>
	<div id=#exports />
	Resource.styled_page("Export Gephi", ["/resources/css.css"], html);
}

function onclick_send(_e) {
	match (Parser.int(Dom.get_content(#gephi_port))) {
		case {none}: jlog("le port doit être une valeur entière");
		case {some:port}:
			host = Dom.get_content(#gephi_host);
			#exports = gephi_loader(host, port);
			do_export(host, port)
	}
}

@async function do_export(host, port) {
	str_url = "http://{host}:{port}/workspace0?operation=updateGraph"
	match (Uri.of_string(str_url)) {
		case {none}: jlog("impossible de créer une url à partir de {host} et {port}");
		case {some: uri}:
			//export_pages(host, port, uri);
			export_links(host, port, uri);
	}
}


function onresult_post(string id)(e) {
	match (e) {
		case {~failure}: #{id} =+ <>ECHEC: {"{failure}"}<br /></>;
		case {~success}: void // #{id} =+ <>SUCCES: {"{success.content}"}<br /></>;
	}
}

@async function export_pages(host,port,uri) {
	count = Map.fold(function (_k,page,acc) {
		js = page_to_js(page);
		envoyer(uri, js, onresult_post(id_loader_pages(host,port)));
		acc + 1;
	}, /mydb/pages, 0);
	#{id_loader_pages(host,port)} =+ <>{count} pages transférées<br /></>;
}

@async function export_links(host,port,uri) {
	count = List.fold(function (link,acc) {
		js = link_to_js(link);
		envoyer(uri, js, onresult_post(id_loader_links(host,port)));
		acc + 1;
	}, Map.To.val_list(/mydb/links), 0);
	#{id_loader_links(host,port)} =+ <>{count} liens transférés<br /></>;
}

function page_to_js(Page page) {
	"\{ 'an': \{ '{page.url}': \{ 'label': '{page.url}' \} \} \}";
}

function link_to_js(Link link) {
	js_link = "\{'ae': \{ '{Link.get_ref(link)}': \{'source':'{link.source}', 'target': '{link.target}' \} \} \}";
	js_source = "\{ 'an': \{ '{link.source}': \{ 'label': '{link.source}' \} \} \}";
	js_target = "\{ 'an': \{ '{link.target}': \{ 'label': '{link.target}' \} \} \}";
	"{js_link}\n\r{js_target}\n\r{js_source}";
}


function envoyer(Uri.uri uri, string data, onresult) {
	//jlog("envoyer {uri} data={data}")
	WebClient.Post.try_post_async(uri, data, onresult);
}

function id_loader(host, port) {"{host}{port}";}
function id_loader_pages(host,port) { "{id_loader(host,port)}_pages"; }
function id_loader_links(host,port) { "{id_loader(host,port)}_links"; }
function gephi_loader(host, port) {
	<div>
		Export to : {host}:{port}
		<div id=#{id_loader_pages(host,port)}></div>
		<div id=#{id_loader_links(host,port)}></div>
	</div>
}
