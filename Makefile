prod:
	@echo "Staring Up Production Server"
	gunicorn wsgi:app -b 0.0.0.0:5000 --workers=2 --access-logfile -

dev:
	@echo "Staring Up Dev Server"
	flask run

test:
	@echo "Running Tests"
	source .env && pytest -vs
