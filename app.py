from models import Base, session, engine, Brands, Products
from datetime import datetime
import csv

# Format the date string into a datetime object in the format 'mm/dd/yyyy'
def clean_date(date_str):
    date = datetime.strptime(date_str, '%m/%d/%Y')
    return date

# Format the price string into an int 
def clean_price(price_str):
    price_str = price_str[1:]
    price_float = float(price_str)
    return int(price_float * 100)

def seed_brands():
    with open('brands.csv') as csvfile:
        data = csv.DictReader(csvfile)
        
        for row in data:
            brand_exists = session.query(Brands).filter(Brands.brand_name==row['brand_name']).one_or_none()
            
            if brand_exists == None:
                name=row['brand_name']
                
                new_brand = Brands(brand_name=name)
                session.add(new_brand)

    session.commit()


def seed_products():
    with open('inventory.csv') as csvfile:
        data = csv.DictReader(csvfile)

        for row in data:
            product_exists = session.query(Products).filter(Products.product_name==row['product_name']).one_or_none()

            if product_exists == None:
                name=row['product_name']
                price_str=row['product_price']
                price=clean_price(price_str)
                quantity=row['product_quantity']

                date_str=row['date_updated']
                updated_date=clean_date(date_str)
                
                brand_exists = session.query(Brands).filter(Brands.brand_name==row['brand_name']).one_or_none()
                if brand_exists == None:
                    print(brand_exists)
                else:
                    brand_id=brand_exists.brand_id

                
            
                new_product = Products(product_name=name, product_price=price, product_quantity=quantity, date_updated=updated_date, brand_id=brand_id)
                session.add(new_product)

        session.commit()

def menu():
    while True:
        print('''
GROCERY INVENTORY MAIN MENU
---------------------------
V - View Product
N - Add Product
A - View Analysis
B - Backup the Database
Q - Quit
''')
        choice = input('>> What would you like to do?  ')
        choice = choice.upper()
        if choice in ['V', 'N', 'A', 'B', 'Q']:
            return choice
        else:
            input('''
Please choose an option from the menu (V, N, A, B, Q).
Press enter to make a selection.
''')

def app():
    app_running = True
    while app_running:
        choice = menu()

        if choice == 'V':
            # view product's inventory
            print('\nselected: View Product Inventory\n')
        elif choice == 'N':
            # add new product
            print('\nselected: Add Product\n')
        elif choice == 'A':
            # view analysis
            print('\nselected: View Analysis\n')
        elif choice == 'B':
            print('\nselected: Backup Database\n')
        else:
            print('\nGoodbye\n')
            app_running = False

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    seed_brands()
    seed_products()
    app()