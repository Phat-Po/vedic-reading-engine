FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY templates ./templates
COPY ephe ./ephe
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "vedic_engine.api:app", "--host", "0.0.0.0", "--port", "8000"]

