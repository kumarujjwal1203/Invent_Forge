.PHONY: prisma dev test

prisma:
	prisma db push

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	pytest
