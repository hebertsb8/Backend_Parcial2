# notifications/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceTokenViewSet, NotificationViewSet, NotificationPreferenceViewSet, NotificationCampaignViewSet, firebase_config_view

router = DefaultRouter()
router.register(r'device-tokens', DeviceTokenViewSet, basename='device-token')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'campaigns', NotificationCampaignViewSet, basename='notification-campaign')

urlpatterns = [
    path('', include(router.urls)),
    path('firebase-config/', firebase_config_view, name='firebase-config'),
]
