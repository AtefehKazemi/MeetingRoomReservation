from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Team, Room, RoomReservation
from django.contrib.auth.models import User

# Adding room test
class AddRoomTests(APITestCase):
    def setUp(self):
        # Create a user for testing
        self.manager_user = User.objects.create_user(username="manager", password="managerpassword", is_staff=True)

    def test_add_room_successful(self):
        url = reverse('AddRoom')
        data = {
            'room_number': 111,
            'is_active': True,
        }
        # Authenticate the user as a manager
        self.client.force_authenticate(user = self.manager_user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)  # room is created successfully
        self.assertEqual(Room.objects.first().room_number, 111)  # Check the room number

    def test_add_room_existing_room_number(self):
        # Create a room with room number '112'
        Room.objects.create(room_number = 112, is_active = True)

        url = reverse('AddRoom')
        data = {
            'room_number': 112,
            'is_active': False,
        }
        # Authenticate the user as a manager
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Room.objects.count(), 1)  # Ensure only one room is present

# Editing room test
class EditRoomTests(APITestCase):
    def setUp(self):
        # Create a user for testing
        self.manager_user = User.objects.create_user(username="manager", password="managerpassword", is_staff=True)

        # Create a test room
        self.room = Room.objects.create(room_number=111, is_active=True)

    def test_get_room(self):
        url = reverse('EditRoom', args=[self.room.pk])
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['room_number'], self.room.room_number)
        self.assertEqual(response.data['is_active'], self.room.is_active)

    def test_get_nonexistent_room(self):
        url = reverse('EditRoom', args=[33])  # Non-existent room ID
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_room(self):
        url = reverse('EditRoom', args=[self.room.pk])
        data = {
            'room_number': 112,  # Updated room number
            'is_active': False,  # Updated is_active status
        }
        # Authenticate the user as a manager
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()  # Refresh room data from the database
        self.assertEqual(self.room.room_number, data['room_number'])
        self.assertEqual(self.room.is_active, data['is_active'])

    def test_update_nonexistent_room(self):
        url = reverse('EditRoom', args=[33])  # Non-existent room ID
        data = {
            'room_number': 112,
            'is_active': False,
        }
        # Authenticate the user as a manager
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# Viewing active rooms test
class ActiveRoomTests(APITestCase):
    def setUp(self):
        # Create test rooms, both active and inactive
        Room.objects.create(room_number=111, is_active=True)
        Room.objects.create(room_number=112, is_active=False)

    def test_get_active_rooms(self):
        url = reverse('ActiveRoom')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # We only have one active room in the test data

    def test_get_no_active_rooms(self):
        # Deactivate all rooms for this test
        Room.objects.update(is_active=False)

        url = reverse('ActiveRoom')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], "No active rooms available.")

# Viewing available rooms test
class RoomAvailabilityTests(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username="user1", password="user1password", is_staff=True)
        self.user2 = User.objects.create_user(username="user2", password="user2password", is_staff=True)

        # Create test teams
        self.team1 = Team.objects.create(name = 'team1')
        self.team2 = Team.objects.create(name = 'team2')
        self.team1.members.add(self.user1)
        self.team2.members.add(self.user1, self.user2)

        # Create test rooms
        self.room1 = Room.objects.create(room_number=111)
        self.room2 = Room.objects.create(room_number=112)

        # Create test reservations
        self.reservation1 = RoomReservation.objects.create(room=self.room1, team = self.team1, user = self.user1, start_time="2023-08-07 10:00:00", end_time="2023-08-07 12:00:00")
        self.reservation2 = RoomReservation.objects.create(room=self.room2, team = self.team1, user = self.user1, start_time="2023-09-05 17:00:00", end_time="2023-09-05 20:00:00")

    def test_get_room_availability(self):
        url = reverse('RoomAvailability')
        time = "2023-08-07 11:00:00"  # Adjust the time
        response = self.client.get(url, {'time': time})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[self.room1.room_number], "Occupied")
        self.assertEqual(response.data[self.room2.room_number], "Empty")

    def test_get_room_availability_no_time(self):
        url = reverse('RoomAvailability')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Please provide the 'time' parameter in the query string.")

    def test_get_room_availability_invalid_time_format(self):
        url = reverse('RoomAvailability')
        response = self.client.get(url, {'time': '2023-08-7 11:00'})  # Invalid time format

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Invalid time format. Please provide time in the format 'YYYY-MM-DD HH:MM:SS'.")

