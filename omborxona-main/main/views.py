from django.utils import timezone

from django.db.models import ExpressionWrapper, F, FloatField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.http import HttpResponse

from .models import *


class HomeView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        return render(request, 'sections.html')


class ProductsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        products = Product.objects.filter(branch=request.user.branch).annotate(
            total_value=ExpressionWrapper(
                F('quantity') * F('price'),
                output_field=FloatField()
            )
        ).order_by('-total_value')

        context = {
            'products': products,
        }
        return render(request, 'products.html', context)

    def post(self, request):
        Product.objects.create(
            name=request.POST.get('name'),
            brand=request.POST.get('brand', "Local"),
            price=request.POST.get('price'),
            quantity=request.POST.get('quantity', 0),
            unit=request.POST.get('unit', 'dona'),
            branch=request.user.branch,
        )
        return redirect('products')


class ProductDeleteConfirmView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        context = {
            'product': product,
        }
        return render(request, 'product-delete-confirm.html', context)


class ProductDeleteView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        product.delete()
        return redirect('products')


class ProductUpdateView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        context = {
            'product': product,
        }
        return render(request, 'product-update.html', context)

    def post(self, request, pk):
        Product.objects.filter(pk=pk).update(
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            quantity=request.POST.get('quantity'),
            unit=request.POST.get('unit'),
            branch=request.user.branch
        )
        return redirect('products')


class ClientsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        clients = Client.objects.filter(branch=request.user.branch).order_by('-debt')
        context = {
            'clients': clients,
        }
        return render(request, 'clients.html', context)

    def post(self, request):
        Client.objects.create(
            name=request.POST.get('name'),
            shop_name=request.POST.get('shop_name'),
            phone_number=request.POST.get('phone_number'),
            address=request.POST.get('address'),
            debt=request.POST.get('debt') if request.POST.get('debt') else 0,
            branch=request.user.branch
        )
        return redirect('clients')


class ClientDeleteConfirmView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        context = {
            'client': client,
        }
        return render(request, 'client-delete-confirm.html', context)


class ClientDeleteView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        client.delete()
        return redirect('clients')


class ClientUpdateView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        context = {
            'client': client,
        }
        return render(request, 'client-update.html', context)

    def post(self, request, pk):
        Client.objects.filter(pk=pk).update(
            name=request.POST.get('name'),
            shop_name=request.POST.get('shop_name'),
            phone_number=request.POST.get('phone_number'),
            address=request.POST.get('address'),
            debt=request.POST.get('debt') if request.POST.get('debt') else 0,
            branch=request.user.branch
        )
        return redirect('clients')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('home')
        return self.get(request)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

class SalesView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request):
        sales = Sale.objects.filter(branch=request.user.branch).order_by('-created_at')
        products = Product.objects.filter(branch=request.user.branch).order_by('name')
        clients = Client.objects.filter(branch=request.user.branch).order_by('name')
        context = {
            'sales': sales,
            'products': products,
            'clients': clients,
        }
        return render(request, 'sales.html', context)

    def post(self, request):
        product = get_object_or_404(Product, branch=request.user.branch, id=request.POST.get('product_id'))
        client = get_object_or_404(Client, branch=request.user.branch, id=request.POST.get('client_id'))
        quantity = float(request.POST.get('quantity')) if request.POST.get('quantity') else 0
        total_price = float(request.POST.get('total_price')) if request.POST.get('total_price') else product.price * quantity
        paid = float(request.POST.get('paid_price')) if request.POST.get('paid_price') else 0
        debt = float(request.POST.get('debt_price')) if request.POST.get('debt_price') else 0

        if product.quantity < quantity:
            return HttpResponse(
                f"""
                {product.name} siz so'ragan miqdordan kam. Mavjud: {product.quantity} {product.unit}
                <a href="/sales/">Ortga<a/>
                """
            )

        if not paid and not debt:
            paid = total_price

        if paid and not debt:
            debt = total_price - paid

        if not paid and debt:
            paid = total_price - debt

        if paid + debt != total_price:
            return HttpResponse(
                f"""
                Pullar noto'g'ri hisoblandi!
                <a href="/sales/">Ortga<a/>
                """
            )

        Sale.objects.create(
            product=product,
            client=client,
            quantity=quantity,
            total_price=total_price,
            paid=paid,
            debt=debt,
            branch=request.user.branch,
        )

        product.quantity -= quantity
        product.save()

        client.debt += debt
        client.save()

        return redirect('sales')


