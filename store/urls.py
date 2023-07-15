from django.urls import path
from .views import CollectionViewSet, ProductViewSet, ReviewViewSet, CartViewSet, CartItemViewSet, CustomerViewSet,\
OrderViewSet, OrderItemsViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('collections', CollectionViewSet)
router.register('carts', CartViewSet)
router.register('customer', CustomerViewSet)
router.register('order', OrderViewSet)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-review')

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + cart_router.urls 