prod:
	@echo "Staring Up Production Server"
	gunicorn wsgi:app -b 0.0.0.0 --workers=2 --access-logfile gunicorn_access.log --error-logfile gunicorn_error.log

dev:
	@echo "Staring Up Dev Server"
	flask run -p 8000

test:
	@echo "Running Tests"
	source .env && pytest -vs
