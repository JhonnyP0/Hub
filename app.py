from flask import Flask, render_template,flash,redirect,url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_login import LoginManager,login_user,login_required, current_user
from dotenv import load_dotenv
import os
from extend import db

app =Flask(__name__)
load_dotenv()
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.secret_key = os.getenv('API_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
mail = Mail(app)
s =URLSafeTimedSerializer(app.secret_key)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_request
def make_session_permanent():
    from flask import session
    session.permanent = True

@login_manager.user_loader
def load_user(user_id):
    from source import Users
    return Users.query.get(int(user_id))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    from source import LoginForm, Users
    form = LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_confirmed:
                flash('You must confirm your email address before logging in.', 'warning')
                return render_template('login.html', form=form)
            login_user(user)
            flash('Logged in successfully.','success')
            return render_template('index.html')
        else:
            flash('Invalid username or password.','error')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    from source import RegisterForm
    form = RegisterForm()
    if form.validate_on_submit():
        from source import Users
        existing_user = Users.query.filter((Users.username == form.username.data) | (Users.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already exists.','error')
            return render_template('register.html', form=form)
        new_user = Users(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)

        try:
            db.session.add(new_user)
            db.session.commit()
            token=s.dumps(new_user.email, salt='email-confirm')
            link = url_for('confirm_email', token=token, _external=True)
            msg = Message('Confirm Your Email', sender=app.config['MAIL_USERNAME'], recipients=[new_user.email])
            msg.body = f'Please click the link to confirm your email: {link}'
            mail.send(msg)
            flash('Registration successful! Please check your email to confirm your account.', 'info')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'error')
            return render_template('register.html', form=form)
        
    return render_template('register.html', form=form)

@app.route('/projects', methods=['GET'])
def projects():
    return render_template('projects.html')

@app.route('/confirm_email/<token>')
def confirm_email(token):
    from source import Users
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('The activation link is invalid or has expired.', 'error')
        return redirect(url_for('login'))

    user = Users.query.filter_by(email=email).first_or_404()

    if user.is_confirmed:
        flash('Account is already confirmed.', 'info')
    else:
        user.is_confirmed = True
        db.session.add(user) 
        db.session.commit()
        flash('Account has been activated! You can now log in.', 'success')

    return redirect(url_for('login'))

@app.route('/opinion', methods=['GET', 'POST'])
@login_required
def opinion():
    from source import ReviewForm, Post
    form = ReviewForm()
    all_opinions=Post.query.all()
    if form.validate_on_submit():
        new_post = Post(content=form.content.data, opinion_score=form.score.data, user_id=current_user.id)
        try:
            existing_post=Post.query.filter_by(user_id=current_user.id).first()
            if existing_post:
                flash('You have already submitted a review.', 'error')
                return redirect(url_for('opinion'))
            else:
                db.session.add(new_post)
                db.session.commit()
                flash('Your review has been submitted successfully.', 'success')
                msg = Message(f'Thank you for submitting your review with a score of {form.score.data}!',sender=app.config['MAIL_USERNAME'], recipients=[current_user.email])
                msg.body = f'Dear {current_user.username},\n\nThank you for your valuable feedback!\n\nYour review: \n\n{form.content.data}\n\nYour opinion matters!\n\nBest regards,\nThe Team'
                mail.send(msg)
                return redirect(url_for('opinion'))
        except:
            flash('An error occurred while submitting your review. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('opinion.html', form=form, opinions=all_opinions)

@app.route('/logout')
@login_required
def logout():
    from flask_login import logout_user
    flash('You have been logged out.', 'info')
    logout_user()
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9091, debug=True)
