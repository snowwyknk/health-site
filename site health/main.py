from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'snowwyzcode'
db = SQLAlchemy(app)

# Настройка Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
# Модель статьи блога
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
# Создаем таблицы при первом запуске
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/articles')
def show_articles():
    posts = Post.query.order_by(Post.created_at.desc()).all()  # Сортировка по дате
    return render_template('articles.html', posts=posts)

@app.route("/nutrition")
def nutrition():
    return render_template("nutrition.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Проверяем, существует ли пользователь
            if User.query.filter_by(username=request.form['username']).first():
                flash('Пользователь уже существует', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=request.form['email']).first():
                flash('Email уже используется', 'error')
                return redirect(url_for('register'))

            # Создаем нового пользователя
            hashed_password = generate_password_hash(request.form['password'], method='sha256')
            new_user = User(
                username=request.form['username'],
                email=request.form['email'],
                password=hashed_password
            )
            
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash('Ошибка при регистрации: ' + str(e), 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        if not request.form['title'] or not request.form['content']:
            return render_template('add_post.html', error="Все поля обязательны")
        post = Post(title=request.form['title'], content=request.form['content'])
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('show_articles'))
    return render_template('add_post.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)