# Reserving rooms test
class ReserveRoomTests(APITestCase):
    def setUp(self):
        # Create test rooms, teams, and users
        self.user = User.objects.create_user(username="user", password="userpassword", is_staff=True)
        self.room = Room.objects.create(room_number = 111)
        self.team = Team.objects.create(name='Test Team')
        self.team.members.add(self.user)

    def test_reserve_room_success(self):
        url = reverse('ReserveRoom')
        data = {
            'room': self.room.id,
            'team': self.team.id,
            'user': self.user.id,
            'start_time': '2023-08-07 10:00:00',
            'end_time': '2023-08-07 12:00:00',
        }

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['room'], self.room.id)
        self.assertEqual(response.data['team'], self.team.id)
        self.assertEqual(response.data['start_time'], '2023-08-07T10:00:00Z')
        self.assertEqual(response.data['end_time'], '2023-08-07T12:00:00Z')

    def test_reserve_room_conflict(self):
        # Create a conflicting reservation
        conflicting_reservation = RoomReservation.objects.create(
            room=self.room,
            team=self.team,
            user = self.user,
            start_time='2023-08-07 09:00:00',
            end_time='2023-08-07 11:00:00',
        )

        url = reverse('ReserveRoom')
        data = {
            'room': self.room.id,
            'team': self.team.id,
            'user': self.user.id,
            'start_time': '2023-08-07 10:00:00',
            'end_time': '2023-08-07 12:00:00',
        }

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'], 'The meeting room is already reserved for this time.'
        )

# Viewing or deleting a Reservation
class ReservationDetailTests(APITestCase):
    def setUp(self):
        # Create test rooms, teams, and users
        self.user = User.objects.create_user(username="user", password="userpassword", is_staff=True)
        # Create a user for testing
        self.manager_user = User.objects.create_user(username="manager", password="managerpassword", is_staff=True)
        self.room = Room.objects.create(room_number = 111)
        self.team = Team.objects.create(name='Test Team')
        self.team.members.add(self.user)
        # Create a test reservation
        self.reservation = RoomReservation.objects.create(
            room=self.room,  # Replace 'self.room' with the room instance for this reservation
            team=self.team,  # Replace 'self.team' with the team instance for this reservation
            user=self.user,  # Replace 'self.user' with the user instance for this reservation
            start_time='2023-09-07 12:00:00',
            end_time='2023-09-07 14:00:00',
        )

    def test_get_reservation_details(self):
        url = reverse('ReservationDetail', args=[self.reservation.id])
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.reservation.id)
        self.assertEqual(response.data['room'], self.reservation.room.id)
        self.assertEqual(response.data['user'], self.reservation.user.id)
        self.assertEqual(response.data['team'], self.reservation.team.id)
        self.assertEqual(response.data['start_time'], '2023-09-07T12:00:00Z')
        self.assertEqual(response.data['end_time'], '2023-09-07T14:00:00Z')

    def test_delete_reservation(self):
        url = reverse('ReservationDetail', args=[self.reservation.id])
        # Authenticate the user as a manager
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RoomReservation.objects.filter(pk = self.reservation.id).exists())


# Creating new team test
class CreateTeamTests(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username="user1", password="user1password", is_staff=True)
        self.user2 = User.objects.create_user(username="user2", password="user2password", is_staff=True)

    def test_create_team(self):
        url = reverse('CreateTeam')

        # Prepare the test data
        team_data = {
            'name': 'team',
            'members': [self.user1.id, self.user2.id],
        }

        response = self.client.post(url, team_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify that the team is created with the correct data
        team = Team.objects.get(pk = response.data['id'])
        self.assertEqual(team.name, team_data['name'])
        self.assertListEqual(list(team.members.values_list('id', flat=True)), team_data['members'])