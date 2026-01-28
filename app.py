#!/usr/bin/env python3
"""
Flask Cache Server for NetworkMonitorLLM

A simple HTTP cache server that stores and serves LLM context files.
Provides endpoints for checking file existence, uploading files, and downloading files.
"""

import os
import hashlib
import logging
from datetime import datetime
from flask import Flask, request, send_file, jsonify, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config.from_object(config)

# Ensure cache directory exists
os.makedirs(app.config['CACHE_DIR'], exist_ok=True)

def validate_api_key():
    """Validate API key from request headers."""
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != app.config['API_KEY']:
        logger.warning(f"Invalid API key attempt: {api_key}")
        abort(401, description="Invalid API key")

def get_file_path(filename, file_hash):
    """Get the full path for a cached file."""
    # Sanitize filename to prevent directory traversal
    safe_filename = secure_filename(filename)
    return os.path.join(app.config['CACHE_DIR'], f"{safe_filename}.{file_hash}")

@app.before_request
def before_request():
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'cache_dir': app.config['CACHE_DIR'],
        'files_count': len(os.listdir(app.config['CACHE_DIR']))
    })

@app.route('/api/cache/<filename>/<file_hash>', methods=['GET'])
def check_file(filename, file_hash):
    """
    Check if a file exists in the cache.
    
    Args:
        filename (str): The filename
        file_hash (str): The SHA256 hash of the file content
    
    Returns:
        JSON response with 'exists' boolean field
    """
    validate_api_key()
    
    try:
        file_path = get_file_path(filename, file_hash)
        exists = os.path.exists(file_path)
        
        logger.info(f"File check: {filename}.{file_hash} - {'exists' if exists else 'not found'}")
        
        return jsonify({
            'filename': filename,
            'hash': file_hash,
            'exists': exists
        })
    except Exception as e:
        logger.error(f"Error checking file {filename}.{file_hash}: {str(e)}")
        abort(500, description="Internal server error")

@app.route('/api/cache/<filename>/<file_hash>', methods=['POST'])
def upload_file(filename, file_hash):
    """
    Upload a file to the cache.
    
    Args:
        filename (str): The filename
        file_hash (str): The SHA256 hash of the file content
    
    Returns:
        JSON response with upload status
    """
    validate_api_key()
    
    try:
        if 'file' not in request.files:
            logger.warning(f"No file provided for upload: {filename}.{file_hash}")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning(f"Empty filename for upload: {filename}.{file_hash}")
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file hash if provided in form data
        provided_hash = request.form.get('hash')
        if provided_hash and provided_hash != file_hash:
            logger.warning(f"Hash mismatch for {filename}: provided={provided_hash}, expected={file_hash}")
            return jsonify({'error': 'Hash mismatch'}), 400
        
        # Generate hash from uploaded file content
        file_content = file.read()
        calculated_hash = hashlib.sha256(file_content).hexdigest()
        
        if calculated_hash != file_hash:
            logger.warning(f"Hash mismatch for {filename}: calculated={calculated_hash}, expected={file_hash}")
            return jsonify({'error': 'Hash mismatch'}), 400
        
        # Save file
        file_path = get_file_path(filename, file_hash)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        file_size = len(file_content)
        logger.info(f"Successfully uploaded: {filename}.{file_hash} ({file_size} bytes)")
        
        return jsonify({
            'filename': filename,
            'hash': file_hash,
            'size': file_size,
            'success': True
        })
        
    except RequestEntityTooLarge:
        logger.warning(f"File too large for upload: {filename}.{file_hash}")
        return jsonify({'error': 'File too large'}), 413
    except Exception as e:
        logger.error(f"Error uploading file {filename}.{file_hash}: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/api/cache/<filename>/<file_hash>/download', methods=['GET'])
def download_file(filename, file_hash):
    """
    Download a file from the cache.
    
    Args:
        filename (str): The filename
        file_hash (str): The SHA256 hash of the file content
    
    Returns:
        File download response
    """
    validate_api_key()
    
    try:
        file_path = get_file_path(filename, file_hash)
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found for download: {filename}.{file_hash}")
            return jsonify({'error': 'File not found'}), 404
        
        file_size = os.path.getsize(file_path)
        logger.info(f"Downloading file: {filename}.{file_hash} ({file_size} bytes)")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{filename}.{file_hash}"
        )
        
    except Exception as e:
        logger.error(f"Error downloading file {filename}.{file_hash}: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/api/cache/files', methods=['GET'])
def list_files():
    """List all cached files."""
    validate_api_key()
    
    try:
        files = []
        for filename in os.listdir(app.config['CACHE_DIR']):
            file_path = os.path.join(app.config['CACHE_DIR'], filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        logger.info(f"Listed {len(files)} cached files")
        return jsonify({'files': files, 'count': len(files)})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': 'Failed to list files'}), 500

@app.route('/api/cache/<filename>/<file_hash>', methods=['DELETE'])
def delete_file(filename, file_hash):
    """Delete a file from the cache."""
    validate_api_key()
    
    try:
        file_path = get_file_path(filename, file_hash)
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found for deletion: {filename}.{file_hash}")
            return jsonify({'error': 'File not found'}), 404
        
        os.remove(file_path)
        logger.info(f"Deleted file: {filename}.{file_hash}")
        
        return jsonify({
            'filename': filename,
            'hash': file_hash,
            'deleted': True
        })
        
    except Exception as e:
        logger.error(f"Error deleting file {filename}.{file_hash}: {str(e)}")
        return jsonify({'error': 'Delete failed'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 errors."""
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Flask Cache Server on port {app.config['PORT']}")
    logger.info(f"Cache directory: {app.config['CACHE_DIR']}")
    logger.info(f"API Key: {app.config['API_KEY'][:4]}***")
    
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )