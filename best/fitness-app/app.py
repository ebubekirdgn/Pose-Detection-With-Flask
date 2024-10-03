from flask import Flask, Response, jsonify, render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from exercises.bicepsCurlStrategy import BicepsCurlStrategy  # Doğru içe aktarma
from exercises.tricepsExtensionStrategy import TricepsExtensionStrategy
from exercises.exercise_strategy import ExerciseStrategy
import mediapipe as mp
from functools import wraps

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Global counter değişkeni

biceps_strategy = BicepsCurlStrategy()

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

#--------------------------------------------------ROOTLAR ------------------------------------------------------------------------------------
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
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('layout'))
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


@app.route('/layout')
def layout():
    if 'user' not in session:
        return redirect(url_for('login'))  # Oturum yoksa giriş sayfasına yönlendir
    return render_template('layout.html', user=session['user'])  # Oturum varsa layout sayfasını yükle

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('login'))

#--------------------------------------------------------------------HAREKETLER--------------------------------------------------------------------
@app.route('/biceps_curl', methods=['GET', 'POST'])
def biceps_curl():
    return render_template('components/biceps_curl.html', user=session['user']) 

@app.route('/triceps_extension')
def triceps_extension():
     return render_template('components/triceps_extension.html')

#--------------------------------------------------------------------KAMERA------------------------------------------------------------------------
@app.route('/start', methods=['POST'])
def start():
    biceps_strategy.perform_exercise()  # Egzersizi başlat
    return jsonify(status='Camera Started')

@app.route('/stop', methods=['POST'])
def stop_camera():
    # Durdurma işlemleri
    return '', 204  # Boş bir yanıt döndür

@app.route('/finish', methods=['POST'])
def finish_stream():
    # Tamamlayıcı işlemler
    return '', 204  # Boş bir yanıt döndür

#-------------------------------------------------------------------HAREKET METHODLARI------------------------------------------------------------
@app.route('/biceps_video_feed')
def biceps_video_feed():
    return Response(biceps_strategy.perform_exercise(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
