from django.urls import path
from .views import CollectionViewSet, ProductViewSet, ReviewViewSet, CartViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('collections', CollectionViewSet)
router.register('carts', CartViewSet)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-review')

urlpatterns = router.urls + products_router.urls