import hashlib
from database import DB

from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired
    )

SECRET_KEY = "SxOW8IKSGVShQD6BXtQzMA"


class User:
    def __init__(self, id, email, password, name, address, mobile
    # , picture
    ):
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.address = address
        self.mobile = mobile
        # self.picture = picture

    def create(self):
    	with DB() as db:
       		values = (self.email, self.password, self.name, 
            	self.address, self.mobile)
        	db.execute('''
            	INSERT INTO users (email, password, name, address, mobile)
            	VALUES (?, ?, ?, ?, ?)''', values)
        	return self

    # @staticmethod
    # def allowed_file(filename):
    #     ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    #     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def find(email):
        if not email:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE email = ?',(email,)
            ).fetchone()
            if row:
                return User(*row)
            else:
                return False

    @staticmethod
    def find_id(id):
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE id = ?',(id,)
            ).fetchone()
            return User(*row)

    @staticmethod
    def find_user_by_id(id):
        if not id:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE id = ?',(id,)
            ).fetchone()
            if row:
                return User(*row)

    @staticmethod
    def find_name_by_id(id):
        with DB() as db:
            name = db.execute(
                'SELECT name FROM users WHERE id = ?',(id,)
            ).fetchone()
            return name[0]

    @staticmethod
    def find_email_by_id(id):
        with DB() as db:
            email = db.execute(
                'SELECT email FROM users WHERE id = ?',(id,)
            ).fetchone()
            return email[0]

    @staticmethod
    def find_address_by_id(id):
        with DB() as db:
            address = db.execute(
                'SELECT address FROM users WHERE id = ?',(id,)
            ).fetchone()
            return address[0]

    @staticmethod
    def find_id_by_name(name):
        with DB() as db:
            id = db.execute(
                'SELECT id FROM users WHERE name = ?',(name,)
            ).fetchone()
            return id[0]


    @staticmethod
    def find_mobile_by_id(id):
        with DB() as db:
            mobile = db.execute(
                'SELECT mobile FROM users WHERE id = ?',(id,)
            ).fetchone()
            return mobile[0]


    def follow(self, user_id2):
        with DB() as db:
            db.execute(
                'INSERT INTO follow (user_id, user_id2) values(?,?)', (self.id, user_id2)
            )
            return self

    def check_follow(self, user_id2):
        with DB() as db:
            following = db.execute(
                'SELECT user_id2 FROM follow WHERE user_id = ? AND user_id2 = ?',(self.id, user_id2,)
            ).fetchone()
            print(following)
            print('1')
            if following == None:
                return False
            else:
                return True

    def unfollow(self, user_id2):
        with DB() as db:
            db.execute(
                'DELETE FROM follow WHERE user_id = ? AND user_id2 =?',(self.id, user_id2,)
            )
        return self

    def save(self):
        with DB() as db:
            values = (
                self.email,
               # self.password,
                self.name,
                self.address,
                self.mobile,
                # self.picture,
                self.id
            )
            db.execute(
                '''UPDATE users 
                SET email = ?, name = ?, address = ?, mobile = ?
                WHERE id = ?''', values
            )
            return self

    @staticmethod
    def hashPassword(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verifyPassword(self, password):
        return self.password == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def generateToken(self):
        s = Serializer(SECRET_KEY, expires_in=600)
        return s.dumps({'email': self.email})

    @staticmethod
    def verifyToken(token):
        s = Serializer(SECRET_KEY)
        try:
            s.loads(token)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        return True
