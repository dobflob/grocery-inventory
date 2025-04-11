from models import Base, session, engine, Brands, Products
from datetime import datetime, date
from sqlalchemy import select, func
import time
import csv

#TODO: make a function to add a brand. use this function everywhere we check to see if the brand exists and it doesn't currently.

#TODO: make a function to edit a product's information. Use this function within 'view' product where users can update the product their viewing as well as in the seed_products function when a product name is found that's already in the db but the date_updated is more recent, so we need to update the info in the db.

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
            # if the product exists, need to check if the updated date is greater than the existing - if it is, then we need to update the fields that have changed (all but product_name or just the ones that don't match?)
            if product_exists:
                row_date_obj = clean_date(row['date_updated'])
                if row_date_obj > product_exists.date_updated:
                    row['product_price'] = clean_price(row['product_price'])
                    row['date_updated'] = row_date_obj
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

# compares each field for the current product record and the updated product record. For any field that doesn't match, that field will be updated for the existing product record.
def update_product_info(existing_product_name, updated_product):
    existing_product = session.query(Products).filter(Products.product_name==existing_product_name).first()

    existing_product.date_updated = updated_product['date_updated']

    if existing_product.product_name != updated_product['product_name']:
        existing_product.product_name = updated_product['product_name']
    if existing_product.product_price != updated_product['product_price']:
        existing_product.product_price = updated_product['product_price']
    if existing_product.product_quantity != updated_product['product_quantity']:
        existing_product.product_quantity = updated_product['product_quantity']
    if existing_product_name != updated_product['brand_name']:
        brand_exists = session.query(Brands).filter(Brands.brand_name==updated_product['brand_name']).one_or_none()
        if brand_exists:
            existing_product.brand_id = brand_exists.brand_id
        else:
            add_brand(updated_product['brand_name'])

def add_brand(name):
    new_brand = Brands(brand_name=name)
    session.add(new_brand)

# If product info is passed to add_product, it will add that information to the database; if not, it will ask the user for product_info via a series of inputs. once all info is entered, it will add the new product to the db.
# TODO: feels like checking if a brand exists could be it's own function since it has to happen a few times.... think this over
# TODO: make a function that prints an error that takes in the field where the error is occuring, then uses conditional logic to pick to corresponding error to print
def add_product(product_info = ()):

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
        name=input('\n>> Enter the product name:  ')

        price_error = True
        while price_error:
            try:
                price = clean_price((input('\n>> Enter the price (ex: 5.99):  ')))
            except ValueError:
                print('Price Value Error...')
            else:
                price_error = False
        
        quantity_error = True
        while quantity_error:
            try:
                quantity = int(input('\n>> Enter product quantity (ex: 10):  '))
            except ValueError:
                print('Quantity Value Error...')
            else:
                quantity_error = False
        updated_date = date.today()
        brand_name = input("\n>> Enter the product's brand (ex: Kraft):  ")

        brand_exists = session.query(Brands).filter(Brands.brand_name==brand_name).one_or_none()
        if brand_exists:
            brand_id = brand_exists.brand_id
        else:
            add_brand(brand_name)
            session.commit()
            new_brand = session.query(Brands).filter(Brands.brand_name==brand_name).first()
            brand_id = new_brand.brand_id

        entered_product_info = {'product_name': name, 'product_price': price, 'product_quantity': quantity, 'date_updated': updated_date, 'brand_name': brand_name}
        product_exists = session.query(Products).filter(Products.product_name==name).one_or_none()
        if product_exists:
            update_product_info(product_exists.product_name, entered_product_info)
            session.commit()
        else:
            new_product = Products(product_name=name, product_price=price, product_quantity=quantity, date_updated=date_updated, brand_id=brand_id)
            session.add(new_product)
            session.commit()

def analyze_products():
    product_list = session.query(Products)
    most_expensive = product_list.order_by(Products.product_price.desc()).first()
    least_expensive = product_list.order_by(Products.product_price).first()
    brands_by_count = session.query(Products.brand_id,func.count(Products.brand_id)).group_by(Products.brand_id).all()
    most_common=brands_by_count[0]
    for brand in brands_by_count:
        if brand[1] > most_common[1]:
            most_common=brand

    most_common_brand=session.query(Brands.brand_name).filter(Brands.brand_id==most_common[0])

    print(f'''
PRODUCT ANALYSIS
----------------
Most Expensive Item: {most_expensive.product_name} (${most_expensive.product_price/100})
Least Expensive Item: {least_expensive.product_name} (${least_expensive.product_price/100})         
Most Common Brand: {most_common_brand[0][0]}

''')

def format_date_str(date_obj):
    date_str = date_obj.strftime('%m/%d/%Y')
    return date_str

def format_price_str(price_int):
    price_float = float(price_int/100)
    price_str = f'${price_float:.2f}'
    return price_str

def display_product():
    id_error = True
    while id_error:
        try:
            entered_id = int(input('\n>> Enter the id of the product you want to view:  '))
        except ValueError:
            print('Id Value Error...')
        else:
            id_error = False
            selected_product = session.query(Products).filter(Products.product_id==entered_id).one_or_none()
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
                # call display_error function once created passing in argument so correct message is displayed
                print(f"""
NOT FOUND
---------                              
Product with the id: {entered_id} not found. 
Please try again.

""")

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
            display_product()
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