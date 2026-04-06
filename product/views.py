from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Category, Review
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer, ProductDetailSerializer, ReviewValidateSerializer
from .serializers import ProductWithReviewsSerializer, CategoryWithCountSerialzier, ProductValidateSerializer, CategoryValidateSerializer
from django.db.models import Count
from django.db import transaction
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView


class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategoryValidateSerializer
        return CategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = Category.objects.create(name=serializer.validated_data['name'])
        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)


class CategoryDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CategoryValidateSerializer
        return CategorySerializer

    def update(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category.name = serializer.validated_data['name']
        category.save()
        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)


class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductValidateSerializer
        return ProductSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = Product.objects.create(
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            price=serializer.validated_data['price'],
            category_id=serializer.validated_data['category']
        )
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)


class ProductDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductValidateSerializer
        return ProductDetailSerializer

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product.title = serializer.validated_data['title']
        product.description = serializer.validated_data.get('description', product.description)
        product.price = serializer.validated_data['price']
        product.category_id = serializer.validated_data['category']
        product.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)


class ReviewListCreateAPIView(ListCreateAPIView):
    queryset = Review.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewValidateSerializer
        return ReviewSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = Review.objects.create(
            text=serializer.validated_data.get('text', ''),
            stars=serializer.validated_data['stars'],
            product_id=serializer.validated_data['product']
        )
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class ReviewDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewValidateSerializer
        return ReviewSerializer

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review.text = serializer.validated_data.get('text', review.text)
        review.stars = serializer.validated_data['stars']
        review.product_id = serializer.validated_data['product']
        review.save()
        return Response(ReviewSerializer(review).data, status=status.HTTP_200_OK)


class ProductWithReviewsAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductWithReviewsSerializer


class CategoryWithCountAPIView(ListAPIView):
    queryset = Category.objects.annotate(products_count=Count('products'))
    serializer_class = CategoryWithCountSerialzier
