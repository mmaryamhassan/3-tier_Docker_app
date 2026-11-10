# STEP 1: Builder
FROM python:3.11-slim-bookworm AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt


# STEP 2: Runtime
FROM python:3.11-slim-bookworm AS runtime
WORKDIR /app
# bring the installed packages over
# COPY --from=builder:/root/.local /root/.local   
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY requirements.txt .
COPY app.py .
# container is Exposing the application localhost:5000 port
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
