"""Authentication routes."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import jsonify
        
        # Check if this is an API request (expects JSON)
        is_api_request = request.path.startswith('/api/') or request.headers.get('Content-Type') == 'application/json'
        
        if 'session_id' not in session:
            if is_api_request:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        
        # Validate session
        auth_service = current_app.auth_service
        if not auth_service.validate_session(session['session_id']):
            session.clear()
            if is_api_request:
                return jsonify({'error': 'Session expired'}), 401
            flash('Session expired. Please login again.', 'warning')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    auth_service = current_app.auth_service
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('auth/login.html')
        
        try:
            user_session = auth_service.authenticate(username, password)
            session['session_id'] = user_session.session_id
            session['username'] = user_session.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'error')
            return render_template('auth/login.html')
    
    # Check if credentials exist
    if not auth_service.credentials_exist():
        return redirect(url_for('auth.create_credentials'))
    
    return render_template('auth/login.html')


@bp.route('/create-credentials', methods=['GET', 'POST'])
def create_credentials():
    """Create initial credentials (first-time setup)."""
    auth_service = current_app.auth_service
    
    # If credentials already exist, redirect to login
    if auth_service.credentials_exist():
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        
        if not username:
            flash('Username cannot be empty', 'error')
            return render_template('auth/create_credentials.html')
        
        if not password:
            flash('Password cannot be empty', 'error')
            return render_template('auth/create_credentials.html')
        
        if password != confirm:
            flash('Passwords do not match', 'error')
            return render_template('auth/create_credentials.html')
        
        try:
            auth_service.create_credentials(username, password)
            flash('Credentials created successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Failed to create credentials: {str(e)}', 'error')
            return render_template('auth/create_credentials.html')
    
    return render_template('auth/create_credentials.html')


@bp.route('/logout')
def logout():
    """Logout and clear session."""
    auth_service = current_app.auth_service
    
    if 'session_id' in session:
        auth_service.logout(session['session_id'])
    
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('auth.login'))

