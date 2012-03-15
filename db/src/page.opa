


module Page {
	function to_string(Page page) {
		OpaSerialize.serialize(page);
	}

	function url_to_ref(string url) {
		url;
	}

	/**
	Récupérer la référence d'une page
	*/
	function get_ref(Page page) {
		page.url;
	}

	/**
	Sauvegarder une page
	*/
	function save(Page page) {
		jlog("save page {page}");
		ref = get_ref(page);
		/mydb/pages[ref] <- page;
	}

	function url_need_a_visit(string url) {
		ref = url_to_ref(url);
		not(Db.exists(@/mydb/pages[ref]));
	}
}


