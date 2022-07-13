from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from const import users, offers, orders

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

db.create_all()


for u in users:
    user = User(id=u['id'], first_name=u['first_name'], last_name=u['last_name'], 
                age=u['age'], email=u['email'], role=u['role'], phone=u['phone'])
    db.session.add(user)
    db.session.commit()


for o in orders:
    order = Order(id=o['id'], name=o['name'], description=o['description'], 
                start_date=datetime.strptime(o['start_date'], "%m/%d/%Y").date(), end_date=datetime.strptime(o['end_date'], "%m/%d/%Y").date(), 
                address=o['address'], price=o['price'], 
                customer_id=o['customer_id'], executor_id=o['executor_id'])
    db.session.add(order)
    db.session.commit()

for o in offers:
    offer = Offer(id=o['id'], order_id=o['order_id'], executor_id=o['executor_id'])
    db.session.add(offer)
    db.session.commit()

@app.route('/users', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        users = db.session.query(User).all()
        result = ''
        for user in users:
            result += '<p>'
            u = user.__dict__
            del u['_sa_instance_state']
            for key in u:
                result += key + ' :  ' + str(u[key]) + '<br>'
            result += '</p>'
        return result
    if request.method == 'POST':
        u = request.get_json()
        new_user = User( first_name=u['first_name'], last_name=u['last_name'], 
                age=u['age'], email=u['email'], role=u['role'], phone=u['phone'])
        db.session.add(new_user)
        db.session.commit()        
        return 'Пользователь добавлен'

@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def get_user_by_id(id):
    if request.method == 'GET':
        user = db.session.query(User).filter(User.id == id).all()
        if len(user) == 0:
            return 'NO'
        else:
            result = ''        
            result += '<p>'
            u = user[0].__dict__
            del u['_sa_instance_state']
            for key in u:
                result += key + ' :  ' + str(u[key]) + '<br>'
            result += '</p>'
            return result
    if request.method == 'DELETE':
        user = db.session.query(User).filter(User.id == id).all()
        if len(user) == 0:
            return 'Такого пользователя нет'
        else:
            if user[0].role == 'customer':
                Order.query.filter(Order.customer_id == id).delete()
                db.session.commit()
            if user[0].role == 'executor':
                Offer.query.filter(Offer.executor_id == id).delete()
                db.session.commit()
            User.query.filter(User.id == id).delete()
            db.session.commit()
            return 'Пользователь удален'
    if request.method == 'PUT':
        user = db.session.query(User).filter(User.id == id).all()
        if len(user) == 0:
            return 'Такого пользователя нет'
        else:
            User.query.filter(User.id == id).update(request.get_json())
            db.session.commit()
            return 'Пользователь обновлен'

@app.route('/orders', methods=['GET', 'POST'])
def get_orders():
    if request.method == 'GET':
        orders = db.session.query(Order).all()
        result = ''
        for order in orders:
            result += '<p>'
            o = order.__dict__
            del o['_sa_instance_state']
            for key in o:
                result += key + ' :  ' + str(o[key]) + '<br>'
            result += '</p>'
        return result
    if request.method == 'POST':
        o = request.get_json()
        new_order = Order(name=o['name'], description=o['description'], 
                start_date=datetime.strptime(o['start_date'], "%m/%d/%Y").date(), end_date=datetime.strptime(o['end_date'], "%m/%d/%Y").date(), 
                address=o['address'], price=o['price'], 
                customer_id=o['customer_id'], executor_id=o['executor_id'])
        db.session.add(new_order)
        db.session.commit()        
        return 'Заказ добавлен'

@app.route('/orders/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def get_order_by_id(id):
    if request.method == 'GET':
        order = db.session.query(Order).filter(Order.id == id).all()
        if len(order) == 0:
            return 'NO'
        else:
            result = ''        
            result += '<p>'
            o = order[0].__dict__
            del o['_sa_instance_state']
            for key in o:
                result += key + ' :  ' + str(o[key]) + '<br>'
            result += '</p>'
            return result
    if request.method == 'DELETE':
        order = db.session.query(Order).filter(Order.id == id).all()
        if len(order) == 0:
            return 'Такого заказа нет'
        else:
            Order.query.filter(Order.id == id).delete()
            db.session.commit()
            return 'Заказ удален'
    if request.method == 'PUT':
        order = db.session.query(Order).filter(Order.id == id).all()
        if len(order) == 0:
            return 'Такого заказа нет'
        else:
            Order.query.filter(Order.id == id).update(request.get_json())
            db.session.commit()
            return 'Заказ обновлен'

@app.route('/offers', methods=['GET', 'POST'])
def get_offers():
    if request.method == 'GET':
        offers = db.session.query(Offer).all()
        result = ''
        for offer in offers:
            result += '<p>'
            o = offer.__dict__
            del o['_sa_instance_state']
            for key in o:
                result += key + ' :  ' + str(o[key]) + '<br>'
            result += '</p>'
        return result
    if request.method == 'POST':
        o = request.get_json()
        new_offer = Offer(order_id=o['order_id'], executor_id=o['executor_id'])
        db.session.add(new_offer)
        db.session.commit()        
        return 'Предложение добавлено'

@app.route('/offers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def get_offer_by_id(id):
    if request.method == 'GET':
        offer = db.session.query(Offer).filter(Offer.id == id).all()
        if len(offer) == 0:
            return 'NO'
        else:
            result = ''        
            result += '<p>'
            o = offer[0].__dict__
            del o['_sa_instance_state']
            for key in o:
                result += key + ' :  ' + str(o[key]) + '<br>'
            result += '</p>'
            return result
    if request.method == 'DELETE':
        offer = db.session.query(Offer).filter(Offer.id == id).all()
        if len(offer) == 0:
            return 'Такого предложения нет'
        else:
            Offer.query.filter(Offer.id == id).delete()
            db.session.commit()
            return 'Предложение удалено'
    if request.method == 'PUT':
        offer = db.session.query(Offer).filter(Offer.id == id).all()
        if len(offer) == 0:
            return 'Такого предложения нет'
        else:
            Offer.query.filter(Offer.id == id).update(request.get_json())
            db.session.commit()
            return 'Предложение обновлено'

app.run(debug=True)
