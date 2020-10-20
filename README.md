## Cumulus: Meteorologic Data Repository and Processing Engine

### Adding New Data Products

1. Add "acquirables" to the database. An Acquirable is nothing more than an organized name for something that will be
   downloaded and a cron-style schedule of when the downloads should take place.  Here's an example of how one might
   add three "acquirables" to the database:

   ```
   INSERT INTO acquirable (name, schedule) VALUES
	('prism_ppt_early',  '55 06-10 * * *'),
	('prism_tmax_early', '55 06-10 * * *'),
	('prism_tmin_early', '55 07-10 * * *');
    ```
