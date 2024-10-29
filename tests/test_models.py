# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory
from random import randint, randrange, random

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_a_product(self):
        """It should read the product that corresponds to the given ID"""
        size = randint(10, 50)
        products = []

        # Randomly create various products
        for i in range(0, size):
            product = ProductFactory()
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)
            products.append(product)

        # Retrieve one random product
        search_index = randrange(0, size)
        search_product = products[search_index]

        # Find randomly goten product in db
        found = Product.find(search_product.id)
        self.assertEqual(found.id, search_product.id)
        self.assertEqual(found.name, search_product.name)
        self.assertEqual(found.description, search_product.description)
        self.assertEqual(found.price, search_product.price)

    def test_update_a_product(self):
        """It should update the product properties modified"""
        # Create product and set id on database
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        original_id = product.id

        # Update product description
        new_description = "Updated description"
        product.description = new_description
        product.update()

        # Fetch all products and check correct update
        products = Product.all()

        self.assertEqual(len(products), 1)

        updated_product = products[0]

        self.assertEqual(original_id, updated_product.id)
        self.assertEqual(new_description, updated_product.description)

    def test_update_without_id(self):
        """It should fail when trying to update a product that has no id"""
        product = ProductFactory()
        product.create()
        product.id = None
        self.assertIsNone(product.id)

        # Update product description
        new_description = "Updated description"
        product.description = new_description

        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should delete the product"""
        # Create product and set id on database
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        original_id = product.id

        # Check that the product is on the database
        products = Product.all()

        self.assertEqual(len(products), 1)

        product.delete()

        # Test that the database is empty after deletion
        self.assertEqual(Product.all(), [])

    def test_list_all_products(self):
        """It should list all products on the database"""
        self.assertEqual(Product.all(), [])

        size = randint(10, 50)
        products = []

        # Randomly create various products
        for i in range(0, size):
            product = ProductFactory()
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)
            products.append(product)

        self.assertEqual(len(products), len(Product.all()))

    def test_find_by_name(self):
        """It should find a product by its name"""
        size = randint(5, 50)
        # Randomly create various products
        products = ProductFactory.create_batch(size)

        for product in products:
            product.create()

        # Get one of the created names
        name = products[randrange(0, size)].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)

        self.assertEqual(found.count(), count)

        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should find a product by the availability"""
        size = randint(5, 50)
        # Randomly create various products
        products = ProductFactory.create_batch(size)

        for product in products:
            product.create()

        # Get the availability of one of the products
        availability = products[randrange(0, size)].available
        count = len([product for product in products if product.available == availability])
        found = Product.find_by_availability(availability)

        self.assertEqual(found.count(), count)

        for product in found:
            self.assertEqual(product.available, availability)

    def test_find_by_category(self):
        """It should find a product by its category"""
        size = randint(5, 50)
        # Randomly create various products
        products = ProductFactory.create_batch(size)

        for product in products:
            product.create()

        # Get the category of one of the products
        category = products[randrange(0, size)].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)

        self.assertEqual(found.count(), count)

        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """It should find a product by its price"""
        size = randint(5, 50)
        # Randomly create various products
        products = ProductFactory.create_batch(size)

        for product in products:
            # Pass some prices as strings to test string to number formatting
            if random() < 0.25:
                product.price = str(product.price)

            product.create()

        # Get the category of one of the products
        price = products[randrange(0, size)].price
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(price)

        self.assertEqual(found.count(), count)

        for product in found:
            self.assertEqual(product.price, price)
