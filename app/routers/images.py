from dotenv import load_dotenv

load_dotenv()
from fastapi import APIRouter, status, HTTPException, UploadFile, Depends, Body
from mysql.connector import pooling
import os
import boto3
from app.oauth2 import get_current_user
from itertools import zip_longest
from app.schemas import Metadatas

router = APIRouter(prefix="/e-commerce/product-images", tags=["Product Images"])

connection_pool = pooling.MySQLConnectionPool(
    pool_name="ImagePool",
    pool_size=3,
    host=os.environ["DB_HOST"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
)

session = boto3.Session(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["AWS_REGION_NAME"],
)

s3 = session.client("s3")
bucket_name = "moksh-ecommerce-bucket"


@router.put("/upload/product-images/{product_id}", status_code=status.HTTP_201_CREATED)
async def upload_images(
    images: list[UploadFile],
    product_id: int,
    data: Metadatas,
    current_user=Depends(get_current_user),
):
    if images and len(images) <= 5:
        with connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE ecommerce;")
                cursor.execute("SELECT * FROM products where id = %s", (product_id,))
                product_info = cursor.fetchone()
                user_name = product_info[4]

                if product_info and (user_name == current_user.username):
                    cursor.execute(
                        """
                                   CREATE TABLE IF NOT EXISTS images (
                                    image_id INT PRIMARY KEY AUTO_INCREMENT, 
                                    product_id INT NOT NULL,
                                    base_path VARCHAR(255) NOT NULL,
                                    metadata VARCHAR(255),
                                    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
                                    );
                                   """
                    )
                    users_directories = []
                    objects = s3.list_objects(Bucket=bucket_name)
                    for obj in objects["Contents"]:
                        if obj["Size"] == 0:
                            users_directories.append(users_directories)
                    if current_user.username not in users_directories:
                        s3.put_object(
                            Bucket=bucket_name,
                            Key=f"{current_user.username}/{str(product_id)}/",
                        )
                    
                    if data and len(data.metadata) <= len(images):  # type: ignore
                        for image, element in zip_longest(images, data.metadata):  # type: ignore
                            if image.filename.endswith((".jpg", ".png", ".jpeg", ".gif", ".webp")):
                                cursor.execute(
                                    "INSERT INTO images (product_id, base_path, metadata) VALUES (%s,%s,%s)",
                                    (product_id, image.filename, element),
                                )
                                response = s3.put_object(
                                        Body=image.file,
                                        Bucket=bucket_name,
                                        Key=f"{current_user.username}/{str(product_id)}/{image.filename}",
                                        ContentType=image.content_type,
                                        Metadata={"metadata": element}
                                    )
                                if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                                    return {
                                        "message": "Image couldn't be uploaded",
                                        "status": response["ResponseMetadata"][
                                            "HTTPStatusCode"
                                        ],
                                    }
                            connection.commit()

                        return {
                            "message": "Images have uploaded succesfully",
                            "status": status.HTTP_201_CREATED,
                        }

                    if not data:
                        for image in images:
                            if image.filename.endswith((".jpg", ".png", ".jpeg", ".gif", ".webp")): # type: ignore
                                cursor.execute(
                                    "INSERT INTO images (product_id, base_path, metadata) VALUES (%s,%s,%s)",
                                    (product_id, image.filename, None),
                                )
                                response = s3.put_object(
                                    s3.put_object(
                                    Body=image.file,
                                    Bucket=bucket_name,
                                    Key=f"{current_user.username}/{str(product_id)}/{image.filename}",
                                    ContentType=image.content_type,
                                    )
                                )
                                if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                                    return {
                                    "message": "Image couldn't be uploaded",
                                    "status": response["ResponseMetadata"][
                                        "HTTPStatusCode"
                                    ],
                                }
                            connection.commit()

                        return {
                            "message": "Images have uploaded succesfully",
                            "status": status.HTTP_201_CREATED,
                        }
                if not product_info:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="No product found"
                    )

                if user_name != current_user.username:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You are unauthorized",
                    )

    if data and len(data.metadata) > len(images):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="metadata cannot exceed the number of images",
        )

    if len(images) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 photos of a product can be uploaded",
        )
