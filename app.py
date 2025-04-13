from models import Base, session, engine, Brands, Products
from datetime import datetime, date
from sqlalchemy import func
import time
import csv

# Format the date string into a datetime object in the format 'mm/dd/yyyy'
def clean_date(date_str):
    date = datetime.strptime(date_str, '%m/%d/%Y')
    return date.date()

# Format the price string into an int 
def clean_price(price_str):
    if price_str[0] == '$':
        price_str = price_str[1:]
    price_float = float(price_str)
    return int(price_float * 100)

def seed_brands():
    with open('brands.csv') as csvfile:
        data = csv.DictReader(csvfile)
        
        for row in data:
            brand_exists = session.query(Brands).filter(Brands.brand_name==row['brand_name']).one_or_none()
            
            if brand_exists == None:
                add_brand(row['brand_name'])

        session.commit()

def seed_products():
    with open('inventory.csv') as csvfile:
        data = csv.DictReader(csvfile)

        for row in data:
            product_exists = session.query(Products).filter(Products.product_name==row['product_name']).one_or_none()
            if product_exists:
                brand = session.query(Brands).filter(Brands.brand_id==product_exists.brand_id).first()
                row['brand_id'] = brand.brand_id
                row['date_updated'] = clean_date(row['date_updated'])
                row['product_price'] = clean_price(row['product_price'])
                update_product_info(product_exists.product_name,row)

            elif product_exists == None:
                add_product(row)

        session.commit()

def create_backup_csv():
    current_date = date.today()

    with open(f'backup_{current_date}.csv', 'w', newline='') as csvfile:
        products = session.query(Products)
        field_names = ['product_name', 'product_price', 'product_quantity', 'date_updated', 'brand_name']
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        
        for product in products:
            date_str = format_date_str(product.date_updated)
            price_str = format_price_str(product.product_price)
            brand = session.query(Brands).filter(Brands.brand_id==product.brand_id).one_or_none()

            writer.writerow({'product_name': product.product_name, 'product_price': price_str, 'product_quantity': product.product_quantity, 'date_updated': date_str, 'brand_name': brand.brand_name})
    print(f'\nBackup successfully created: backup_{current_date}.csv\n')

# Takes in the field being modified (or object being searched for) when the error occured and displays an appropriate message
def display_error(error_field):
    if error_field in ('price', 'quantity', 'date', 'id'):
        error_string = error_field + ' error'
        print(f'''
*** {error_string.upper()} ***

The value you entered for {error_field} is invalid.
Please try again.

''')
    elif error_field in ('product', 'brand'):
        error_string = error_field + ' not found'
        print(f'''
*** {error_string.upper()} ***

The {error_field.capitalize()} you entered could not be found.
Please try again.

''')

# Handles getting input from the user, cleaning the data, and returns a db ready product record
def enter_product_info():
    name=input('\n>> Enter the product name:  ')

    price_error = True
    while price_error:
        try:
            price = clean_price((input('\n>> Enter the price (ex: 5.99):  ')))
        except ValueError:
            display_error('price')
        else:
            price_error = False
    
    quantity_error = True
    while quantity_error:
        try:
            quantity = int(input('\n>> Enter product quantity (ex: 10):  '))
        except ValueError:
            display_error('quantity')
        else:
            quantity_error = False

    date_error = True
    while date_error:
        try:
            updated_date = clean_date(input('\n>> Enter the last updated date of the product (ex: 4/12/2025):  '))
        except ValueError:
            display_error('date')
        else:
            date_error = False

    brand_name = input("\n>> Enter the product's brand (ex: Kraft):  ")

    brand_exists = session.query(Brands).filter(Brands.brand_name==brand_name).one_or_none()
    if brand_exists:
        brand_id = brand_exists.brand_id
    else:
        add_brand(brand_name)
        session.commit()
        new_brand = session.query(Brands).filter(Brands.brand_name==brand_name).first()
        brand_id = new_brand.brand_id

    return {'product_name': name, 'product_price': price, 'product_quantity': quantity, 'date_updated': updated_date, 'brand_id': brand_id}

# compares each field for the current product record and the updated product record. For any field that doesn't match, that field will be updated for the existing product record.
def update_product_info(existing_product_name, updated_product_info = {}):
    existing_product = session.query(Products).filter(Products.product_name==existing_product_name).first()
    
    if not updated_product_info:
        updated_product_info = enter_product_info()

    if updated_product_info['date_updated'] > existing_product.date_updated:
        existing_product.date_updated = updated_product_info['date_updated']

        if existing_product.product_name != updated_product_info['product_name']:
            existing_product.product_name = updated_product_info['product_name']

        if existing_product.product_price != updated_product_info['product_price']:
            existing_product.product_price = updated_product_info['product_price']

        if existing_product.product_quantity != updated_product_info['product_quantity']:
            existing_product.product_quantity = updated_product_info['product_quantity']
        
        if existing_product.brand_id != updated_product_info['brand_id']:
            brand_exists = session.query(Brands).filter(Brands.brand_id==updated_product_info['brand_id']).one_or_none()
            if brand_exists:
                existing_product.brand_id = brand_exists.brand_id
            else:
                add_brand(updated_product_info['brand_name'])
                new_brand = session.query(Brands).filter(Brands.brand_name==existing_product_name).first()
                existing_product.brand_id = new_brand.brand_id

