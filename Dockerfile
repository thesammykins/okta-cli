FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 oktauser && \
    chown -R oktauser:oktauser /app

# Switch to non-root user
USER oktauser

# Create config directory
RUN mkdir -p /home/oktauser/.okta-cli

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/home/oktauser/.local/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD okta-cli --help || exit 1

# Default command
ENTRYPOINT ["okta-cli"]
CMD ["--help"]