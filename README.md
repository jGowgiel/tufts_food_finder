# Tufts Food Finder

Written in Python using the Flask framework, this site gives visitors a chance to see what foods at the Tufts dining halls will be available in the next week.

Thanks to the work of Derick Yang on a [scraper for the Tufts dining menus](https://github.com/dyang108/diningdata), this app mostly contains front-end code alongside the search functions that use the API provided by this service.

Future versions will include a proper database to store menu information and reduce load times, instead of using Memcached (which is admittedly a bit of a hack).