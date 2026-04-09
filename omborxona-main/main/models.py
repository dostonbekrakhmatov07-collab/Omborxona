from django.core.validators import MinValueValidator
from django.db import models

from django.contrib.auth.models import AbstractUser


class Branch(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, blank=True, null=True)


class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    quantity = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    unit = models.CharField(max_length=10, blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=100)
    shop_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    debt = models.FloatField(validators=[MinValueValidator(0.0)], default=0)

    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.FloatField(validators=[MinValueValidator(0.0)], default=1)
    total_price = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    paid = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    debt = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name


class ImportProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.FloatField(validators=[MinValueValidator(0.0)], default=1)
    buy_price = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    sell_price = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name


class DebtPay(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField(validators=[MinValueValidator(0.0)], default=1)
    description = models.TextField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description


class Expense(models.Model):
    text = models.TextField(blank=True, null=True)
    amount = models.FloatField(validators=[MinValueValidator(0.0)], default=1)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
