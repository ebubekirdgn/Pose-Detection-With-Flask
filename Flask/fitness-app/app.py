from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Veri tabanı bağlantısı
def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

# Kullanıcı tablosu oluşturma
def create_user_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        date_of_birth DATE NOT NULL,
        height REAL NOT NULL,
        weight REAL NOT NULL
    )''')
    conn.commit()
    conn.close()

create_user_table()

# Login formu
class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    submit = SubmitField('Giriş Yap')

# Register formu
class RegisterForm(FlaskForm):
    first_name = StringField('Ad', validators=[DataRequired()])
    last_name = StringField('Soyad', validators=[DataRequired()])
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Şifreyi Onayla', validators=[DataRequired(), EqualTo('password', message='Şifreler eşleşmiyor')])
    date_of_birth = StringField('Doğum Tarihi (YYYY-MM-DD)', validators=[DataRequired()])
    height = StringField('Boy (cm)', validators=[DataRequired()])
    weight = StringField('Kilo (kg)', validators=[DataRequired()])
    submit = SubmitField('Kayıt Ol')

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Form nesnesi oluşturuluyor
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Kullanıcıyı veri tabanından al
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        # Şifreyi kontrol et
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Kullanıcı adı veya şifre hatalı', 'danger')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()  # Form nesnesi oluşturuluyor
    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data)
        first_name = form.first_name.data
        last_name = form.last_name.data
        date_of_birth = form.date_of_birth.data
        height = form.height.data
        weight = form.weight.data

        # Kullanıcıyı veri tabanına kaydet
        conn = get_db_connection()
        # Kullanıcı adı var mı kontrol et
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if existing_user:
            flash('Kullanıcı adı zaten mevcut!', 'danger')
        else:
            # Şifreleri kontrol et
            if form.password.data != form.confirm_password.data:
                flash('Şifreler eşleşmiyor!', 'danger')
            else:
                try:
                    conn.execute('INSERT INTO users (first_name, last_name, username, password, date_of_birth, height, weight) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                 (first_name, last_name, username, password, date_of_birth, height, weight))
                    conn.commit()
                    flash('Kayıt başarılı! Lütfen giriş yapın.', 'success')
                    return redirect(url_for('login'))
                except Exception as e:
                    flash('Bir hata oluştu: {}'.format(e), 'danger')
                finally:
                    conn.close()

    return render_template('register.html', form=form)



@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
