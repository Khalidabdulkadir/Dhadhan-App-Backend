
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import Category, Product, Order, Reel, SavedReel, Restaurant
from .serializers import (
    CategorySerializer, ProductSerializer, OrderSerializer, 
    RegisterSerializer, UserSerializer, CreateOrderSerializer,
    ReelSerializer, SavedReelSerializer, RestaurantSerializer
)

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = (permissions.AllowAny,) # Update based on requirements, potentially IsAdminUser for write operations

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        queryset = Category.objects.all()
        restaurant = self.request.query_params.get('restaurant')
        if restaurant:
            queryset = queryset.filter(restaurant_id=restaurant)
        return queryset

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (permissions.AllowAny,)
    
    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        restaurant = self.request.query_params.get('restaurant')
        search = self.request.query_params.get('search')
        
        if category:
            queryset = queryset.filter(category_id=category)
        if restaurant:
            queryset = queryset.filter(restaurant_id=restaurant)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        read_serializer = OrderSerializer(order)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

class ReelViewSet(viewsets.ModelViewSet):
    queryset = Reel.objects.all().order_by('-is_highlight', '-created_at')
    serializer_class = ReelSerializer
    permission_classes = (permissions.AllowAny,) # Allow viewing by anyone, adjust if needed (e.g., ReadOnly for public)

    def get_parsers(self):
        if hasattr(self, 'action') and self.action in ['create', 'update', 'partial_update']:
             from rest_framework.parsers import MultiPartParser, FormParser
             return [MultiPartParser, FormParser]
        return super().get_parsers()

    def get_queryset(self):
        queryset = Reel.objects.all().order_by('-is_highlight', '-created_at')
        restaurant = self.request.query_params.get('restaurant')
        if restaurant:
             queryset = queryset.filter(restaurant_id=restaurant)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny]) # Ideally IsAuthenticated
    def view(self, request, pk=None):
        reel = self.get_object()
        reel.views += 1
        reel.save()
        return Response({'views': reel.views})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_save(self, request, pk=None):
        reel = self.get_object()
        user = request.user
        
        saved_item, created = SavedReel.objects.get_or_create(user=user, reel=reel)
        
        if not created:
            saved_item.delete()
            return Response({'status': 'unsaved'})
        
        return Response({'status': 'saved'})

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

class GoogleLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        print(f"Received token: {token[:20]}...")

        user_data = None
        
        # 1. Try as Access Token (UserInfo Endpoint)
        try:
            print("Trying UserInfo endpoint...")
            response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                params={'access_token': token}
            )
            if response.status_code == 200:
                user_data = response.json()
                print("UserInfo success")
            else:
                print(f"UserInfo failed: {response.status_code} {response.text}")
        except Exception as e:
            print(f"UserInfo exception: {e}")

        # 2. If failed, try as ID Token (TokenInfo Endpoint)
        if not user_data:
            try:
                print("Trying TokenInfo endpoint...")
                response = requests.get(
                    'https://oauth2.googleapis.com/tokeninfo',
                    params={'id_token': token}
                )
                if response.status_code == 200:
                    user_data = response.json()
                    print("TokenInfo success")
                else:
                    print(f"TokenInfo failed: {response.status_code} {response.text}")
            except Exception as e:
                print(f"TokenInfo exception: {e}")

        if not user_data:
            return Response({'error': 'Invalid token. Could not verify with Google.'}, status=status.HTTP_400_BAD_REQUEST)

        email = user_data.get('email')
        if not email:
            return Response({'error': 'Email not found in Google data'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            print(f"Found existing user: {email}")
        except User.DoesNotExist:
            print(f"Creating new user: {email}")
            first_name = user_data.get('given_name', '')
            last_name = user_data.get('family_name', '')
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=User.objects.make_random_password()
            )

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
