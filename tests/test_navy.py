# -*- coding: utf-8 -*-
"""
    Navy Tests
    ~~~~~~~~~~~~    
"""

import os
import tempfile
import pytest
from NavyDiary import NavyDiary


@pytest.fixture
def client(request):
    db_fd, NavyDiary.app.config['DATABASE'] = tempfile.mkstemp()
    NavyDiary.app.config['TESTING'] = True
    client = NavyDiary.app.test_client()
    with NavyDiary.app.app_context():
        NavyDiary.init_db()

    def teardown():
         os.close(db_fd)
         os.unlink(NavyDiary.app.config['DATABASE'])
    request.addfinalizer(teardown)

    return client


def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_empty_db(client):
    """Start with a blank database."""
    rv = client.get('/')
    assert b'No events' in rv.data


def test_login_logout(client):
    """Make sure login and logout works"""
    rv = login(client, NavyDiary.app.config['USERNAME'],
               NavyDiary.app.config['PASSWORD'])
    assert b'You were logged in' in rv.data
    rv = logout(client)
    assert b'You were logged out' in rv.data
    rv = login(client, NavyDiary.app.config['USERNAME'] + 'x',
               NavyDiary.app.config['PASSWORD'])
    assert b'Invalid username' in rv.data
    rv = login(client, NavyDiary.app.config['USERNAME'],
               NavyDiary.app.config['PASSWORD'] + 'x')
    assert b'Invalid password' in rv.data


def test_messages(client):
    """Test that messages work"""
    login(client, NavyDiary.app.config['USERNAME'],
          NavyDiary.app.config['PASSWORD'])
    rv = client.post('/add', data=dict(
        title='<Hello>',
        text='<strong>HTML</strong> allowed here'
    ), follow_redirects=True)
    assert b'No events' not in rv.data
    assert b'&lt;Hello&gt;' in rv.data
    assert b'<strong>HTML</strong> allowed here' in rv.data