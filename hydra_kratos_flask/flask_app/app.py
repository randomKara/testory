import os
import requests
from flask import Flask, redirect, request, session, url_for, render_template_string, jsonify, render_template
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Configuration URLs
KRATOS_PUBLIC_URL = os.environ.get("KRATOS_PUBLIC_URL", "http://kratos:4433")
KRATOS_UI_URL = os.environ.get("KRATOS_UI_URL", "http://localhost:4455")

# Default text for home page
HOME_TEXT = "Welcome to the Flask application!"



def check_kratos_session():
    """Check if user has valid Kratos session"""
    try:
        # Get all cookies from request and forward them to Kratos
        cookies = {k: v for k, v in request.cookies.items()}
        
        # Check with Kratos whoami endpoint
        response = requests.get(
            f"{KRATOS_PUBLIC_URL}/sessions/whoami",
            cookies=cookies,
            timeout=5
        )
        
        if response.status_code == 200:
            user_data = response.json()
            # Extract user information from Kratos session
            identity = user_data.get('identity', {})
            traits = identity.get('traits', {})
            
            # Store user information in Flask session
            session['authenticated'] = True
            session['user_email'] = traits.get('email', 'Unknown')
            session['user_id'] = identity.get('id', 'Unknown')
            session['user_name'] = traits.get('name', traits.get('email', 'User'))
            return True
    except Exception as e:
        print(f"Error checking Kratos session: {e}")
    
    return False

def login_required(f):
    """Decorator to protect routes - like Keycloak App A"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_kratos_session():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def home():
    """Main page - protected like Keycloak App A"""
    global HOME_TEXT
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Flask + Kratos Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .success { background-color: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }
        .button { display: inline-block; padding: 12px 24px; margin: 8px; text-decoration: none; border-radius: 6px; font-weight: bold; transition: all 0.3s; text-align: center; }
        .logout-btn { background-color: #dc3545; color: white; }
        .logout-btn:hover { background-color: #c82333; }
        .protected-btn { background-color: #28a745; color: white; }
        .protected-btn:hover { background-color: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ home_text }}</h1>
        
        <div class="success">
            <h3>🎉 Authentication Successful!</h3>
            <p><strong>Email:</strong> {{ session.get('user_email') }}</p>
            <p><strong>Name:</strong> {{ session.get('user_name') }}</p>
            <p><strong>User ID:</strong> <code>{{ session.get('user_id') }}</code></p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="/protected" class="button protected-btn">Test Protected API</a>
            <a href="/logout" class="button logout-btn">Logout</a>
        </div>
        
        <div style="background-color: #e7f3ff; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; margin: 20px 0;">
            <h4>Test Users:</h4>
            <ul>
                <li><strong>user1@example.com</strong> / password: <code>user1</code></li>
                <li><strong>user2@example.com</strong> / password: <code>user2</code></li>
            </ul>
        </div>
    </div>
</body>
</html>
    """, home_text=HOME_TEXT)


@app.route("/login")
def login():
    """Redirect to Kratos UI - like Keycloak App A"""
    return redirect(f"{KRATOS_UI_URL}/login")


@app.route("/logout")
def logout():
    """Logout endpoint - clear session and redirect to Kratos logout"""
    session.clear()
    return redirect(f"{KRATOS_UI_URL}/login")


@app.route("/protected")
@login_required
def protected():
    """Protected API endpoint"""
    return jsonify({
        "status": "success",
        "message": "Authentication successful! This is a protected endpoint.",
        "user_data": {
            "email": session.get("user_email"),
            "name": session.get("user_name"), 
            "user_id": session.get("user_id"),
            "authenticated": session.get("authenticated")
        },
        "timestamp": str(__import__('datetime').datetime.now())
    })


@app.route("/register")
def register():
    """Registration is disabled"""
    return jsonify({"error": "Registration is disabled. Please contact administrator."}), 403


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "flask-kratos-app"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)