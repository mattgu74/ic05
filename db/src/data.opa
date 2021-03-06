



abstract type Page.ref = string
abstract type Page = {
	string url,
	list(Page.ref) links
}

type Link.ref = string
type Link = {
	Page.ref source,
	Page.ref target
}

database mydb {
	map(Page.ref, Page) /pages
	map(Link.ref, Link) /links
}


