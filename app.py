from init import *
from config import *

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'your secret keyjskkkisioio'


@app.route("/comments")
def comments():
    data_list = []
    PER_PAGE = 5
    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    cur.execute("SELECT * FROM comments")
    for (id, video_title, username, comment, date) in cur:
        data_list.append({
            "username": username,
            "video_title": video_title,
            "comment": comment,
            'date': date,
        })
    i = (page - 1) * PER_PAGE
    List1 = data_list[i:i + 5]
    pagination = Pagination(page=page, per_page=PER_PAGE, search=search, total=len(data_list),
                            record_name='List')
    parent_active = "comments"
    return render_template('comments.html', data_list=List1, pagination=pagination, parent_active=parent_active)


@app.route("/rate_content", methods=['GET', 'POST'])
def rate_content():
    if request.method == 'POST':
        username = request.form.get("name")
        track_name = request.form.get('track_name')
        comment = request.form.get('message')
        today = current_date.today()
        try:
            statement = "INSERT INTO comments (username,video_title,comment ,date ) VALUES (%s,%s, %s , %s)"
            data = (username, track_name, comment, today)
            cur.execute(statement, data)
            conn.commit()
            print("Successfully added entry to database")
        except Exception as e:
            print(f"Error adding entry to database: {e}")
        return redirect(url_for('comments'))

    data_list = []
    cur.execute("SELECT * FROM videos")
    for (id, video_id, title, video_url, channelTitle, date) in cur:
        data_list.append({
            "video_id": video_id,
            "title": title,
            "video_url": video_url,
            'url': 'https://www.youtube.com/embed/' + video_id,
            'channelTitle': channelTitle,

        })
    parent_active = "rate_content"
    return render_template('rate_my_content.html', data_list=data_list, parent_active=parent_active)


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/content")
def content():
    try:

        if session['loggedin'] == True:

            data_list = []
            PER_PAGE = 8
            search = False
            q = request.args.get('q')
            if q:
                search = True
            try:
                page = int(request.args.get('page', 1))
            except ValueError:
                page = 1
            print(page)
            cur.execute("SELECT * FROM videos")
            for (id, video_id, title, video_url, channelTitle, date) in cur:
                data_list.append({
                    "video_id": video_id,
                    "title": title,
                    "video_url": video_url,
                    'url': 'https://www.youtube.com/embed/' + video_id,
                    'channelTitle': channelTitle,

                })
            i = (page - 1) * PER_PAGE
            List1 = data_list[i:i + 8]
            pagination = Pagination(page=page, per_page=PER_PAGE, search=search, total=len(data_list),
                                    record_name='List')
            parent_active = "content"

            return render_template("index.html", data_list=List1, pagination=pagination, parent_active=parent_active)
        else:
            return redirect(url_for('login'))
    except:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        email = request.form['username']
        password = request.form['password']
        # cur.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password,))
        cur.execute(
            "SELECT * FROM accounts WHERE email=? AND  password =?",
            (email, password,))
        account = {'id': '', 'username': '', 'email': '', 'date': ''}
        for (id, username, email, password, date) in cur:
            account['id'] = id
            account['username'] = username
            account['email'] = email
            account['date'] = date
            print(f"Name: {username}, Email: {email} , ID: ")
        if account['username'] != '':
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return redirect(url_for('content'))
        else:
            msg = 'Incorrect username / password !'
            print(msg)
            return render_template('login.html', msg=msg)
        print(account)
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cur.execute(
            "SELECT * FROM accounts WHERE username =?",
            (username,))
        account = {'id': '', 'username': '', 'email': '', 'date': ''}
        for (id, username, email, password, date) in cur:
            account['id'] = id
            account['username'] = username
            account['email'] = email
            account['date'] = date
            print(f"Name: {username}, Email: {email} , ID: ")
        if account['username'] != '':
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            today = current_date.today()
            statement = "INSERT INTO accounts (username,email,password,date) VALUES (%s,%s, %s,%s)"
            data = (username, email, password, today)
            cur.execute(statement, data)
            conn.commit()
            msg = 'You have successfully registered ! You csn sign in now'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route("/create-table")
def create_table():
    sql = """CREATE TABLE IF NOT EXISTS accounts(
    id INT(11) NOT NULL AUTO_INCREMENT,
    username CHAR(20) NOT NULL,
    email CHAR(50) NOT NULL,
    password CHAR(50) NOT NULL,
    date DATE,
    CONSTRAINT accounts_pk PRIMARY KEY (id))"""
    cur.execute(sql)

    video = """CREATE TABLE IF NOT EXISTS videos(
       id INT(11) NOT NULL AUTO_INCREMENT,
       video_id CHAR(200) NOT NULL,
       title CHAR(200) NOT NULL,
       video_url CHAR(250) NOT NULL,
       channelTitle CHAR(200) NOT NULL,
       date DATE,
       CONSTRAINT videos_pk PRIMARY KEY (id))"""
    cur.execute(video)

    comments = """CREATE TABLE IF NOT EXISTS comments(
       id INT(11) NOT NULL AUTO_INCREMENT,
       video_title CHAR(200) NOT NULL,
       username CHAR(250) NOT NULL,
       comment CHAR(250) NOT NULL,
       date DATE,
       CONSTRAINT comments_pk PRIMARY KEY (id))"""
    cur.execute(comments)
    # cur.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")
    return "All tables are created"


@app.route("/read-json")
def read_json():
    data_list = []
    video_list = []
    cur.execute("SELECT * FROM videos")
    for (id, video_id, title, video_url, channelTitle, date) in cur:
        video_list.append(video_id)
    f = open('emil_de_la_cruz.json')
    data = json.load(f)
    for i in data:
        video_data = data[i]['video_data']
        for key, value in video_data.items():
            print(key, '->', value)
            data_list.append({
                "video_id": key,
                "title": value.get('title'),
                'video_url': 'https://www.youtube.com/watch?v=' + key,
                'channelTitle': value.get('channelTitle'),

            })

    f.close()
    print(data_list)
    for data in data_list:
        if data['video_id'] in video_list:
            pass
        else:
            try:
                statement = "INSERT INTO videos (video_id,title,video_url,channelTitle ) VALUES (%s,%s, %s ,%s)"
                data = (data['video_id'], data['title'], data['video_url'], data['channelTitle'])
                cur.execute(statement, data)
                conn.commit()
                print("Successfully added entry to database")
            except Exception as e:
                print(f"Error adding entry to database: {e}")
            # return "Hello, World!"
    return data_list


@app.route("/create-json")
def create_json():
    yt = YTstats(API_KEY, channel_id)
    yt.extract_all()
    yt.dump()  # dumps to .json
    return "json created"


if __name__ == "__main__":
    app.run()
