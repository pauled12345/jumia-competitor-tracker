.PHONY: install run test seed docker-build docker-run clean

install:
	pip install -r requirements.txt

run:
	python run.py

test:
	python test_scraper.py

seed:
	python seed_data.py

docker-build:
	docker build -t jumia-tracker .

docker-run:
	docker run -p 8000:8000 jumia-tracker

clean:
	rm -rf __pycache__ *.db *.log
