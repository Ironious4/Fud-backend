from models import db, User, Menu, MenuItem, Order, OrderItem, Reservation, Review, Schedule
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_jwt_extended import ( 
    JWTManager, jwt_required, create_access_token, get_jwt, get_jwt_identity, create_refresh_token
)
from flask_cors import CORS
from datetime import datetime, timedelta

from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from werkzeug.utils import secure_filename
from dotenv import load_dotenv


import secrets
import os

load_dotenv()


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7) 
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)   


db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)




UPLOAD_FOLDER = 'static/uploads'  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    role = request.form.get('role', 'customer')

    profile_picture_file = request.files.get('profile_picture')
    
    
    if profile_picture_file and allowed_file(profile_picture_file.filename):
        filename = secure_filename(profile_picture_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_picture_file.save(filepath)
        profile_picture_url = f"/{filepath}" 
    else:
        return jsonify({'message': 'Invalid or missing profile picture'}), 400


    if User.query.filter((User.name == name) | (User.email == email)).first():
        return jsonify({'message': 'User already exists'}), 400

    
    user = User(
        name=name,
        email=email,
        phone_number=phone_number,
        profile_picture=profile_picture_url,
        role=role
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=int(user.id))

    return jsonify({
        'message': 'User created successfully',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone_number': user.phone_number,
            'profile_picture': user.profile_picture,
            'role': user.role
        }
    }), 200


@app.route('/login', methods=['POST'])
def login(refresh=True):
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'msg': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}
    }), 200



