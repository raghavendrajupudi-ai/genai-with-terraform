# Docker Deployment Guide

## Prerequisites
- Docker installed on your system
- Docker Compose (optional, but recommended)
- Google API key for Gemini

## Building and Running with Docker

### Option 1: Using Docker Compose (Recommended)

1. **Create a `.env` file** in the project root with your API key:
   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

2. **Build and start the container**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   Open your browser and navigate to: `http://localhost:8501`

4. **View logs**:
   ```bash
   docker-compose logs -f
   ```

5. **Stop the application**:
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker CLI

1. **Build the Docker image**:
   ```bash
   docker build -t genai-terraform-app .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name genai-terraform \
     -p 8501:8501 \
     -e GOOGLE_API_KEY=your_api_key_here \
     -v $(pwd)/terraform_files:/app/terraform_files:ro \
     genai-terraform-app
   ```

3. **Access the application**:
   Open your browser and navigate to: `http://localhost:8501`

4. **View logs**:
   ```bash
   docker logs -f genai-terraform
   ```

5. **Stop the container**:
   ```bash
   docker stop genai-terraform
   docker rm genai-terraform
   ```

## Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google Gemini API key (required)

### Ports
- Default port: `8501` (Streamlit default)
- You can change the port mapping: `-p 8080:8501` to access via port 8080

### Volumes
- `./terraform_files:/app/terraform_files:ro` - Mounts your Terraform files as read-only

## Production Deployment

For production, consider:

1. **Use secrets management** instead of environment variables:
   ```bash
   docker secret create google_api_key api_key.txt
   ```

2. **Add resource limits**:
   ```yaml
   services:
     streamlit-app:
       # ... other config
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
           reservations:
             cpus: '1'
             memory: 1G
   ```

3. **Use a reverse proxy** (nginx/traefik) for HTTPS

4. **Set up proper logging**:
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

## Troubleshooting

### Container fails to start
```bash
docker logs genai-terraform
```

### Application not accessible
- Check if port 8501 is already in use
- Verify firewall settings
- Check container status: `docker ps -a`

### API key issues
- Ensure the API key is correctly set in `.env` file
- Verify no extra spaces or quotes in the key

## Updates

To update the application:

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```
