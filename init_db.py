from app import create_app, db
from app.models import User, Product, CartItem

def initialize_database():
    """Build the physical database file and structures within the app context."""
    app = create_app()
    
    print("[*] Initializing database engine context...")
    with app.app_context():
        # Drop tables if they exist to guarantee a clean state
        db.drop_all()
        
        print("[*] Generating relational table structures (users, products, cart_items)...")
        db.create_all()
        
        print("[+] HERMES-Bench database schemas successfully created!")

if __name__ == '__main__':
    initialize_database()