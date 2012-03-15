




module Link {
	function to_string(Link link) {
		OpaSerialize.serialize(link);
	}
	/**
	Récupérer la référence d'un lien
	*/
	function get_ref(Link link) {
		jlog("save link {link}");
		"{link.source}_to_{link.target}";
	}

	/**
	Sauvegarder un lien
	*/
	function save(Link link) {
		ref = get_ref(link);
		/mydb/links[ref] <- link;
	}
}

