
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    CategoryViewSet, ProductViewSet, OrderViewSet, 
    RegisterView, UserProfileView, GoogleLoginView, UserViewSet,
    ReelViewSet, RestaurantViewSet, UserDeleteView, FavoriteFoodViewSet, DirectOrderViewSet
)

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'users', UserViewSet)
router.register(r'reels', ReelViewSet)
router.register(r'favorites', FavoriteFoodViewSet, basename='favorite')
router.register(r'direct-orders', DirectOrderViewSet, basename='direct-order')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('auth/profile/delete/', UserDeleteView.as_view(), name='user_delete'),
]
