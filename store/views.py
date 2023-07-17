from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from .serializer import ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer,\
    CartItemsSerializer, AddCartItemsSerializer, UpdatingCartItemSerializer, CustomerSerializer,\
    OrderSerializer, OrderItemSerializer, CreateOrderSerializer, UpdateOrderSerializer, ProductImageSerializer
from .pagination import DefaultPagination
from .models import Product, Collection, OrderItem, Review, Cart, CartItem, Customer, Order, ProductImage
from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermission

# Create your views here.
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update', 'inventory']

    def get_serializer_context(self):
        return {'request':self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error':'Product is assoicate with orderitem'},
                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
     

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('product')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error':'collection has product in it'},
                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}

class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,   
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemsSerializer
        elif self.request.method == 'PATCH':
            return UpdatingCartItemSerializer
        return CartItemsSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')
    
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
 
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        else:
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('ok')
    
class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, 
                                           context={'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()
        
        customer_id = Customer.objects.only('id').get(user_id=user.id)
        Order.objects.filter(customer_id=customer_id)

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}
    
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])
    




