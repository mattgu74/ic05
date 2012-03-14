






/**
Extraire le json du body
*/
function extract_json_from_body() {
	match (HttpRequest.get_body()) {
	case {none}: {none}
	case {some: raw_body}: Json.deserialize(raw_body)
	}
}



function extract_url(json_record) {
	match (List.assoc("url", json_record)) {
		case {some: {String:url}}: {some:url};
		default: {none};
	}
}

function extract_page(json_record) {
	match (extract_url(json_record)) {
		case {none}: {none}
		case {some:url}:
			Page page = {url: url};
			{some: page};
	}
}

function extract_source(json_record) {
	match (List.assoc("source", json_record)) {
		case {some: {String:url}}: {some:url};
		default: {none};
	}
}

function extract_target(json_record) {
	match (List.assoc("target", json_record)) {
		case {some: {String:url}}: {some:url};
		default: {none};
	}
}

function extract_link(json_record) {
	source = extract_source(json_record);
	target = extract_target(json_record);
	match ((source,target)) {
		case ({some:source}, {some:target}):
			Link link = {~source, ~target};
			{some: link};
		default: {none}
	}
}


/**
Ajouter une page
*/
function add_page() {
	match (extract_json_from_body()) {
		case {none}: Resource.raw_status({bad_request});		// pas de body
		case {some:json}: 
			match (json) {
				case {Record:record}:
					match (extract_page(record)) {
						case {none}: Resource.raw_status({bad_request});	// mauvais formatage
						case {some:page}:
							Page.save(page);
							Resource.raw_status({success});
					}
				default: Resource.raw_status({bad_request});	// mauvais formatage du json
			}
	}
}


/**
Ajouter un lien
*/
function add_link() {
	match (extract_json_from_body()) {
		case {none}: Resource.raw_status({bad_request});		// pas de body
		case {some:json}: 
			match (json) {
				case {Record:record}:
					match (extract_link(record)) {
						case {none}: Resource.raw_status({bad_request});	// mauvais formatage
						case {some:link}:
							Link.save(link);
							Resource.raw_status({success});
					}
				default: Resource.raw_status({bad_request});	// mauvais formatage du json
			}
	}
}

function rest(path) {
	match (HttpRequest.get_method()) {
		case {some : {post}} :
			match (path) {
				case ["add_page" | _path]: add_page();
				case ["add_link" | _path]: add_link();
				default: Resource.raw_status({bad_request});
			}
		default:
			Resource.raw_status({bad_request});
	}
}


function start(url) {
	match (url) {
		case {path:[] ... }:
		Resource.styled_page("Hello", ["/resources/css.css"], <>Hello</>);
		case {path: ["_rest_" | path] ...}:
		rest(path)
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