class SalesUpdateView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk, branch=request.user.branch)
        products = Product.objects.filter(branch=request.user.branch).order_by('name')
        clients = Client.objects.filter(branch=request.user.branch).order_by('name')
        context = {
            'sale': sale,
            'products': products,
            'clients': clients,
        }
        return render(request, 'sales-update.html', context)

    def post(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk, branch=request.user.branch)
        old_quantity = sale.quantity
        old_debt = sale.debt

        product = get_object_or_404(Product, pk=request.POST.get('product_id'), branch=request.user.branch)
        client = get_object_or_404(Client, pk=request.POST.get('client_id'), branch=request.user.branch)

        quantity = float(request.POST.get('quantity')) if request.POST.get('quantity') else old_quantity
        total_price = float(request.POST.get('total_price')) if request.POST.get('total_price') else product.price * quantity
        paid = float(request.POST.get('paid_price')) if request.POST.get('paid_price') else 0
        debt = float(request.POST.get('debt_price')) if request.POST.get('debt_price') else 0

        if not paid and not debt:
            paid = total_price
        if paid and not debt:
            debt = total_price - paid
        if not paid and debt:
            paid = total_price - debt

        if paid + debt != total_price:
            return HttpResponse("Pullar noto'g'ri hisoblandi! <a href='/sales/'>Ortga</a>")

        product.quantity += old_quantity - quantity
        product.save()

        client.debt = client.debt - old_debt + debt
        client.save()

        sale.product = product
        sale.client = client
        sale.quantity = quantity
        sale.total_price = total_price
        sale.paid = paid
        sale.debt = debt
        sale.save()

        return redirect('sales')

class SalesDeleteConfirmView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk, branch=request.user.branch)
        context = {
            'sale': sale,
        }
        return render(request, 'sale-delete-confirm.html', context)


class SalesDeleteView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk, branch=request.user.branch)
        sale.delete()
        return redirect('sales')


class ImportProductsView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request):
        import_products = ImportProduct.objects.filter(branch=request.user.branch).order_by('-created_at')
        products = Product.objects.filter(branch=request.user.branch).order_by('name')
        context = {
            'import_products': import_products,
            'products': products,
        }
        return render(request, 'import-products.html', context)

    def post(self, request):
        product = get_object_or_404(Product, branch=request.user.branch, id=request.POST.get('product_id'))
        quantity = float(request.POST.get('quantity')) if request.POST.get('quantity') else 0
        ImportProduct.objects.create(
            product=product,
            quantity=quantity,
            buy_price=request.POST.get('buy_price'),
            sell_price=request.POST.get('sell_price'),
            branch=request.user.branch,
            user=request.user,
        )

        product.quantity += quantity
        product.updated_at = timezone.now()
        product.price = float(request.POST.get('sell_price')) if request.POST.get('sell_price') else product.price * quantity
        product.save()
        return redirect('import-products')


class ImportProductsUpdateView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        import_product = get_object_or_404(ImportProduct, pk=pk, branch=request.user.branch)
        products = Product.objects.filter(branch=request.user.branch).order_by('name')
        context = {
            'import_product': import_product,
            'products': products,
        }
        return render(request, 'import-product-update.html', context)

    def post(self, request, pk):
        ImportProduct.objects.filter(pk=pk).update(
            product=request.POST.get('product'),
            quantity=request.POST.get('quantity'),
            buy_price=request.POST.get('buy_price'),
            sell_price=request.POST.get('sell_price'),
            branch=request.user.branch,
            user=request.user,
        )
        return redirect('import-products')

class ImportProductsDeleteConfirmView(LoginRequiredMixin, View):
        login_url = 'login'

        def get(self, request, pk):
            import_product = get_object_or_404(ImportProduct, pk=pk, branch=request.user.branch)
            context = {
                'import_product': import_product,
            }
            return render(request, 'import-product-delete-confirm.html', context)

