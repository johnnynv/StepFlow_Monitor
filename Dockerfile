# StepFlow Monitor - Production Ready Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY generate_complete_test_data.py .
COPY demo_script.py .

# Create necessary directories
RUN mkdir -p storage/database storage/executions storage/artifacts

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🚀 Starting StepFlow Monitor..."\n\
echo "📋 Current directory: $(pwd)"\n\
echo "📋 Files in app/: $(ls -la app/)"\n\
\n\
# Initialize database and generate test data if not exists\n\
if [ ! -f "storage/database/stepflow.db" ]; then\n\
    echo "📊 Database not found, generating test data..."\n\
    PYTHONPATH=. python generate_complete_test_data.py\n\
    echo "✅ Test data generated successfully"\n\
else\n\
    echo "✅ Database already exists, skipping test data generation"\n\
fi\n\
\n\
# Start the application\n\
echo "🎯 Starting StepFlow Monitor application..."\n\
exec PYTHONPATH=. python app/main.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 8080 8765

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Start the application
CMD ["/app/start.sh"]