@app.route('/admin/signup', methods=['POST'])
def admin_signup():
    name = request.form.get('name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    role = request.form.get('role', 'admin')

    profile_picture_file = request.files.get('profile_picture')
    
    
    if profile_picture_file and allowed_file(profile_picture_file.filename):
        filename = secure_filename(profile_picture_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_picture_file.save(filepath)
        profile_picture_url = f"/{filepath}"  
    else:
        return jsonify({'message': 'Invalid or missing profile picture'}), 400

  
    if User.query.filter((User.name == name) | (User.email == email)).first():
        return jsonify({'message': 'Admin already exists'}), 400

  
    user = User(
        name=name,
        email=email,
        phone_number=phone_number,
        profile_picture=profile_picture_url,
        role=role
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=int(user.id))

    return jsonify({
        'message': 'Admin created successfully',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone_number': user.phone_number,
            'profile_picture': user.profile_picture,
            'role': user.role
        }
    }), 200





@app.route('/staff/signup', methods=['POST'])
def staff_signup():
    name = request.form.get('name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    role = request.form.get('role', 'staff')

    profile_picture_file = request.files.get('profile_picture')
    
    
    if profile_picture_file and allowed_file(profile_picture_file.filename):
        filename = secure_filename(profile_picture_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_picture_file.save(filepath)
        profile_picture_url = f"/{filepath}"  
    else:
        return jsonify({'message': 'Invalid or missing profile picture'}), 400

    
    if User.query.filter((User.name == name) | (User.email == email)).first():
        return jsonify({'message': 'Staff already exists'}), 400

    user = User(
        name=name,
        email=email,
        phone_number=phone_number,
        profile_picture=profile_picture_url,
        role=role
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=int(user.id))

    return jsonify({
        'message': 'Staff created successfully',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone_number': user.phone_number,
            'profile_picture': user.profile_picture,
            'role': user.role
        }
    }), 200





@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Logout successful"}), 200



@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200


@app.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200



@app.route('/menu', methods=['GET'])
@jwt_required()
def get_menus():
    menus = Menu.query.all()
    return jsonify([menu.to_dict() for menu in menus]), 200


@app.route('/menu_items', methods=['GET'])
@jwt_required()
def get_menu_items():
    items = MenuItem.query.all()
    return jsonify([item.to_dict() for item in items]), 200


@app.route('/menu_items/<int:id>', methods=['GET'])
@jwt_required()
def get_menu_item(id):
    item = MenuItem.query.get_or_404(id)
    return jsonify(item.to_dict())



@app.route('/menu-items/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_menu_item(id):
    item = MenuItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return '', 204


@app.route('/menu-items', methods=['POST'])
@jwt_required()
def create_menu_item():
    data = request.get_json()
    new_item = MenuItem(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        available=data['available'],
        image_url=data.get('image_url'),
        menu_id=data['menu_id']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201



@app.route("/orders/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_orders_by_user(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    return jsonify([order.to_dict() for order in orders]), 200


@app.route('/order_items', methods=['POST'])
@jwt_required()
def create_order_item():
    data = request.get_json()

    user_id = data.get('user_id')
    menu_item_id = data.get('menu_item_id')
    quantity = int(data.get('quantity', 1))  

    if not user_id or not menu_item_id:
        return jsonify({"error": "user_id and menu_item_id are required"}), 400

    menu_item = MenuItem.query.get(menu_item_id)
    if not menu_item:
        return jsonify({"error": "Menu item not found"}), 404

    price = menu_item.price

    new_order = Order(user_id=user_id, total=0)
    db.session.add(new_order)
    db.session.flush() 

    order_item = OrderItem(
        order_id=new_order.id,
        menu_item_id=menu_item_id,
        quantity=quantity,
        price=price
    )
    db.session.add(order_item)

    new_order.total = quantity * price  

    db.session.commit()

    return jsonify(order_item.to_dict()), 201




@app.route("/reservations", methods=["POST"])
@jwt_required()
def create_reservation():
    data = request.get_json()
    try:
        user_id = data.get("user_id")
        guest_size = data.get("guest_size")
        reservation_time_str = data.get("reservation_time")

        if not (user_id and guest_size and reservation_time_str):
            return jsonify({"error": "Missing fields"}), 400

       
        try:
            reservation_time = datetime.fromisoformat(reservation_time_str)
        except ValueError:
            return jsonify({"error": "Invalid reservation_time format (use ISO 8601)"}), 422

        reservation = Reservation(
            user_id=int(user_id),
            guest_size=int(guest_size),
            reservation_time=reservation_time
        )
        db.session.add(reservation)
        db.session.commit()

        return jsonify({
            "id": reservation.id,
            "user_id": reservation.user_id,
            "guest_size": reservation.guest_size,
            "reservation_time": reservation.reservation_time.isoformat(),
            "created_at": reservation.created_at.isoformat()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reservations/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_reservations_by_user(user_id):
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    return jsonify([r.to_dict() for r in reservations]), 200




@app.route("/reviews", methods=["POST"])
@jwt_required()
def create_review():
    data = request.get_json()
    try:
        user_id = data.get("user_id")
        menu_item_id = data.get("menu_item_id")
        rating = data.get("rating")
        comment = data.get("comment", "")

        if not (user_id and rating):
            return jsonify({"error": "Missing required fields"}), 400

        review = Review(
            user_id=user_id,
            menu_item_id=menu_item_id,
            rating=rating,
            comment=comment,
        )
        db.session.add(review)
        db.session.commit()

        return jsonify({
            "id": review.id,
            "user_id": review.user_id,
            "menu_item_id": review.menu_item_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/reviews/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_reviews_by_user(user_id):
    reviews = Review.query.filter_by(user_id=user_id).all()
    return jsonify([r.to_dict() for r in reviews]), 200




@app.route('/orders', methods=['GET'])
@jwt_required()
def get_all_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders]), 200

@app.route('/reservations', methods=['GET'])
@jwt_required()
def get_all_reservations():
    reservations = Reservation.query.all()
    return jsonify([res.to_dict() for res in reservations]), 200

@app.route('/reviews', methods=['GET'])
@jwt_required()
def get_all_reviews():
    reviews = Review.query.all()
    return jsonify([rev.to_dict() for rev in reviews]), 200



@app.route("/users", methods=["GET"])
@jwt_required()
def get_all_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


@app.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        
        Review.query.filter_by(user_id=user.id).delete()

        
        Reservation.query.filter_by(user_id=user.id).delete()

       
        orders = Order.query.filter_by(user_id=user.id).all()
        for order in orders:
            OrderItem.query.filter_by(order_id=order.id).delete()
        Order.query.filter_by(user_id=user.id).delete()

       
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": f"User '{user.name}' deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete user", "details": str(e)}), 500



@app.route("/schedules", methods=["GET"])
@jwt_required()
def get_schedules():
    schedules = Schedule.query.all()
    return jsonify([s.to_dict() for s in schedules]), 200


@app.route("/schedules", methods=["POST"])
@jwt_required()
def create_schedule():
    data = request.get_json()
    try:
       
        date_obj = datetime.strptime(data["date"], "%Y-%m-%d").date()
        start_time_obj = datetime.strptime(data["start_time"], "%H:%M").time()
        end_time_obj = datetime.strptime(data["end_time"], "%H:%M").time()

        schedule = Schedule(
            staff_id=int(data["staff_id"]),
            date=date_obj,
            start_time=start_time_obj,
            end_time=end_time_obj,
            tasks=data["tasks"],
            is_completed=bool(data.get("is_completed", False))
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify(schedule.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400



@app.route("/schedules/<int:id>", methods=["PATCH"])
@jwt_required()
def update_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    data = request.get_json()

    try:
        if "staff_id" in data:
            schedule.staff_id = data["staff_id"]

        if "date" in data:
            schedule.date = datetime.strptime(data["date"], "%Y-%m-%d").date()

        if "start_time" in data:
            schedule.start_time = datetime.strptime(data["start_time"], "%H:%M").time()

        if "end_time" in data:
            schedule.end_time = datetime.strptime(data["end_time"], "%H:%M").time()

        if "tasks" in data:
            schedule.tasks = data["tasks"]

        if "is_completed" in data:
            schedule.is_completed = data["is_completed"]

        db.session.commit()
        return jsonify(schedule.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

@app.route("/schedules/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_schedule(id):
    schedule = Schedule.query.get_or_404(id)

    try:
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({"message": "Schedule deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
