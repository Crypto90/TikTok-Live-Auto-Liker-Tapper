FROM python:3.11-slim

# Install system libraries required for PyQt6, QtWebEngine, and Xvfb virtual display
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrender1 \
    libxrandr2 \
    libxtst6 \
    libxi6 \
    libasound2 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libegl1-mesa \
    libfontconfig1 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose web dashboard port
EXPOSE 8080

# Run with virtual display via xvfb-run
CMD ["xvfb-run", "-a", "python3", "headless_runner.py", "--port", "8080"]
