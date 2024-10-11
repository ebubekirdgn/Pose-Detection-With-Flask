from datetime import datetime
from flask import Flask, Response, jsonify, render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from exercises.bicep_curl_strategy import BicepsCurlStrategy  # Doğru içe aktarma
from exercises.crunch_strategy import CrunchStrategy
from exercises.triceps_extension_strategy import TricepsExtensionStrategy
from exercises.shoulder_press_strategy import ShoulderPressStrategy
from exercises.lateral_raise_strategy import LateralRaiseStrategy
from models.exercise import add_exercise, create_exercises_table
from models.user import create_user_table, get_db_connection
from datetime import datetime  

app = Flask(__name__)
app.secret_key = "your_secret_key"

biceps_strategy = BicepsCurlStrategy()

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
           #flash('Giriş başarılı!', 'success')
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

    user = session['user']
    biceps_strategy = BicepsCurlStrategy()
    totals = biceps_strategy.get_totals(user)  # Toplam değerleri al

    return render_template('layout.html', user=user, totals=totals)  # Toplamları sayfaya gönder

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('login'))

#--------------------------------------------------------------------HAREKETLER--------------------------------------------------------------------
@app.route('/biceps_curl', methods=['GET', 'POST'])
def biceps_curl():
    if 'user' not in session:
        return jsonify(status='Unauthorized'), 401  # Kullanıcı oturumu yoksa hata döndür

    user = session['user']
    biceps_strategy = BicepsCurlStrategy()
    totals = biceps_strategy.get_totals(user)  # Toplam değerleri al

    return render_template('components/biceps_curl.html', user=session['user'],totals=totals) 

@app.route('/triceps_extension')
def triceps_extension():
     if 'user' not in session:
        return redirect(url_for('login'))  # Oturum yoksa giriş sayfasına yönlendir

     user = session['user']
     triceps_extension_strategy = TricepsExtensionStrategy()  # CrunchStrategy sınıfınızı oluşturmalısınız
     totals = triceps_extension_strategy.get_totals(user)  # Toplam değerleri al
     return render_template('components/triceps_extension.html', user=user, totals=totals)

@app.route('/lateral_raise')
def lateral_raise():
     if 'user' not in session:
        return redirect(url_for('login'))  # Oturum yoksa giriş sayfasına yönlendir

     user = session['user']
     lateral_raise_strategy = LateralRaiseStrategy()  # CrunchStrategy sınıfınızı oluşturmalısınız
     totals = lateral_raise_strategy.get_totals(user)  # Toplam değerleri al
     return render_template('components/lateral_raise.html', user=user, totals=totals)

@app.route('/squat')
def squat():
     if 'user' not in session:
        return redirect(url_for('login'))  # Oturum yoksa giriş sayfasına yönlendir

     user = session['user']
     shoulder_press_strategy = CrunchStrategy()  # CrunchStrategy sınıfınızı oluşturmalısınız
     totals = shoulder_press_strategy.get_totals(user)  # Toplam değerleri al
     return render_template('components/squat.html', user=user, totals=totals)

@app.route('/shoulder_press')
def shoulder_press():
     if 'user' not in session:
        return redirect(url_for('login'))  # Oturum yoksa giriş sayfasına yönlendir

     user = session['user']
     shoulder_press_strategy = ShoulderPressStrategy()  # CrunchStrategy sınıfınızı oluşturmalısınız
     totals = shoulder_press_strategy.get_totals(user)  # Toplam değerleri al
     return render_template('components/shoulder_press.html', user=user, totals=totals)

@app.route('/crunch')
def crunch():
    if 'user' not in session:
        return redirect(url_for('login'))  # Oturum yoksa giriş sayfasına yönlendir

    user = session['user']
    crunch_strategy = CrunchStrategy()  # CrunchStrategy sınıfınızı oluşturmalısınız
    totals = crunch_strategy.get_totals(user)  # Toplam değerleri al

    return render_template('components/crunch.html', user=user, totals=totals)  # Toplamları sayfaya gönder

#--------------------------------------------------------------------KAMERA------------------------------------------------------------------------
@app.route('/start', methods=['POST'])
def start():
    biceps_strategy.perform_exercise()  # Egzersizi başlat
    return jsonify(status='Camera Started')

@app.route('/stop', methods=['POST'])
def stop_camera():
    biceps_strategy.stop_exercise()  # Egzersizi durdurma işlevi
    return jsonify(status='Camera Stopped')

@app.route('/finish', methods=['POST'])
def finish_stream():
    if 'user' not in session:
        return jsonify(status='Unauthorized'), 401  # Kullanıcı oturumu yoksa hata döndür

    user = session['user']
    counter_value = biceps_strategy.get_counter()  # Sayaç değerini al
    current_date = datetime.now().date()  # Şu anki tarihi al

    if counter_value > 0:
        # Veritabanından aynı tarih ve kullanıcıya ait mevcut egzersiz kaydını al
        conn = get_db_connection()
        existing_record = conn.execute('SELECT * FROM exercises WHERE user = ? AND created_date = ?', 
                                       (user, current_date)).fetchone()

        if existing_record:
            # Aynı tarihte zaten kayıt var, mevcut biceps curl sayısını güncelle
            new_biceps_curl = existing_record['biceps_curl'] + counter_value
            conn.execute('''
                UPDATE exercises
                SET biceps_curl = ?
                WHERE user = ? AND created_date = ?
            ''', (new_biceps_curl, user, current_date))
            conn.commit()
        else:
            # Aynı tarihte kayıt yok, yeni bir kayıt ekle
            conn.execute('''
                INSERT INTO exercises (user, biceps_curl, triceps_extension, lateral_raise, squat, shoulder_press, crunch, created_date)
                VALUES (?, ?, 0, 0, 0, 0, 0, ?)
            ''', (user, counter_value, current_date))
            conn.commit()

        conn.close()

        # Sayaç sıfırlama işlemi
        biceps_strategy.reset_counter()

        # Kullanıcıya başarı mesajı döndür
        return jsonify(status='Exercise Finished', counter=counter_value)
    else:
        return jsonify(status='No data to save')  # Sayaç sıfırsa veri kaydedilmez

#-------------------------------------------------------------------HAREKET METHODLARI------------------------------------------------------------
@app.route('/biceps_video_feed')
def biceps_video_feed():
    return Response(biceps_strategy.perform_exercise(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_counter')
def get_counter():
    # Sayaç değerini JSON formatında döndür
    counter_value = biceps_strategy.get_counter()
    return jsonify({'counter': counter_value})

if __name__ == '__main__':
    create_user_table()
    create_exercises_table()
    app.run(debug=True)
