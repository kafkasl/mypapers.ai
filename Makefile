run:
	docker-compose up --build
test:
	python -m pytest knowledge_base/test_find.py
freeze:
	pip freeze > requirements.txt
install:
	python -m venv venv
	pip install -r requirements.txt
deploy-site:
	rsync -avz --progress templates static mypapers-ai:/home/user/
deploy:
	rsync -avz --progress --exclude='papers' --exclude='*.pyc' --exclude='__pycache__/' --exclude='venv/' --exclude='*.env' . mypapers-ai:/home/user/app
restart:
	sudo docker compose down && sudo docker compose up --build -d
clean:
	rm -rf venv
