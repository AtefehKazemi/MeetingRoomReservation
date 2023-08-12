from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TeamSerializer, RoomSerializer, RoomReservationSerializer
from .models import Team, Room, RoomReservation
from .permissions import IsManagerOrReadOnly
from datetime import datetime


# Create a new room 
# Only manager is allowed to do so
class AddRoom(APIView):
    permission_classes = [IsManagerOrReadOnly]
    def post(self, request):
        data = request.data
        serializer = RoomSerializer(data = data)
        if serializer.is_valid():
            # Check if the meeting room is available for the specified time
            room_number = serializer.validated_data.get('room_number')
            #is_active = serializer.validated_data.get['is_active']
            
            if Room.objects.filter(room_number = room_number).exists():
                return Response({"error": "This room number is registered already"}, status = 400)
            else:
                serializer.save()
                return Response(serializer.data, status = 201)
        return Response(serializer.errors, status = 400)


# Edit a specific room
# Everyone can view
# Ony manager can edit
class EditRoom(APIView):
    permission_classes = [IsManagerOrReadOnly]
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return None

    def get(self, request, pk):
        meeting_room = self.get_object(pk)
        if not meeting_room:
            return Response({"error": "Meeting Room not found."}, status = 404)

        serializer = RoomSerializer(meeting_room)
        return Response(serializer.data)

    def put(self, request, pk):
        meeting_room = self.get_object(pk)
        if not meeting_room:
            return Response({"error": "Meeting Room not found."}, status = 404)

        serializer = RoomSerializer(meeting_room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = 200)

        return Response(serializer.errors, status = 404)


# View all active rooms
class ActiveRoom(APIView):
    def get(self, request):
        active_rooms = Room.objects.filter(is_active = True)

        if active_rooms:
            serializer = RoomSerializer(active_rooms, many = True)
            return Response(serializer.data)
        else:
            return Response({"message": "No active rooms available."}, status = 404)
        

# Get all rooms' status(Occupied/Empty) in given time
class RoomAvailability(APIView):
    def get(self, request):
        time = request.GET.get('time') 

        if not time:
            return Response({"error": "Please provide the 'time' parameter in the query string."}, status = 400)

        try:
            # Try parsing the time using the specified format
            parsed_time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            reservations = RoomReservation.objects.filter(start_time__lte=parsed_time, end_time__gt=parsed_time).values_list('room', flat=True)
        except ValueError:
            # Handle the case when the time format is incorrect
            return Response({"error": "Invalid time format. Please provide time in the format 'YYYY-MM-DD HH:MM:SS'."}, status=400)

        rooms = Room.objects.all()
        availability_status = {}
        for room in rooms:
            if room.id in reservations:
                availability_status[room.room_number] = "Occupied"
            else:
                availability_status[room.room_number] = "Empty"
        print (availability_status)
        return Response(availability_status)
    

# Reserve a room
class ReserveRoom(APIView):
    def post(self, request):
        data = request.data
        serializer = RoomReservationSerializer(data = data)

        if serializer.is_valid():
            # Check if the meeting room is available for the specified time
            room = serializer.validated_data['room']
            team = serializer.validated_data['team']
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['end_time']

            if RoomReservation.objects.filter(room = room, start_time__lt = end_time, end_time__gt = start_time).exists():
                return Response({"error": "The meeting room is already reserved for this time."}, status = 400)

            serializer.save(user = request.user)
            return Response(serializer.data, status = 201)
        
        return Response(serializer.errors, status = 400)  


# View or delete a specific reservation
# Everyone can view details
# Only manager is allowed to delete that
class ReservationDetail(APIView):
    permission_classes = [IsManagerOrReadOnly]

    def get_object(self, pk):
        try:
            return RoomReservation.objects.get(pk = pk)
        except RoomReservation.DoesNotExist:
            return None

    def get(self, request, pk):
        reservation = self.get_object(pk)
        if not reservation:
            return Response({"error": "Reservation not found."}, status = 404)

        serializer = RoomReservationSerializer(reservation)
        return Response(serializer.data)

    def delete(self, request, pk):
        reservation = self.get_object(pk)
        if not reservation:
            return Response({"error": "Reservation not found."}, status = 404)

        reservation.delete()
        return Response({"message": "Reservation deleted successfully."}, status = 204)


# Create a new team
class CreateTeam(APIView):
    def post(self, request):
        data = request.data
        serializer = TeamSerializer(data = data)

        if serializer.is_valid():
            # Check if the meeting room is available for the specified time
            # name = serializer.validated_data['name']
            # members = serializer.validated_data['members']
            serializer.save()
            return Response(serializer.data, status = 201)
        
        return Response(serializer.errors, status = 400)
    

