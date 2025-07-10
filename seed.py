from app import app, db
from models import Menu, MenuItem
from faker import Faker
import random

fake = Faker()

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Sample Menus ---
        menus = [
            Menu(name="Breakfast", description="Start your day with energy."),
            Menu(name="Lunch", description="Hearty meals for midday hunger."),
            Menu(name="Dinner", description="Delicious dishes to end your day."),
            Menu(name="Drinks", description="Refreshing beverages and hot drinks."),
            Menu(name="Desserts", description="Sweet treats and baked goods.")
        ]
        db.session.add_all(menus)
        db.session.commit()

        # --- Sample Items ---
        sample_items = {
            "Breakfast": [
                ("Pancakes", "Fluffy pancakes served with syrup and butter.", 600, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274119/pancakes_ow9ucn.jpg"),
                ("Omelette", "3-egg omelette with cheese, tomato and spinach.", 650, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274120/omelette_fj9zzf.jpg"),
                ("Avocado Toast", "Sourdough topped with smashed avocado and chili flakes.", 500, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274119/avocado_toast_tvgego.jpg"),
            ],
            "Lunch": [
                ("Grilled Chicken Sandwich", "Served with lettuce, tomato, and aioli.", 850, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274120/grilled_chicken_sandwich_siqate.jpg"),
                ("Caesar Salad", "Crisp romaine with croutons, parmesan, and Caesar dressing.", 730, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274119/caesar_salad_ti7is1.jpg"),
                ("Veggie Wrap", "Spinach wrap filled with hummus, cucumber, and roasted veggies.", 690, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274118/veggie_wrap_ajjiju.jpg"),
            ],
            "Dinner": [
                ("Steak Frites", "Grilled sirloin steak served with crispy fries.", 1500, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274119/steak_frites_fdgydc.jpg"),
                ("Salmon Teriyaki", "Pan-seared salmon glazed in teriyaki sauce.", 1350, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274119/salmon_teriyaki_qqv6jk.jpg"),
                ("Vegetable Stir Fry", "Seasonal veggies in garlic soy sauce over rice.", 1000, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274119/vegetable_stir_fry_l7g6g2.jpg"),
                ("Pizza", "Greasy flavor", 1200, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751191799/pizza_fjmt0z.jpg"),
            ],
            "Drinks": [
                ("Iced Latte", "Espresso with chilled milk over ice.", 400, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274120/iced_latte_fv2btx.jpg"),
                ("Smoothie", "Banana, mango, and spinach smoothie.", 450, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274119/smoothie_airuod.jpg"),
                ("Hot Chocolate", "Rich cocoa with whipped cream on top.", 300, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274120/hot_chocolate_cellu0.jpg"),
                
            ],
            "Desserts": [
                ("Chocolate Cake", "Decadent chocolate cake slice with ganache.", 500, "https://images.unsplash.com/photo-1578985545062-69928b1d9587"),
                ("Cheesecake", "Classic New York cheesecake with berry compote.", 550, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274118/cheesecake_a2erlo.jpg"),
                ("Ice Cream Sundae", "Vanilla ice cream with chocolate syrup and nuts.", 380, "https://res.cloudinary.com/dmbzl8jpm/image/upload/v1751274120/ice_cream_sundae_jwjb8i.jpg"),
            ]
        }

        for menu in menus:
            items = sample_items.get(menu.name, [])
            for name, description, price, image_url in items:
                menu_items = MenuItem(
                    name=name,
                    description=description,
                    price=price,
                    image_url=image_url,
                    available=random.choice([True, True, True, False]),  # 75% available
                    menu=menu
                )
                db.session.add(menu_items)

        db.session.commit()
        print("✅ Database seeded!")

if __name__ == "__main__":
    seed_data()
