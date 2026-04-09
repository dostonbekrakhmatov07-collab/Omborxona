from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from main.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('products/', ProductsView.as_view(), name='products'),
    path('products/<int:pk>/delete-confirm/', ProductDeleteConfirmView.as_view(), name='product-confirm-delete'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('clients/', ClientsView.as_view(), name='clients'),
    path('clients/<int:pk>/delete-confirm/', ClientDeleteConfirmView.as_view(), name='client-confirm-delete'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client-delete'),
    path('clients/<int:pk>/update/', ClientUpdateView.as_view(), name='client-update'),
    path('sales/', SalesView.as_view(), name='sales'),
    path('sales/<int:pk>/delete-confirm/', SalesDeleteConfirmView.as_view(), name='sale-confirm-delete'),
    path('sales/<int:pk>/delete/', SalesDeleteView.as_view(), name='sale-delete'),
    path('sales/<int:pk>/update/', SalesUpdateView.as_view(), name='sale-update'),
    path('import-products/', ImportProductsView.as_view(), name='import-products'),
    path('import-products/<int:pk>/update/', ImportProductsUpdateView.as_view(), name='import-product-update'),
    path('import-products/<int:pk>/delete-confirm/', ImportProductsDeleteConfirmView.as_view(), name='import-product-confirm-delete'),
    path('import-products/<int:pk>/delete/', ImportProductsDeleteView.as_view(), name='import-product-delete'),
    path('debt-pays/', DebtPaysView.as_view(), name='debt-pays'),
    path('debt-pays/<int:pk>/delete-confirm/', DebtPaysDeleteConfirmView.as_view(), name='debt-pay-confirm-delete'),
    path('debt-pays/<int:pk>/delete/', DebtPaysDeleteView.as_view(), name='debt-pay-delete'),
    path('debt-pays/<int:pk>/update/', DebtPayUpdateView.as_view(), name='debt-pay-update'),
]

urlpatterns += [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

