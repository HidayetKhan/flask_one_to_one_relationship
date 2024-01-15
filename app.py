from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api ,Resource

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api=Api(app)
db=SQLAlchemy(app)


class User(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(200),unique=True)
    password=db.Column(db.String(150))

    profile = db.relationship('UserProfile', back_populates='user', uselist=False)

    def __repr__(self):
        return f'<User {self.username}>'
    

class UserProfile(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    # Define the one-to-one relationship with User
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), unique=True, nullable=False)
    user = db.relationship('User', back_populates='profile', uselist=False)


class UserResorce(Resource):
    def get(self,user_id=None):
        if user_id:
            user=User.query.get(user_id)
            if user:
               return {'id':user.id,'username':user.username,'password':user.password,'full_name':user.profile.full_name if user.profile else None},200
            else:
                return {'message':'user not found'},400
        else:
            users=User.query.all()
            user_list=[{'id':user.id,'username':user.username,'password':user.password,'full_name':user.profile.full_name if user.profile else None}for user in users]
            return {'users':user_list}

    def post(self):
        data=request.get_json()
        new_user=User(username=data['username'],password=data['password'])
        if 'full_name' in data:
            new_user.profile=UserProfile(full_name=data['full_name'])
        db.session.add(new_user)
        db.session.commit()
        return {'message':'new user created succsefully','id':new_user.id}


    def put(self,user_id):
        user=User.query.get(user_id)
        if user:
            data=request.get_json()
            user.username=data['username']
            user.password=data['password']
            if 'full_name' in data:
                if not user.profile:
                    user.profile=UserProfile(full_name=data['full_name'])
                else:
                    user.profile.full_name=data['full_name']
            db.session.commit()
            return {'meassage':'user data is updated','id':user.id}
        else:
            return {'message':'user not found'},404
        

    def delete(self,user_id):
        user=User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return {'message':'user is deklete'}
        else:
            return {'message':'user not found'},404



api.add_resource(UserResorce,'/gete','/gete/<int:user_id>')




if __name__=='__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)