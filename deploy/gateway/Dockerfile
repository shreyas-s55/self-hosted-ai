FROM python:3.12-slim

WORKDIR /app

# Copy the tools library: gateway, models, runtime packages.
# Build context is the project root (set in compose.generated.yaml).
COPY tools/lib/ ./lib/

COPY deploy/gateway/requirements.txt ./requirements.txt
COPY deploy/gateway/main.py ./main.py

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
