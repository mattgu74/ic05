






/**
Extraire le json du body
*/
function extract_json_from_body() {
	match (HttpRequest.get_body()) {
	case {none}: {failure: "no body"};
	case {some: raw_body}: 
		match (Json.deserialize(raw_body)) {
		case {none}: {failure: "impossible de convertir en json"};
		case {some:jsast}: {success: OpaSerialize.Json.unserialize_unsorted(jsast)};
		}
	}
}



type Rest.Add.page = {
	string url,
}
function rest_page_transform(Rest.Add.page rest_page) {
	{url: rest_page.url};
}
/**
Ajouter une page
*/
function add_page() {
	match (extract_json_from_body()) {
	case {~failure}: 
		jlog("add_page : {failure}");
		Resource.raw_status({bad_request});
	case {success:opt}: 
		match (opt) {
		case {none}: 
			jlog("add_page : le json ne correspond pas");
			Resource.raw_status({bad_request});
		case {some: (Rest.Add.page record)}:
	    	//jlog("{record}");
			Page.save(rest_page_transform(record));
			Resource.raw_status({success});
		}
	}
}


type Rest.Add.link = {
	string source,
	string target,
}
function rest_link_transform(Rest.Add.link rest_link) {
	{source: rest_link.source, target: rest_link.target}
}
/**
Ajouter un lien
*/
function add_link() {
	match (extract_json_from_body()) {
	case {~failure}: 
		jlog("add_link : {failure}");
		Resource.raw_status({bad_request});
	case {success:opt}: 
		match (opt) {
		case {none}: 
			jlog("add_link : le json ne correspond pas");
			Resource.raw_status({bad_request});
		case {some: (Rest.Add.link record)}:
	    	//jlog("{record}");
			Link.save(rest_link_transform(record));
			Resource.raw_status({success});
		}
	}
}


type Rest.url = {
	string url
}
/**

*/
function url_need_a_visit() {
	match (extract_json_from_body()) {
	case {~failure}: 
		jlog("url_need_a_visit : {failure}");
		Resource.raw_status({bad_request});
	case {success:opt}:
		match (opt) {
		case {none}: 
			jlog("url_need_a_visit : le json ne correspond pas");
			Resource.raw_status({bad_request});
		case {some: (Rest.url record)}:
	    	//jlog("{record}");
			rep = Page.url_need_a_visit(record.url);
			Resource.raw_response(Json.serialize({Bool: rep}), "application/json", {success});
		}
	}
}

type Rest.Get.urls_to_visit = {
	int nb_max,
}
function get_urls_to_visit() {
	match (extract_json_from_body()) {
	case {~failure}: 
		jlog("get_urls_to_visit : {failure}");
		Resource.raw_status({bad_request});
	case {success:opt}:
		match (opt) {
		case {none}: 
			jlog("get_urls_to_visit : le json ne correspond pas");
			Resource.raw_status({bad_request});
		case {some: (Rest.Get.urls_to_visit record)}:
	    	//jlog("{record}");
			urls = Link.get_urls_to_visit(record.nb_max);
			Resource.raw_response(Json.serialize(OpaSerialize.Json.serialize(urls)), "application/json", {success});
		}
	}
}

function rest(path) {
	match (HttpRequest.get_method()) {
		case {some : {post}} :
			match (path) {
				case ["add_page" | _path]: add_page();
				case ["add_link" | _path]: add_link();
				case ["url_need_a_visit" | _path]: url_need_a_visit();
				case ["get_urls_to_visit" | _path]: get_urls_to_visit();
				default: Resource.raw_status({bad_request});
			}
		default:
			Resource.raw_status({bad_request});
	}
}

function home() {
	html_pages = Map.fold(function (k,v,a) {
		<>{a}<div>{k}<br/>{Page.to_string(v)}</div></>
	}, /mydb/pages, <></>)
	html_links = Map.fold(function (k,v,a) {
		<>{a}<div>{k}<br/>{Link.to_string(v)}</div></>
	}, /mydb/links, <></>)
	Resource.styled_page("Home", ["/resources/css.css"], html_pages <+> html_links);
}

function start(url) {
	match (url) {
		case {path:[] ... }: home();
		case {path: ["_rest_" | path] ...}: rest(path)
		case  {~path ...} :
		path = String.concat("/", path);
		Resource.styled_page("404", ["/resources/css.css"], <><h1>404</h1><div>{path} doesn't exist</div></>);
	}
}


Server.start(
	Server.http,
	[ {resources: @static_include_directory("resources")}
	  /** Launch the [start] dispatcher */
	  , {dispatch: start}
	]
);