# 1. Base Image
FROM python:3.11-slim

# 2. System Setup
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Code
COPY . .

# 5. Set Environment Variables
ENV PYTHONPATH=/app
ENV API_URL="http://localhost:8000" 
# ^ This tells Streamlit to look for the API inside the container

# 6. Create Non-Root User
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# 7. THE DUAL LAUNCH COMMAND
# We use a shell script to launch Uvicorn (API) in the background (&) 
# and Streamlit (UI) in the foreground.
CMD uvicorn src.api.main:app --host 0.0.0.0 --port 8000 & \
    streamlit run streamlit_app/app.py --server.port 7860 --server.address 0.0.0.0