def add_brand(name):
    new_brand = Brands(brand_name=name)
    session.add(new_brand)

def delete_product(product):
    name = product.product_name
    name.capitalize()
    session.delete(product)
    session.commit()
    print(f'\n{name} was deleted.\n')

# If a product is passed in, it will add that information to the database
# If there is no product, it will collect the info from the user before adding to the db
def add_product(product_info = {}):

    if product_info:
        name=product_info['product_name']
        price=clean_price(product_info['product_price'])
        quantity=product_info['product_quantity']
        updated_date=clean_date(product_info['date_updated'])

        brand_exists = session.query(Brands).filter(Brands.brand_name==product_info['brand_name']).one_or_none()
        if brand_exists:
            brand_id = brand_exists.brand_id
        else:
            add_brand(product_info['brand_name'])
            new_brand = session.query(Brands).filter(Brands.brand_name==product_info['brand_name']).first()
            brand_id = new_brand.brand_id

        new_product = Products(product_name=name, product_price=price, product_quantity=quantity, date_updated=updated_date,brand_id=brand_id)
        session.add(new_product)
    else:
        product_info = enter_product_info()

        product_exists = session.query(Products).filter(Products.product_name==product_info['product_name']).one_or_none()
        if product_exists:
            update_product_info(product_exists.product_name, product_info)
            session.commit()
        else:
            new_product = Products(product_name=product_info['product_name'], product_price=product_info['product_price'], product_quantity=product_info['product_quantity'], date_updated=product_info['date_updated'], brand_id=product_info['brand_id'])
            session.add(new_product)
            session.commit()

#TODO: additional analysis points - maybe product with the highest quantity, product with the lowest quantity, most recently updated product, etc.
def analyze_products():
    product_list = session.query(Products)
    most_expensive = product_list.order_by(Products.product_price.desc()).first()
    least_expensive = product_list.order_by(Products.product_price).first()

    highest_quantity = product_list.order_by(Products.product_quantity.desc()).first()
    lowest_quantity = product_list.order_by(Products.product_quantity).first()

    most_recent_update = product_list.order_by(Products.date_updated.desc()).first()
    brands_by_count = session.query(Products.brand_id,func.count(Products.brand_id)).group_by(Products.brand_id).all()
    most_common=brands_by_count[0]
    for brand in brands_by_count:
        if brand[1] > most_common[1]:
            most_common=brand

    most_common_brand=session.query(Brands.brand_name).filter(Brands.brand_id==most_common[0])

    print(f'''
PRODUCT ANALYSIS
----------------
Most Expensive: {most_expensive.product_name} (${most_expensive.product_price/100})
Least Expensive: {least_expensive.product_name} (${least_expensive.product_price/100}) 

Highest Quantity: {highest_quantity.product_name} ({highest_quantity.product_quantity})
Lowest Quantity: {lowest_quantity.product_name} ({lowest_quantity.product_quantity})

Last Updated: {most_recent_update.product_name}
Most Common Brand: {most_common_brand[0][0]}

''')

def format_date_str(date_obj):
    date_str = date_obj.strftime('%m/%d/%Y')
    return date_str

def format_price_str(price_int):
    price_float = float(price_int/100)
    price_str = f'${price_float:.2f}'
    return price_str

def display_product(selected_product):
    if selected_product:
        brand_name = session.query(Brands.brand_name).filter(Brands.brand_id==selected_product.brand_id).first()
        print(f"""
PRODUCT DETAILS
---------------
Product: {selected_product.product_name}
Price: {format_price_str(selected_product.product_price)}
Quantity: {selected_product.product_quantity}
Last Updated: {format_date_str(selected_product.date_updated)}
Brand: {brand_name[0]}
""")
    elif selected_product == None:
        display_error('product')
                
def get_product():
    id_error = True
    while id_error:
        try:
            entered_id = int(input('\n>> Enter the product Id:  '))
        except ValueError:
            display_error('id')
        else:
            return session.query(Products).filter(Products.product_id==entered_id).one_or_none()

def product_menu():
    while True:
        print('''
PRODUCT MENU
------------
E - Edit Product
D - Delete Product
M - Main Menu
Q - Exit Application
''')
        choice = input('>>> What would you like to do?  ')
        choice = choice.upper()
        if choice in ['E', 'D', 'M', 'Q']:
            return choice
        else:
            input('''
Please choose an option from the menu (E, D, Q).
Press enter to make a selection.
''')

def menu():
    while True:
        print('''
GROCERY INVENTORY MAIN MENU
---------------------------
V - View Product
N - Add Product
A - View Analysis
B - Backup the Database
Q - Exit Application
''')
        choice = input('> What would you like to do?  ')
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
            selected_product = get_product()
            display_product(selected_product)
            if selected_product:
                product_choice = product_menu()

                if product_choice == 'E':
                    update_product_info(selected_product.product_name)
                    session.commit()
                elif product_choice == 'D':
                    delete_product(selected_product)
                elif product_choice == 'M':
                    continue
                elif product_choice == 'Q':
                    return
            time.sleep(1.5)
        elif choice == 'N':
            # add new product
            add_product()
            time.sleep(1.5)
        elif choice == 'A':
            # view analysis
            analyze_products()
            time.sleep(1.5)
        elif choice == 'B':
            create_backup_csv()
            time.sleep(1.5) 
        else:
            print('\nGoodbye\n')
            return

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    seed_brands()
    seed_products()
    app()