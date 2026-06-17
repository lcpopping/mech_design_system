"""Flask application factory."""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__,
                template_folder='../frontend',
                static_folder='../frontend')

    from backend.config import get_config
    app.config.from_object(get_config())

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # Register blueprints
    from backend.routes.standard_parts import standard_parts_bp
    app.register_blueprint(standard_parts_bp, url_prefix='/api/standard-parts')

    @app.route('/api/health')
    def health():
        return {'status': 'healthy', 'service': 'mech-design-system'}

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)
