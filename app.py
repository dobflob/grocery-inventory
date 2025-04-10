from models import Base, session, engine, Brands, Products
from datetime import datetime, date
from sqlalchemy import select, func
import time
import csv

#TODO: make a function to add a product. use this function in the seed_products function as well as when the user opts to add a new product

#TODO: make a function to add a brand. use this function everywhere we check to see if the brand exists and it doesn't currently.

#TODO: make a function to edit a product's information. Use this function within 'view' product where users can update the product their viewing as well as in the seed_products function when a product name is found that's already in the db but the date_updated is more recent, so we need to update the info in the db.

#TODO: move logic our of the app() function to ensure separation of concerns

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
                name=row['brand_name']
                
                new_brand = Brands(brand_name=name)
                session.add(new_brand)

    session.commit()


def seed_products():
    with open('inventory.csv') as csvfile:
        data = csv.DictReader(csvfile)

        for row in data:
            product_exists = session.query(Products).filter(Products.product_name==row['product_name']).one_or_none()
            # if the product exists, need to check if the updated date is greater than the existing - if it is, then we need to update the fields that have changed (all but product_name or just the ones that don't match?)
            if product_exists:
                row_date = clean_date(row['date_updated'])
                if row_date > product_exists.date_updated:
                    price_str=row['product_price']
                    product_exists.product_price=clean_price(price_str)
                    product_exists.product_quantity=row['product_quantity']
                    date_str=row['date_updated']
                    product_exists.date_updated=clean_date(date_str)

                    brand_exists = session.query(Brands).filter(Brands.brand_name==row['brand_name']).one_or_none()
                    if brand_exists:
                        product_exists.brand_id = brand_exists.brand_id
                    else:
                        new_brand = Brands(brand_name=row['brand_name'])
                        session.add(new_brand)
                        session.commit()
                        product_exists.brand_id = new_brand.brand_id

                    session.commit()

            elif product_exists == None:
                name=row['product_name']
                price_str=row['product_price']
                price=clean_price(price_str)
                quantity=row['product_quantity']

                date_str=row['date_updated']
                updated_date=clean_date(date_str)
                
                brand_exists = session.query(Brands).filter(Brands.brand_name==row['brand_name']).one_or_none()
                if brand_exists:
                    brand_id = brand_exists.brand_id
                else:
                    new_brand = Brands(brand_name=row['brand_name'])
                    session.add(new_brand)
                    session.commit()
                    brand_id = new_brand.brand_id

                new_product = Products(product_name=name, product_price=price, product_quantity=quantity, date_updated=updated_date,brand_id=brand_id)
                session.add(new_product)

        session.commit()

def format_date(date_obj):
    date_str = date_obj.strftime('%m/%d/%Y')
    return date_str

def format_price(price_int):
    price_float = float(price_int/100)
    formatted_price = f'{price_float:.2f}'
    return f'${formatted_price}'

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
            # TODO: maybe create a function to validate the selection so that this main app function isn't giant when the app is finished?
            # TODO: add a function that displays the product information in a way that's more visually appealing and readable

            # view product's inventory - get product by Id; if the Id cannot be converted to an integer, display an error message and re-prompt the user for a valid id. 
            id_error = True
            while id_error:
                try:
                    selected_id = int(input('\n>> Enter the id of the product you want to view:  '))
                except ValueError:
                    print('''
                          
********* ID ERROR *********
                    
Product id must be a number.
Please try again.
                    
****************************

    ''')
                else:
                    id_error = False
                    selected_product = session.query(Products).filter(Products.product_id==selected_id).one_or_none()
                    
                    if selected_product:
                        print(selected_product)
                    else:
                        print(f'''

NOT FOUND
---------                              
Product with the id: {selected_id} not found. 
Please try again.

''')
                        # wait 1.5 seconds before displaying the main menu again
                        time.sleep(1.5) 
        elif choice == 'N':
            # add new product

            product_name = input('\n>> Enter the product name:  ')
            quantity_error = True
            while quantity_error:
                try:
                    quantity = int(input('\n>> Enter the quantity:  '))
                    if quantity:
                        quantity_error = False
                except ValueError:
                    print('''
                          
******** QUANTITY ERROR ********
                    
Quantity must be a whole number.
Please try again.
                    
********************************

    ''')

            price_error = True
            while price_error:
                try:
                    price = input('\n>> Enter the price (ex. 5.99):  ')
                    cleaned_price = clean_price(price)
                    if clean_price:
                        price_error = False
                except ValueError:
                    print('''
                          
********** PRICE ERROR ************
                    
Price must be a number. (e.g. 5.99)
Please try again.
                    
***********************************

    ''')

            name = input('\n>> Enter the brand of the product:  ')
            brand_exists = session.query(Brands).filter(Brands.brand_name==name).one_or_none()
            if brand_exists:
                brand_id = brand_exists.brand_id
            else:
                new_brand=Brands(brand_name=name)
                session.add(new_brand)
                session.commit()
                brand_id=new_brand.brand_id
                print(f'brand: {brand_id}')
            updated_date = date.today()

            new_product = Products(product_name=product_name, product_price=cleaned_price, product_quantity=quantity, date_updated=updated_date,brand_id=brand_id)
            
            session.add(new_product)
            session.commit()
            
            time.sleep(1.5)
            

        elif choice == 'A':
            # view analysis
            # most expensive item = sort by price highest to lowest and return the first product?
            product_list = session.query(Products)
            most_expensive = product_list.order_by(Products.product_price.desc()).first()
            least_expensive = product_list.order_by(Products.product_price).first()
            brands = product_list.group_by(Products.brand_id).all()
            print(f'''
PRODUCT ANALYSIS
----------------
Most Expensive Item: {most_expensive.product_name} (${most_expensive.product_price/100})

Least Expensive Item: {least_expensive.product_name} (${least_expensive.product_price/100})
                  
Most Common Brand: {brands}

''')
            
            # least expensive item = sort by price lowest to highest and return the first product?
            # most common brand = which brand has the most products in the db 
        elif choice == 'B':
            current_date = date.today()

            with open(f'backup_{current_date}.csv', 'w', newline='') as csvfile:
                products = session.query(Products)
                field_names = ['product_name', 'product_price', 'product_quantity', 'date_updated', 'brand_name']
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writeheader()
                
                for product in products:
                    formatted_date = format_date(product.date_updated)
                    formatted_price = format_price(product.product_price)
                    brand = session.query(Brands).filter(Brands.brand_id==product.brand_id).one_or_none()

                    writer.writerow({'product_name': product.product_name, 'product_price': formatted_price, 'product_quantity': product.product_quantity, 'date_updated': formatted_date, 'brand_name': brand.brand_name})
            print(f'\nBackup successfully created: backup_{current_date}.csv\n')
            # wait 1.5 seconds before displaying the main menu again
            time.sleep(1.5) 
        else:
            print('\nGoodbye\n')
            return

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    seed_brands()
    seed_products()
    app()