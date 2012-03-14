


module Page {
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
}


