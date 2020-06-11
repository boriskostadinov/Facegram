from functools import wraps

from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify, session, make_response
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from time import localtime, strftime

from user import User
from advertisement import Advertisement

import json
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "SxOW8IKSGVShQD6BXtQzMA"
app.secret_key = "SxOW8IKSGVShQD6BXtQzMA"
upload_folder = "\\D:\\CHATAPP\\Webchat\\img"

socketio = SocketIO(app)
ROOMS = ["lounge", "news", "games", "coding"]

def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get('token')
        if not token or not User.verifyToken(token):
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    token = request.cookies.get('token')
    user_id = session.get("user_id")
    if token:
        username = User.find_name_by_id(user_id)
        return render_template('index.html', advertisements=Advertisement.all(), token=token, username=username)
    else:
        return render_template('index.html', advertisements=Advertisement.all(), token=token)

@app.route('/profile')
def profile():
    token = request.cookies.get('token')
    if token:
        user_id = session.get("user_id")
        username = User.find_name_by_id(user_id)
        email = User.find_email_by_id(user_id)
        address = User.find_address_by_id(user_id)
        mobile = User.find_mobile_by_id(user_id)
        return render_template('profile.html', 
                                username=username, 
                                email = email, 
                                address = address, 
                                mobile = mobile,
                                user_id = user_id)
                                
    else:
        return redirect('/login')

@app.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_profile(id):
    user = User.find_user_by_id(id)
    if request.method == "GET":
        return render_template('edit_profile.html', user = user)
    elif request.method == "POST":
        user.email = request.form['email']
        user.name = request.form['name'] 
        user.address = request.form['address'] 
        user.mobile = request.form['mobile'] 
        user.save()
        return redirect('/profile')

@app.route('/new', methods=['GET', 'POST'])
def new_ad():
    if request.method == 'GET':
        return render_template('new_ad.html')
    elif request.method == 'POST':
        user_id = session.get("user_id")
        values = (
            None,
            request.form['title'],
            request.form['description'],
            request.form['price'],
            request.form['date'],
            1,
            0,
            user_id
        )
        Advertisement(*values).create()

        return redirect('/')

@app.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_ad(id):
    advertisement = Advertisement.find(id)
    if request.method == "GET":
        return render_template('edit_ad.html', advertisement=advertisement)
    elif request.method == "POST":
        advertisement.title = request.form['title']
        advertisement.description = request.form['description']
        advertisement.price = request.form['price']
        advertisement.date = request.form['date']
        advertisement.save()
        return redirect(url_for('show_advertisement', id = advertisement.id))

@app.route('/<int:id>')
def show_advertisement(id):
    token = request.cookies.get('token')
    advertisement = Advertisement.find(id)
    user_id = session.get("user_id")
    if advertisement.active == 0:
        buyer = Advertisement.buyer_info_by_id(advertisement.buyer_id)
        return render_template('advertisement.html', advertisement=advertisement, token=token, user_id=user_id, buyer=buyer)
    else:
        return render_template('advertisement.html', advertisement=advertisement, token=token, user_id=user_id)

@app.route('/<int:id>/delete', methods=['POST'])
def delete_ad(id):
    advertisement = Advertisement.find(id)
    if advertisement.seller_id == session.get("user_id"):
        advertisement.delete()

    return redirect('/')

@app.route('/<int:id>/buy', methods=['POST'])
def buy_ad(id):
    advertisement = Advertisement.find(id)
    if advertisement.seller_id != session.get("user_id"):
        buyer_id = session.get("user_id")
        advertisement.buy(buyer_id)

    return redirect('/')

@app.route('/search', methods=['GET', 'POST'])
def search_user():
    if request.method == 'GET':
        return render_template('search.html')
    elif request.method == "POST":
        email = request.form['email']
        if User.find(email) == False:
            username = "This user doesn't exists"
            return redirect('/search')
        else:
            user2 = User.find(email)
            username = user2.name
        return redirect(url_for('follow', username=username, id=user2.id))

@app.route('/<int:id>/follow', methods=['GET', 'POST'])
def follow(id):
    user2 = User.find_user_by_id(id)
    user_id = session.get("user_id")
    user = User.find_user_by_id(user_id)
    if request.method == 'GET':
        return render_template('follow.html', user2 = user2, user = user)
    elif request.method == 'POST':
        user1 = User.find_user_by_id(user_id)
        if user1.check_follow(user2.id) == False:
            user1.follow(user2.id)
        return redirect(url_for('follow', id=user2.id))
        
@app.route('/<int:id>/unfollow', methods=['GET', 'POST'])
def unfollow(id):
    username = request.args.get('username')
    # print("\n\n\n\n\n")
    user_id2 = User.find_id_by_name(username)
    user_id1 = session.get("user_id")
    current_user = User.find_user_by_id(user_id1)
    current_user.unfollow(user_id2)
    return redirect(url_for('search_user'))





@app.route('/register', methods=["GET", "POST"])
def register():
    token = request.cookies.get('token')
    if not token or not User.verifyToken(token):
        if request.method == 'GET':
            return render_template('register.html')
        elif request.method == 'POST':
            # if 'file' not in request.files:
            #     return redirect(request.url)
            # file = request.files['file']
            # if file.filename == '':
            #     filename = secure_filename("/default.png")
            #     filepath = os.path.join("img", filename)
            # if file and User.allowed_file(file.filename):
            #     filename = secure_filename(file.filename)
            #     file.save(os.path.join(upload_folder, filename))
            #     filepath = os.path.join("img/uploads", filename)
            info = (
                None,
                request.form['email'],
                User.hashPassword(request.form['password']),
                request.form['name'],
                request.form['address'],
                request.form['mobile'] #,
                # filepath
            )
            User(*info).create()
            return redirect('/')
    else:
        return redirect('/')


@app.route('/login', methods=["GET", "POST"])
def login():
    token = request.cookies.get('token')
    if not token:
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            data = json.loads(request.data.decode('ascii'))
            email = data['email']
            password = data['password']
            user = User.find(email)
            if not user or not user.verifyPassword(password):
                return jsonify({'token': None})
            token = user.generateToken()
            session["user_id"] = user.id
            return jsonify({'token': token.decode('ascii')})
    else:
        return redirect('/')

@app.route('/logout', methods=["GET"])
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('token', '', expires=0)
    session.pop("user_id")
    return resp

@app.route("/chat", methods=['GET', 'POST'])
def chat():
    
    user_id = session.get("user_id")
    username = User.find_name_by_id(user_id)
    # print(username)

    return render_template('chat.html', username=username, rooms=ROOMS)

@socketio.on('message')
def message(data):
    
    print(f"\n\n{data}\n\n")
    # emit('some-event', 'this is a  custom event message')

    send({'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime('%b-%d %I:%M%p', localtime())}, room=data['room'])
 
@socketio.on("join")
def join(data):

    join_room(data['room'])
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])

@socketio.on("leave")
def leave(data):

    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])


if __name__ == "__main__":
    socketio.run(app, debug=True)

# if __name__ == '__main__':
#     app.run(debug=True)      
