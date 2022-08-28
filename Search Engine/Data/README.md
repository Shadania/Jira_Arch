# Restoring the database from the backup file (first time running)

- Have pgAdmin installed
- Create an empty database named 'archedetector'
- Right-click the database and click 'restore'.
- For filename, pick a folder and select the file in it. The options should be as follows:
	+ Format: custom or tar
	+ Role name: postgres
- From that same folder, put the `index` folder in the correct location in the Search Engine Backend program in order to avoid having to regenerate indices or not having the correct indices when using the search engine.