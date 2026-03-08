FROM python:3.11.15

# set working directory in container
WORKDIR /usr/src/app

# copy the rest of the application
COPY . .

# install system dependencies
# RUN apt-get update && apt-get install -y \
#     libopencv-dev \
#     python3-opencv \
#     && rm -rf /var/lib/apt/lists/*

# copy requirements first for better caching
# COPY requirements.txt .

# install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# expose port
EXPOSE 5000

# create uploads directory
RUN mkdir -p uploads

# # set environment variables
# ENV FLASK_APP=app.py
# ENV FLASK_ENV=production
# ENV PYTHONUNBUFFERED=1

# health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')"

# run the application
CMD ["python", "app.py"]