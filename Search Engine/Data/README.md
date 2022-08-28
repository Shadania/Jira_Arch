# Restoring the database from the backup file (first time running)

- Have pgAdmin installed
- Create an empty database named 'archedetector'
- Right-click the database and click 'restore'.
- For filename, pick a folder and select the file in it. The options should be as follows:
	+ Format: custom or tar
	+ Role name: postgres
- From that same folder, put the `index` folder in the correct location in the Search Engine Backend program in order to avoid having to regenerate indices or not having the correct indices when using the search engine.

Please note that the database backup file might be too big in some versions to be able to go on Github, which is why in those cases a .zip has been added instead. Please unzip these files before using them.