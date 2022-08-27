import os.path

def getFileName(file_name):
	dir_base = os.path.dirname(__file__)
	return os.path.join(dir_base, file_name)