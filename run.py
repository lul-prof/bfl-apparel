import os

import click
from app import create_app, db
from app.models import User, Product, Order, Cart

app = create_app()




def initialize_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if products table is empty
        if Product.query.count() == 0:
            print("⚙️ Populating products database...")
            
            sample_products = [
                Product(
                    name="BFL Signature Tee",
                    description="Premium 100% cotton t-shirt with logo",
                    price=29.99,
                    image="shirt1.jpg",
                    stock=100,
                    category="Shirts"
                ),
                Product(
                    name="BFL Performance Hoodie",
                    description="Athletic hoodie with moisture-wicking fabric",
                    price=59.99,
                    image="hoodie1.jpg",
                    stock=75,
                    category="Hoodies"
                ),
                Product(
                    name="BFL Classic Jeans",
                    description="Slim-fit denim jeans with stretch",
                    price=79.99,
                    image="jeans1.jpg",
                    stock=50,
                    category="Pants"
                )
            ]
            
            try:
                db.session.bulk_save_objects(sample_products)
                db.session.commit()
                print(f"✅ Successfully added {len(sample_products)} products")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error adding products: {str(e)}")

@app.cli.command('create-admin')
def create_admin():
    """Create an admin user"""
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    email = input("Enter admin email: ")
    
    user = User(username=username, email=email, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"Admin user {username} created successfully!")
    
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Product': Product, 'Order': Order, 'Cart': Cart}


if __name__ == '__main__':

    # Clear console for better visibility
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🚀 Starting BFL Apparel application...")
    initialize_database()
    app.run(debug=True)