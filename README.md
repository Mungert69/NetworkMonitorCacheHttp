# Flask Cache Server for NetworkMonitorLLM

A simple HTTP cache server designed to store and serve LLM context files for the NetworkMonitorLLM project. This server provides RESTful endpoints for checking file existence, uploading files, and downloading files with proper authentication and security measures.

## 🚀 Features

- **File Existence Check**: Check if a file exists in the cache by filename and hash
- **File Upload**: Upload files to the cache with hash validation
- **File Download**: Download files from the cache by filename and hash
- **Authentication**: API key-based authentication for all endpoints
- **Security**: File path sanitization and size limits
- **Logging**: Comprehensive request/response logging
- **Health Check**: Health endpoint for monitoring
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **CORS Support**: Cross-origin resource sharing support

## 📋 Requirements

- Python 3.8+
- pip

## 🛠️ Installation

### Option 1: Local Installation

1. **Clone or navigate to the flask directory:**
   ```bash
   cd ~/code/flask
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export API_KEY="your-secure-api-key-here"
   export FLASK_ENV="development"
   ```

4. **Run the server:**
   ```bash
   python app.py
   ```

### Option 2: Docker Installation

1. **Build and run with Docker Compose:**
   ```bash
   cd ~/code/flask
   docker-compose up -d
   ```

2. **Or build manually:**
   ```bash
   docker build -t flask-cache-server .
   docker run -p 5000:5000 -e API_KEY="your-secure-api-key-here" flask-cache-server
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_PORT` | 5000 | Server port |
| `FLASK_DEBUG` | False | Enable debug mode |
| `API_KEY` | default-api-key-change-in-production | API key for authentication |
| `CACHE_DIR` | ./cache_files | Directory to store cached files |
| `MAX_FILE_SIZE` | 524288000 (500MB) | Maximum file size in bytes |
| `LOG_LEVEL` | INFO | Logging level |
| `CORS_ORIGINS` | * | Allowed CORS origins |

### Configuration File

The server uses `config.py` for configuration management. You can modify the configuration classes for different environments (development, production, testing).

## 🌐 API Endpoints

### Health Check
```http
GET /health
```
Returns server health status and cache statistics.

### Check File Existence
```http
HEAD /api/cache/{filename}/{hash}
Headers: X-API-Key: your-api-key
```
Returns `200` if the file exists, `404` if it does not.

### Upload File
```http
POST /api/cache/{filename}/{hash}
Headers: X-API-Key: your-api-key
Body: multipart/form-data with 'file' field
```
Uploads a file to the cache with hash validation. Files are stored under `<CACHE_DIR>/<filename>/<hash>`.

**Response:**
```json
{
  "hash": "sha256-hash",
  "size": 1024000,
  "success": true
}
```

### Download File
```http
GET /api/cache/{filename}/{hash}/download
Headers: X-API-Key: your-api-key
```
Downloads a file from the cache.

**Response:** File download (binary)

### List Files
```http
GET /api/cache/files
Headers: X-API-Key: your-api-key
```
Lists all cached files with metadata.

**Response:**
```json
{
  "files": [
    {
      "filename": "context-qwen-3.gguf",
      "hash": "sha256-hash",
      "size": 1024000,
      "modified": "2023-01-01T12:00:00"
    }
  ],
  "count": 1
}
```

### Delete File
```http
DELETE /api/cache/{filename}/{hash}
Headers: X-API-Key: your-api-key
```
Deletes a file from the cache.

**Response:**
```json
{
  "filename": "context-file",
  "hash": "sha256-hash",
  "deleted": true
}
```

## 🔐 Authentication

All endpoints (except `/health`) require an API key in the `X-API-Key` header:

```http
X-API-Key: your-secure-api-key-here
```

## 🐳 Docker Deployment

### Basic Docker Compose
```bash
docker-compose up -d
```

### Production with Nginx
```bash
docker-compose --profile production up -d
```

### Environment Variables in Docker
Create a `.env` file:
```bash
API_KEY=your-secure-api-key-here
FLASK_ENV=production
CACHE_DIR=/app/cache_files
```

## 🔗 Integration with NetworkMonitorLLM

Configure NetworkMonitorLLM to use this cache server by updating the `appsettings.json`:

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

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:5000/health
```

### View Logs
```bash
# Docker
docker-compose logs flask-cache-server

# Local
# Check console output or configure logging in config.py
```

## 🔒 Security Considerations

1. **Always use a strong API key** in production
2. **Enable HTTPS** for production deployments
3. **Set appropriate file size limits** based on your needs
4. **Monitor disk usage** of the cache directory
5. **Use Docker secrets** for sensitive configuration in production

## 🚨 Error Handling

The server returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (missing file, invalid data)
- `401`: Unauthorized (invalid API key)
- `404`: Not found (file not found)
- `413`: Payload too large
- `500`: Internal server error

## 🧪 Testing

### Manual Testing with curl

1. **Check health:**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Check file existence:**
   ```bash
   curl -I -H "X-API-Key: your-api-key" \
        http://localhost:5000/api/cache/test-file/abc123
   ```

3. **Upload a file:**
   ```bash
   curl -X POST \
        -H "X-API-Key: your-api-key" \
        -F "file=@/path/to/file" \
        -F "hash=abc123" \
        http://localhost:5000/api/cache/test-file/abc123
   ```

4. **Download a file:**
   ```bash
   curl -H "X-API-Key: your-api-key" \
        http://localhost:5000/api/cache/test-file/abc123/download \
        -o downloaded-file
   ```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

1. **Permission denied on cache directory:**
   ```bash
   chmod 755 cache_files
   ```

2. **Port already in use:**
   ```bash
   # Change port in config.py or environment variable
   export FLASK_PORT=5001
   ```

3. **Docker volume permissions:**
   ```bash
   # Ensure cache_files directory exists and has proper permissions
   mkdir -p cache_files
   chmod 755 cache_files
   ```

4. **API key authentication failing:**
   - Check that the API key matches between client and server
   - Verify the header is correctly formatted: `X-API-Key: your-key`

### Getting Help

- Check the server logs for detailed error messages
- Verify network connectivity between client and server
- Ensure the API key is correctly configured on both sides
