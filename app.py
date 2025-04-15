from flask import Flask, render_template, request, jsonify, session, url_for, redirect
import os
from dotenv import load_dotenv
from search import search_with_gemini
from authlib.integrations.flask_client import OAuth
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=30)

#database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'github_users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#github oauthorization

oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',
    refresh_token_url=None,
    client_kwargs={'scope':'user:email repo:status repo_deployment public_repo'}
)
#user model

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    github_id = db.Column(db.Integer, nullable = False, unique = True)
    username = db.Column(db.String(200), nullable = True)
    email = db.Column(db.String(200))
    avatar_url = db.Column(db.String(200))
    access_token = db.Column(db.String(200), nullable = True)
# routes

@app.route("/")
def main():
    github_id = request.cookies.get('github_id')
    if github_id: #if ID exists in cookies then identify the browser ami oke bhule gechi, o amake bholeni
        user = User.query.filter_by(github_id = github_id).first()
        if user: #user ke chine nao
            session.permanent = True
            session['github_user'] = {
                'id': user.github_id,
                'login': user.username,
                'email': user.email,
                'avatar_url': user.avatar_url,
                'access_token': user.access_token
            }
    return render_template("index.html")

@app.route("/login")
def login():
    return github.authorize_redirect(url_for('login_callback', _external=True))

@app.route('/login/callback')
def login_callback():
    token = github.authorize_access_token()
    user_data = github.get('https://api.github.com/user').json()
    
    user = User.query.filter_by(github_id=user_data['id']).first()
    if not user:
        user = User(
            github_id=user_data['id'],
            username=user_data.get('login'),
            email=user_data.get('email'),
            avatar_url=user_data.get('avatar_url'),
            access_token=token['access_token']  # Store the access token here
        )
        db.session.add(user)
    else:
        user.access_token = token['access_token']
    db.session.commit()
    user_data['access_token'] = token['access_token']
    session['github_user'] = user_data
    response = redirect(url_for('main'))
    response.set_cookie('github_id', str(user.github_id), max_age=60*60*24*30)  # 30 days
    return response

@app.route("/logout")
def logout():
    session.clear()
    response = redirect(url_for("main"))
    response.delete_cookie('github_id', path='/')
    response.set_cookie('session', '', expires=0)
    return response

@app.route('/search', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        user_input = data.get('user_input')
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        github_user = session.get('github_user')
        if not github_user:
            return jsonify({"error": "User is not authenticated"}), 400

        username = github_user.get('login')
        access_token = github_user.get('access_token')
        if "assigned issues" in user_input.lower() or "github" in user_input.lower():
            from github import get_issues_of_user
            issues = get_issues_of_user(username, access_token)
            return jsonify({"response": f"Here are your tasks\n{issues}"})
        
        chat_memory = session.get("chat_memory", [])
        response = search_with_gemini(user_input, chat_memory)
        chat_memory.append({"user_input": user_input, "bot_response": response})
        chat_memory = chat_memory[-20:]
        session["chat_memory"] = chat_memory
        return jsonify({"response": response})
    
    except Exception as e:
        print(f"Error during /search: {e}")
        return jsonify({"response": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    with app.app_context():  # Start an app context
        db.create_all()
    app.run(debug=True)