from models import Base, session, engine, Brands, Products
from datetime import datetime, date
import time
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
            # if the produce exists, need to check if the updated date is greater than the existing - if it is, then we need to update the fields that have changed (all but product_name or just the ones that don't match?)
            if product_exists == None:
                name=row['product_name']
                price_str=row['product_price']
                price=clean_price(price_str)
                quantity=row['product_quantity']

                date_str=row['date_updated']
                updated_date=clean_date(date_str)
                
                brand_exists = session.query(Brands).filter(Brands.brand_name==row['brand_name']).one_or_none()
                if brand_exists:
                    brand_id=brand_exists.brand_id
                else:
                    #what should happen if a brand isn't in the brand table but is listed on the inventory list? do you update the brand table and come back?
                    print(brand_exists)
            
                new_product = Products(product_name=name, product_price=price, product_quantity=quantity, date_updated=updated_date,brand_id=brand_id)
                session.add(new_product)                

        session.commit()

def format_date(date_obj):
    print(date_obj)

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
            name = input('>> Enter the product name:  ')
            quantity = input('>> Enter the quantity:  ')
            price = input('>> Enter the price (ex. 5.99):  ')
            brand = input('>> Enter the brand of the product:  ')

        elif choice == 'A':
            # view analysis
            # most expensive item = sort by price highest to lowest and return the first product?
            # least expensive item = sort by price lowest to highest and return the first product?
            # most common brand = which brand has the most products in the db 
            print('product analysis')
        elif choice == 'B':
            current_date = date.today()
            print(current_date)
            with open(f'backup_{current_date}.csv', 'w', newline='') as csvfile:
                products = session.query(Products)
                field_names = ['product_name', 'product_price', 'product_quantity', 'date_updated', 'brand_name']
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writeheader()
                
                for product in products:
                    #formatted_date = format_date(product['date_updated'])
                    formatted_price = format_price(product.product_price)
                    brand = session.query(Brands).filter(Brands.brand_id==product.brand_id).one_or_none()

                    writer.writerow({'product_name': product.product_name, 'product_price': formatted_price, 'product_quantity': product.product_quantity, 'date_updated': product.date_updated, 'brand_name': brand.brand_name})
        else:
            print('\nGoodbye\n')
            app_running = False

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    seed_brands()
    seed_products()
    app()