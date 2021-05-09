install:
	pip install -r requirements.txt
	pip install -e .

update_csv:
	python mlopstools/main.py -u csv