class ImportProductsDeleteView(LoginRequiredMixin, View):
        login_url = 'login'

        def get(self, request, pk):
            import_product = get_object_or_404(ImportProduct, pk=pk, branch=request.user.branch)
            import_product.delete()
            return redirect('import-products')

class DebtPaysView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        debt_pays = DebtPay.objects.filter(branch=request.user.branch).order_by('-created_at')
        clients = Client.objects.filter(branch=request.user.branch).order_by('name')
        context = {
            'debt_pays': debt_pays,
            'clients': clients,
        }
        return render(request, 'debt-pays.html', context)

    def post(self, request):
        client = get_object_or_404(Client, branch=request.user.branch, id=request.POST.get('client_id'))
        amount = float(request.POST.get('amount')) if request.POST.get('amount') else 0

        if amount <= 0:
            return redirect('debt-pays')

        DebtPay.objects.create(
            client=client,
            amount=amount,
            description=request.POST.get('description'),
            user=request.user,
            branch=request.user.branch,
        )

        client.debt -= amount
        if client.debt < 0:
            client.debt = 0
        client.save()

        remaining_amount = amount
        sales = Sale.objects.filter(client=client, debt__gt=0).order_by('created_at')

        for sale in sales:
            if remaining_amount <= 0:
                break

            pay_for_sale = min(sale.debt, remaining_amount)
            sale.debt -= pay_for_sale
            sale.paid += pay_for_sale
            sale.save()

            remaining_amount -= pay_for_sale

        return redirect('debt-pays')

class DebtPayUpdateView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        debt_pay = get_object_or_404(DebtPay, pk=pk, branch=request.user.branch)
        clients = Client.objects.filter(branch=request.user.branch).order_by('name')

        context = {
            'debt_pay': debt_pay,
            'clients': clients
        }
        return render(request, 'debt-pay-update.html', context)

    def post(self, request, pk):
        debt_pay = get_object_or_404(DebtPay, pk=pk, branch=request.user.branch)

        client = get_object_or_404(
            Client,
            id=request.POST.get('client_id'),
            branch=request.user.branch
        )

        new_amount = float(request.POST.get('amount')) if request.POST.get('amount') else 0
        description = request.POST.get('description')

        old_amount = debt_pay.amount

        remaining = old_amount
        sales = Sale.objects.filter(client=debt_pay.client).order_by('-created_at')

        for sale in sales:
            paid_from_sale = sale.total_price - sale.debt

            if paid_from_sale <= 0:
                continue

            if remaining <= 0:
                break

            if remaining >= paid_from_sale:
                sale.debt += paid_from_sale
                sale.paid -= paid_from_sale
                remaining -= paid_from_sale
            else:
                sale.debt += remaining
                sale.paid -= remaining
                remaining = 0

            sale.save()

        remaining = new_amount
        sales = Sale.objects.filter(client=client, debt__gt=0).order_by('created_at')

        for sale in sales:

            if remaining <= 0:
                break

            if remaining >= sale.debt:
                sale.paid += sale.debt
                remaining -= sale.debt
                sale.debt = 0
            else:
                sale.paid += remaining
                sale.debt -= remaining
                remaining = 0

            sale.save()

        client.debt += old_amount
        client.debt -= new_amount

        if client.debt < 0:
            client.debt = 0

        client.save()

        debt_pay.client = client
        debt_pay.amount = new_amount
        debt_pay.description = description
        debt_pay.save()

        return redirect('debt-pays')


class DebtPaysDeleteConfirmView(LoginRequiredMixin, View):
        login_url = 'login'

        def get(self, request, pk):
            debt_pay = get_object_or_404(DebtPay, pk=pk, branch=request.user.branch)
            context = {
                'debt_pay': debt_pay,
            }
            return render(request, 'debt-pay-delete-confirm.html', context)

class DebtPaysDeleteView(LoginRequiredMixin, View):
        login_url = 'login'

        def post(self, request, pk):
            debt_pay = get_object_or_404(DebtPay, pk=pk, branch=request.user.branch)
            debt_pay.delete()
            return redirect('debt-pays')