import os
from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# AAF OIDC Configuration (Supports environment variables or fallback test configs)
app.config['AAF_CLIENT_ID'] = os.getenv('AAF_CLIENT_ID', 'test-client-id')
app.config['AAF_CLIENT_SECRET'] = os.getenv('AAF_CLIENT_SECRET', 'test-client-secret')
app.config['AAF_SERVER_METADATA_URL'] = os.getenv(
    'AAF_SERVER_METADATA_URL',
    'https://rapid.aaf.edu.au/.well-known/openid-configuration'
)

db = SQLAlchemy(app)
jwt = JWTManager(app)
oauth = OAuth(app)

# Register AAF OIDC remote app
oauth.register(
    name='aaf',
    client_id=app.config['AAF_CLIENT_ID'],
    client_secret=app.config['AAF_CLIENT_SECRET'],
    server_metadata_url=app.config['AAF_SERVER_METADATA_URL'],
    client_kwargs={'scope': 'openid profile email'}
)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(50), nullable=False, default='VIEWER')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role
        }


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html') if os.path.exists('templates/index.html') else '<h1>Welcome</h1><a href="/login">Login with AAF</a>'


@app.route('/login')
def login():
    redirect_uri = url_for('auth_callback', _external=True)
    return oauth.aaf.authorize_redirect(redirect_uri)


@app.route('/auth/callback')
def auth_callback():
    try:
        token = oauth.aaf.authorize_access_token()
    except Exception as e:
        return jsonify({'error': 'Authentication failed', 'details': str(e)}), 400

    user_info = token.get('user_info')
    if not user_info:
        try:
            user_info = oauth.aaf.parse_id_token(token)
        except Exception:
            user_info = {}

    email = user_info.get('email') or user_info.get('sub')
    name = user_info.get('name') or user_info.get('preferred_username', 'User')

    if not email:
        return jsonify({'error': 'Email not provided by OIDC provider'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name, role='VIEWER')
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=user.email)
    
    # Redirect to dashboard with token or set cookie / query param
    resp = redirect(url_for('dashboard', token=access_token))
    return resp


@app.route('/dashboard')
def dashboard():
    token = request.args.get('token')
    return render_template('dashboard.html', token=token) if os.path.exists('templates/dashboard.html') else jsonify({'message': 'Welcome to Dashboard', 'token': token})


@app.route('/api/me')
@jwt_required()
def api_me():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())


if __name__ == '__main__':
    app.run(debug=True)
