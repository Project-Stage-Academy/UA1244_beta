import os

import pytest
import mongomock
from cryptography.fernet import Fernet
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from mongoengine import connect, disconnect

from communications.models import Message, Room
from users.models import User


cipher = Fernet(os.environ.get('FERNET_KEY'))

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='password', email='test@example.com')

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture(scope='function', autouse=True)
def mongo_client():
    connect('mocked_db', mongo_client_class=mongomock.MongoClient, alias='mocked')
    yield
    disconnect(alias='mocked')

@pytest.fixture
def conversation(user):
    participants = [
        {"user_id": str(user.user_id), "username": user.username},
        {"user_id": "456", "username": "participant2"},
    ]
    room = Room(messages=[], participants=participants)
    room.save()
    return room

@pytest.mark.django_db
def test_create_conversation_success(authenticated_client):
    url = reverse('communications:conversation')
    user = User.objects.create_user(username='user', password='password', email='user@example.com')
    response = authenticated_client.post(url, {
    "participants": [
        {
            "user_id": user.user_id,
            "username": user.username
        }]
    }, format='json')
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_conversation_not_authorized(api_client):
    url = reverse('communications:conversation')
    user = User.objects.create_user(username='user', password='password', email='user@example.com')
    response = api_client.post(url, {
    "participants": [
        {
            "user_id": user.user_id,
            "username": user.username
        }]
    }, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_create_conversation_not_valid(authenticated_client):
    url = reverse('communications:conversation')
    user = User.objects.create_user(username='user', password='password', email='user@example.com')
    response = authenticated_client.post(url, {
        "participants": [
            {
                "user": user.user_id,
                "username": user.username
            }]
    }, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_conversation_empty_request(authenticated_client):
    url = reverse('communications:conversation') 
    response = authenticated_client.post(url, {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "Empty request body"}

@pytest.mark.django_db
def test_create_conversation_empty_participants_list(authenticated_client):
    url = reverse('communications:conversation')
    data = {"participants": []}
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "'participants' empty in request body"}

# Test MessageApiView
@pytest.mark.django_db
def test_send_message(authenticated_client, conversation):
    url = reverse('communications:send_message') 
    data = {
        "conversation_id": str(conversation.id),
        "text": "Hello!"
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data == "Message sent successfully!"

@pytest.mark.django_db
def test_send_message_not_authorized(api_client, conversation):
    url = reverse('communications:send_message')
    data = {
        "conversation_id": str(conversation.id),
        "text": "Hello!"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_send_message_empty_request(authenticated_client):
    url = reverse('communications:send_message')
    response = authenticated_client.post(url, {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "Empty request body"}

@pytest.mark.django_db
def test_send_message_missing_conversation_id_key(authenticated_client):
    url = reverse('communications:send_message')
    data = {
        "text": "Hello, this is a test message!"
    }
    response = authenticated_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    expected_error_message = {"error": "Missing 'conversation_id' key in request body"}
    assert response.data == expected_error_message


# Test ListMessagesApiView
@pytest.mark.django_db
def test_list_messages(authenticated_client, conversation):
    # Create a Message instance
    text = "Hello!"
    encrypted_text = cipher.encrypt(text.encode()).decode()

    message = Message(
        sender={"user_id": str(conversation.participants[0]['user_id']),
                "username": conversation.participants[0]['username']},
        message=encrypted_text
    )
    conversation.messages.append(message)
    conversation.save()
    url = reverse('communications:list_messages', kwargs={'conversation_id': str(conversation.id)})
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0
    assert response.data[0] == text