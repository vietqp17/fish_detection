# Docker Setup Guide

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.29+)
- Optional: [nvidia-docker](https://github.com/NVIDIA/nvidia-docker) for GPU support

## Quick Start

### Using Docker Compose (Recommended)

1. Build and run the container:

```bash
docker-compose up --build
```

2. Open your browser to:

```
http://localhost:5000
```

3. Stop the container:

```bash
docker-compose down
```

### Using Docker Directly

1. Build the Docker image:

```bash
docker build -t fish-vision:latest .
```

2. Run the container:

```bash
# Basic usage
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads fish-vision:latest

# With data directory mounting
docker run -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/data:/app/data \
  fish-vision:latest
```

3. Access the app at:

```
http://localhost:5000
```

4. Stop the container:

```bash
docker stop <container_id>
```

## GPU Support

If you have an NVIDIA GPU and want to use it:

1. Install [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)

2. Uncomment the GPU section in `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

3. Run with docker-compose:

```bash
docker-compose up --build
```

Or with Docker directly:

```bash
docker run --gpus all -p 5000:5000 -v $(pwd)/uploads:/app/uploads fish-vision:latest
```

## File Structure

```
fish_vision/
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Compose orchestration
├── .dockerignore           # Files to exclude from build
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── uploads/                # (Auto-created) Mounted volume for results
└── data/                   # (Mounted) Training data directory
```

## Configuration

### Environment Variables

You can set environment variables in `docker-compose.yml`:

```yaml
environment:
  - FLASK_ENV=production # production, development
  - FLASK_DEBUG=0 # 0 or 1
  - PYTHONUNBUFFERED=1 # For real-time logs
```

### Volumes

The compose file mounts these directories:

- `./uploads:/app/uploads` - Persistent storage for uploaded images and results
- `./data:/app/data` - Training data directory

### Ports

By default, the app runs on port 5000. To change it:

```yaml
ports:
  - "8080:5000" # Expose on port 8080 instead
```

Then access at `http://localhost:8080`

## Docker Commands

### Build the image

```bash
docker build -t fish-vision:latest .
```

### List images

```bash
docker images | grep fish-vision
```

### Remove image

```bash
docker rmi fish-vision:latest
```

### View logs

```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs -f <container_id>
```

### Inspect running container

```bash
docker ps
docker inspect <container_id>
```

### Execute command in running container

```bash
docker exec -it <container_id> bash
```

## Troubleshooting

### Issue: "Cannot connect to localhost:5000"

**Solution:**

- Check if container is running: `docker ps`
- Check logs: `docker-compose logs`
- Ensure port isn't already in use: `lsof -i :5000`

### Issue: "CUDA out of memory" or GPU not detected

**Solution:**

- Check GPU: `docker run --gpus all nvidia/cuda:11.8.0-runtime-ubuntu22.04 nvidia-smi`
- Ensure nvidia-docker is installed
- Check docker-compose.yml GPU configuration

### Issue: "Module not found" errors

**Solution:**

- Rebuild the image: `docker-compose build --no-cache`
- Check Dockerfile dependencies

### Issue: Uploaded files don't persist after container stops

**Solution:**

- Ensure volumes are properly mounted in docker-compose.yml
- Check volume permissions: `ls -la uploads/`

## Performance Tips

1. **Layer Caching**: Keep frequently changing files (like app.py) after dependencies in Dockerfile
2. **Multi-stage builds**: For production, consider using multi-stage builds to reduce image size
3. **Resource limits**: Set memory and CPU limits in docker-compose.yml if needed

## Production Considerations

For production deployment:

1. Change `FLASK_ENV` to `production`
2. Use a production WSGI server like Gunicorn:

```dockerfile
RUN pip install gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

3. Set up reverse proxy (nginx/Apache)
4. Use environment variables for sensitive data
5. Set up volume backups for uploaded files
6. Monitor container health with health checks

## Deployment Examples

### Google Cloud Run

See `.github/workflows/deploy-gcp.yml` for CI/CD setup

### AWS ECS

Configure task definition with proper port mappings and environment variables

### DigitalOcean App Platform

Simple Docker-based deployment with automatic scaling

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
