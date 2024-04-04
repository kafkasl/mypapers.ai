run:
	docker-compose up --build
test:
	python -m pytest knowledge_base/test_find.py
freeze:
	pip freeze > requirements.txt
install:
	python -m venv venv
	pip install -r requirements.txt
clean:
	rm -rf venv
