run:
	docker-compose up --build
freeze:
	pip freeze > requirements.txt
install:
	python -m venv venv
	pip install -r requirements.txt
clean:
	rm -rf venv
