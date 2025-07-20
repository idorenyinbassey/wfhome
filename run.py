import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Get host from environment variable or default to localhost
    host = os.environ.get('HOST', '127.0.0.1')
    
    # Determine if we're in production
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )