from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime,timezone,timedelta
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    profile_picture = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')

    orders = db.relationship('Order', backref='customer', lazy=True, cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', back_populates='user', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='author', lazy=True, cascade='all, delete-orphan')
    assigned_tasks = db.relationship('Schedule', backref='staff', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "profile_picture": self.profile_picture,
            "role": self.role,
        }

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Menu(db.Model):
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    available = db.Column(db.Boolean, default=True)

    items = db.relationship('MenuItem', backref='menu', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "available": self.available,
            "items": [item.to_dict() for item in self.items],
        }



class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    available = db.Column(db.Boolean, default=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)

    order_items = db.relationship('OrderItem', backref='menu_item', lazy=True)
    reviews = db.relationship('Review', backref='item', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image_url": self.image_url,
            "available": self.available,
            "menu_id": self.menu_id,
        }



class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    items = db.relationship('OrderItem', backref='parent_order', lazy=True)
    user = db.relationship('User', back_populates='orders')

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "total": self.total_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "items": [item.to_dict() for item in self.items]
        }

    @property
    def total_amount(self):
        return sum(item.price * item.quantity for item in self.items)



class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "menu_item_id": self.menu_item_id,
            "quantity": self.quantity,
            "price": self.price,
        }


class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reservation_time = db.Column(db.DateTime, nullable=False)
    guest_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='reservations')  

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name,
            'reservation_time': self.reservation_time.isoformat(),
            'guest_size': self.guest_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)  
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    user = db.relationship('User', back_populates='reviews')  

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name,
            'menu_item_id': self.menu_item_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }



class Schedule(db.Model):
    __tablename__ = 'staff_schedules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    tasks = db.Column(db.Text, nullable=False)  
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

  
    staff_member = db.relationship('User', backref='schedules')

    def to_dict(self):
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "staff_name": self.staff_member.name if self.staff_member else None,
            "date": self.date.isoformat(),
            "start_time": self.start_time.strftime("%H:%M"),
            "end_time": self.end_time.strftime("%H:%M"),
            "tasks": self.tasks,
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
