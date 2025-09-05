from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CUSTOMER = 'customer'
    ROLE_SELLER = 'seller'
    ROLE_CHOICES = [
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_SELLER, 'Seller'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)

    def is_seller(self):
        return self.role == self.ROLE_SELLER

    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER
