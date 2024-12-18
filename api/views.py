from django.db.models import Max
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import InStockFilterBackend, ProductFilter, OrderFilter
from api.models import Order, Product
from api.serializers import OrderSerializer, ProductInfoSerializer, ProductSerializer

# def product_list(request):
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)
#     return JsonResponse({"data": serializer.data})


class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.order_by("pk")
    serializer_class = ProductSerializer
    # filterset_fields = ('name', 'price')
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
    ]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "stock"]
    # pagination_class = PageNumberPagination
    # pagination_class.page_size = 2
    # pagination_class.page_query_param = "pagenum"
    # pagination_class.page_size_query_param = "size"
    # pagination_class.max_page_size = 6
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


# class ProductCreateAPIView(generics.CreateAPIView):
#     model = Product
#     serializer_class = ProductSerializer

#     def create(self, request, *args, **kwargs):
#         print(request.data)
#         return super().create(request, *args, **kwargs)


# @api_view(["GET"])
# def product_list(request):
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data)


# @api_view(["GET"])
# def product_detail(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     serializer = ProductSerializer(product)
#     return Response(serializer.data)


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = "product_id"

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


# @api_view(["GET"])
# def order_list(request):
#     orders = Order.objects.prefetch_related("items__product")
#     serializer = OrderSerializer(orders, many=True)
#     return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("items__product")
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    @action(
        detail=False,
        methods=["get"],
        url_path="user-orders",
        permission_classes=[IsAuthenticated],
    )
    def user_orders(self, request):
        orders = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


# class OrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related("items__product")
#     serializer_class = OrderSerializer


# class UserOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related("items__product")
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         qs = super().get_queryset()
#         return qs.filter(user=user)


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer(
            {
                "products": products,
                "count": len(products),
                "max_price": products.aggregate(max_price=Max("price"))["max_price"],
            }
        )
        return Response(serializer.data)


# @api_view(["GET"])
# def product_info(request):
#     products = Product.objects.all()
#     serializer = ProductInfoSerializer(
#         {
#             "products": products,
#             "count": len(products),
#             "max_price": products.aggregate(max_price=Max("price"))["max_price"],
#         }
#     )
#     return Response(serializer.data)
