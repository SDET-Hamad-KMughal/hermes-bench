from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Product

def seed_database():
    """Populate the database with baseline target records for benchmarking."""
    app = create_app()
    
    print("[*] Accessing app context for database seeding...")
    with app.app_context():
        # Clear existing entries to prevent primary key constraint conflicts
        db.session.query(Product).delete()
        db.session.query(User).delete()
        
        print("[*] Seeding default test user accounts...")
        admin_user = User(
            username="test_buyer",
            email="buyer@hermesbench.org",
            password_hash=generate_password_hash("password123"),
            balance=100.0  # Base balance to test decrement logic
        )
        db.session.add(admin_user)
        
        print("[*] Seeding default retail product inventory catalog...")
        sample_products = [
            Product(name="Research Notebook", description="Premium academic developer logbook.", price=15.0, stock=20),
            Product(name="Mechanical Keyboard", description="Compact 65% linear switch setup.", price=75.0, stock=5),
            Product(name="Coffee Mug", description="Thermal insulated container.", price=10.0, stock=50),
            Product(name="Fuzzing Guide", description="Advanced mutation testing handbook.", price=45.0, stock=2)
        ]
        
        db.session.add_all(sample_products)
        db.session.commit()
        print("[+] Database seeding complete! Target environment is ready.")

if __name__ == '__main__':
    seed_database()