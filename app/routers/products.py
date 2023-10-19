from fastapi import APIRouter, Depends, HTTPException, status
from mysql.connector import pooling
from app.schemas import Product, ShowMultipleProducts
from app.oauth2 import get_current_user
import os

router = APIRouter(prefix="/e-commerce/products", tags=["Products"])

connection_pool = pooling.MySQLConnectionPool(pool_name="ProductPool", pool_size=3, host = os.getenv("DB_HOST"), user = os.getenv("DB_USER"), password = os.getenv("DB_PASSWORD"))

@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=Product)
async def upload_products(product: Product, current_user =  Depends(get_current_user)):
    try:
        with connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE ecommerce;")
                cursor.execute("""CREATE TABLE IF NOT EXISTS products (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(50) NOT NULL,
                    price FLOAT NOT NULL,
                    description VARCHAR(255),
                    username VARCHAR(50) NOT NULL,
                    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
                    );
                    """)
                cursor.execute("INSERT INTO products (name, price, description, username) VALUES (%s, %s, %s, %s);", (product.Name, product.Price, product.Description, current_user.username))
                connection.commit()
                return product
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/get/{username}", status_code=status.HTTP_200_OK, response_model=ShowMultipleProducts)
async def get_user_products(username: str, current_user = Depends(get_current_user)):
    try:
        user_products = []
        with connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE ecommerce;")
                if username != current_user.username:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Not authorized to make changes")
                cursor.execute("SELECT name, price, description, username FROM products WHERE username = %s", (current_user.username,))
                products_data = cursor.fetchall()
                if products_data:
                    for product_data in products_data:
                        product_dict = {
                            "Name": product_data[0],
                            "Price": product_data[1],
                            "Description": product_data[2],
                            "username": product_data[3]
                        }
                        user_products.append(product_dict)
                        
                    if user_products:
                        return {"products":user_products}
                    
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/get", status_code=status.HTTP_200_OK, response_model=ShowMultipleProducts)
async def get_all_products():
    try:
        products = []
        with connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE ecommerce;")
                cursor.execute("SELECT name, price, description, username FROM products;")
                all_products = cursor.fetchall()
                if all_products:
                    for product_data in all_products:
                        product_dict = {
                            "Name": product_data[0],
                            "Price": product_data[1],
                            "Description": product_data[2],
                            "username": product_data[3]
                        }
                        
                        products.append(product_dict)
                
                    if products:
                        return {"products": products}
                
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products listed")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.put("/edit/{id}", status_code=status.HTTP_202_ACCEPTED)
async def edit_product(id: int, product: Product, current_user = Depends(get_current_user)):
    try:
        with connection_pool.get_connection() as connection:
            with connection.cursor(buffered = True) as cursor:
                cursor.execute("USE ecommerce;")
                cursor.execute("UPDATE products SET name = %s, price = %s, description = %s WHERE id = %s", (product.Name, product.Price, product.Description, id)) 
                connection.commit()
                cursor.execute("SELECT name, price, description FROM products WHERE username = %s", (current_user.username,))
                updated_product = cursor.fetchone()
                if not updated_product:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No product found")
                
                updated_product_dict = {
                    "Name": updated_product[0],
                    "Price": updated_product[1],
                    "Description": updated_product[2]
                }
                
                return updated_product_dict
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.delete("/remove/{id}", status_code=status.HTTP_200_OK)
async def remove_product(id:int, current_user = Depends(get_current_user)):
    with connection_pool.get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("USE ecommerce;")
            cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
            product = cursor.fetchone()
            if product:
                cursor.execute("DELETE FROM products WHERE id = %s", (id,))
                connection.commit()
                return {"message": f"Product {product[1]} is deleted succesfully"}
             
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No product found")
                

       