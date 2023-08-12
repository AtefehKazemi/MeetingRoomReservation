from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, blank = False)

    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "room number: " + self.room_number

class RoomReservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return "room: " + self.room.room_number + "team: " + self.team.name



