from django.contrib import admin
from .models import Team, Room, RoomReservation

admin.site.register(Team)
admin.site.register(Room)
admin.site.register(RoomReservation)