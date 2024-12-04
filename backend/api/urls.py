from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, EventViewSet, TicketViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'events', EventViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

# from django.urls import path
# from . import views

# urlpatterns = [
#     path("User/", views.UserListCreate.as_view(), name= "user-view-create"),
#     path("User/<int:pk>", views.UserRetrieveUpdateDestroy.as_view(), name= "user-view-create")
    
# ]

# urlpatterns = [
#     path("User/", views.UserRetrieveUpdateDestroy.as_view(), name= "user-view-create")
    
# ]
