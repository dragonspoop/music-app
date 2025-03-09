from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='ajaypatgar',
    database='music_db'
)
cursor = conn.cursor()

# Ensure table exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS songs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL
)
''')
conn.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form.get('search')
        cursor.execute("SELECT * FROM songs WHERE title LIKE %s", (f"%{search_query}%",))
    else:
        cursor.execute("SELECT * FROM songs")

    songs = cursor.fetchall()
    return render_template('index.html', songs=songs)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    title = request.form.get('title')

    if file and title and file.filename.endswith('.mp3'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        cursor.execute("INSERT INTO songs (title, filename) VALUES (%s, %s)", (title, file.filename))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/play/<filename>')
def play(filename):
    return redirect(url_for('static', filename=f'uploads/{filename}'))


@app.route('/delete/<int:song_id>', methods=['POST'])
def delete(song_id):
    cursor.execute("SELECT filename FROM songs WHERE id = %s", (song_id,))
    song = cursor.fetchone()

    if song:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], song[0])
        if os.path.exists(filepath):
            os.remove(filepath)

        cursor.execute("DELETE FROM songs WHERE id = %s", (song_id,))
        conn.commit()

    return redirect(url_for('index'))
@app.route('/edit/<int:song_id>', methods=['POST'])
def edit(song_id):
    new_title = request.form.get('new_title')
    if new_title:
        cursor.execute("UPDATE songs SET title = %s WHERE id = %s", (new_title, song_id))
        conn.commit()

    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)
