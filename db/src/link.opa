




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

	function get_urls_to_visit(int max) {
		r_fold = Map.fold(function (_k,link,acc) {
			if (acc.counter <= max && not(Db.exists(@/mydb/pages[link.target]))) {
				{counter: acc.counter+1, result: List.add(link.target, acc.result)};
			} else {
				acc;
			}
		}, /mydb/links, {counter: 0, result: []});
		r_fold.result;
	}
}

