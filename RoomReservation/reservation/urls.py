from django.urls import path
from .views import *

urlpatterns = [
    path('AddRoom/', AddRoom.as_view(), name='AddRoom'),
    path('EditRoom/<int:pk>/', EditRoom.as_view(), name='EditRoom'),
    path('ActiveRoom/', ActiveRoom.as_view(), name='ActiveRoom'),
    path('RoomAvailability/', RoomAvailability.as_view(), name='RoomAvailability'),
    path('ReserveRoom/', ReserveRoom.as_view(), name='ReserveRoom'),
    path('ReservationDetail/<int:pk>/', ReservationDetail.as_view(), name='ReservationDetail'),
    path('CreateTeam/', CreateTeam.as_view(), name='CreateTeam'),

]
