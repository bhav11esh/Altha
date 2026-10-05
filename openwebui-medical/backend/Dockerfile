FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=sqlite:///./medical_ai.db
ENV SECRET_KEY=your-secret-key-change-in-production

EXPOSE 8000

CMD ["python", "app.py"]
