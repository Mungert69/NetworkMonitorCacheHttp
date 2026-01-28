# NetworkMonitorCacheHttp Build Instructions

This directory contains a build script for the NetworkMonitorCacheHttp that follows the same pattern as the NetworkMonitorService build script.

## Build Script Usage

### Basic Usage
```bash
./build-run
```

### With Configuration
```bash
# Set environment variables
export CONTAINER_TAG=1.0.1
export CONTAINER_REPO=myrepo/networkmonitorcachehttp

# Run build
./build-run
```

### Test Container (Optional)
```bash
TEST_CONTAINER=true ./build-run
```

## Configuration

### Container Configuration File
The `container-config.env` file defines default container settings:

```bash
# Container Image Tag
CONTAINER_TAG=1.0.0

# Container Repository
CONTAINER_REPO=mungert/networkmonitorcachehttp

# Container Name
CONTAINER_NAME=networkmonitorcachehttp

# Default API Key (can be overridden by domain-env)
DEFAULT_API_KEY=change-me-in-production

# Default Port
DEFAULT_PORT=5000

# Cache Directory
CACHE_DIR=./cache_files

# Max File Size (in bytes)
MAX_FILE_SIZE=524288000

# Log Level
LOG_LEVEL=INFO
```

### Environment Variables
You can override any configuration by setting environment variables:

- `CONTAINER_TAG` - Image tag (overrides config file)
- `CONTAINER_REPO` - Image repository (overrides config file)
- `TEST_CONTAINER` - Enable container testing (true/false)

## Build Process

The build script:

1. **Loads configuration** from `container-config.env` if it exists
2. **Validates required files** (Dockerfile, requirements.txt, app.py)
3. **Builds Docker image** with both tag and latest
4. **Optionally tests container** if `TEST_CONTAINER=true`
5. **Provides usage instructions** for running the container

## Running the Container

### Direct Docker Run
```bash
docker run -p 5000:5000 \
  -e API_KEY=your-secure-api-key \
  -v ./cache_files:/app/cache_files \
  mungert/networkmonitorcachehttp:1.0.0
```

### Docker Compose
```bash
docker-compose -f docker-compose-run-cachehttp-dev.yml up -d
```

## Security Notes

- **API Key**: Always use a strong, unique API key in production
- **Environment Variables**: Store sensitive configuration in `.env` files
- **File Permissions**: The container runs as non-root user `cacheuser`
- **Volume Mounts**: Ensure proper permissions on cache directory

## Integration with NetworkMonitorLLM

Configure NetworkMonitorLLM to use this cache server:

```json
{
  "RemoteCache": {
    "Enabled": true,
    "Type": "Http",
    "BaseUrl": "http://localhost:5000/api",
    "ApiKey": "your-secure-api-key-here"
  }
}
```

## Troubleshooting

### Build Failures
- Ensure Docker is running
- Check that all required files exist
- Verify Docker has sufficient resources

### Container Issues
- Check logs: `docker logs <container-id>`
- Verify API key is set correctly
- Ensure cache directory has proper permissions

### Network Issues
- Verify port 5000 is available
- Check firewall settings
- Ensure proper CORS configuration