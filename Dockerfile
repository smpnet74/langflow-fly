FROM langflowai/langflow:latest

WORKDIR /app

# Install requests for proxying
RUN pip install requests

COPY wrapper.py .

ENV HOST=0.0.0.0
ENV PORT=8080
ENV LANGFLOW_DATABASE_URL="sqlite:////data/langflow.db"
ENV TIMEOUT_MINUTES=5

EXPOSE 8080

CMD ["python", "wrapper.py"]
