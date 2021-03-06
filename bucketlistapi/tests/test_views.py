'''
Test file to test bucketlist endpoints
'''
import json
import unittest
from base64 import b64encode

from flask import url_for, g

from app import create_app, db
from app.models import User, BucketList, BucketItem


class TestAPI(unittest.TestCase):
    default_username = 'lade'
    default_password = 'password'
    default_bucketlist = 'This is a default bucketlist'
    default_bucketlistitem = 'This is a default bucketlist item'
    new_user = 'dave'

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        u = User(username=self.default_username)
        u.hash_password(self.default_password)
        u.save()
        g.user = u
        new_u = User(username=self.new_user)
        new_u.hash_password(self.default_password)
        new_u.save()
        bucketlist = BucketList(name=self.default_bucketlist)
        bucketlist.create()
        bucketlist.save()
        item = BucketItem(
            name=self.default_bucketlistitem, bucketlist_id=bucketlist.id
        )
        item.create()
        item.save()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization':
                'Basic ' + b64encode(
                    (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_token(self):
        # calls the login function and returns the token generated
        response = self.client.post(
            url_for('api_1.login'),
            headers=self.get_api_headers('lade', 'password'),
            data=json.dumps({'username': 'lade', 'password': 'password'}))
        token = json.loads(response.data)['token']
        return token

    def test_get_users(self):
        # test return all users
        token = self.get_token()
        response = self.client.get(
            url_for('api_1.get_users'),
            headers=self.get_api_headers(token, 'password'))
        self.assertTrue(response.status_code == 200)

    def test_get_user(self):
        # test return a user
        token = self.get_token()
        response = self.client.get(
            url_for('api_1.get_user', username='lade'),
            headers=self.get_api_headers(token, 'password'))
        self.assertTrue(response.status_code == 200)

    def test_get_bucketlists(self):
        # test return all bucketlists
        token = self.get_token()
        response = self.client.get(
            url_for('api_1.bucketlists'),
            headers=self.get_api_headers(token, 'password'))
        self.assertTrue(response.status_code == 200)

    def test_get_bucketlists_with_limit(self):
        # test return bucketlists with limit
        token = self.get_token()
        response = self.client.get(
            url_for('api_1.bucketlists', limit=1),
            headers=self.get_api_headers(token, 'password'))
        self.assertTrue(response.status_code == 200)

    def test_get_bucketlists_with_max_limit(self):
        # test return bucketlists with max limit
        token = self.get_token()
        response = self.client.get(
            url_for('api_1.bucketlists', limit=101),
            headers=self.get_api_headers(token, 'password'))
        self.assertTrue(response.status_code == 200)

    def test_get_bucketlists_with_query_search(self):
        # test return bucketlists with partial match in query
        token = self.get_token()
        response = self.client.get(
            url_for('api_1.bucketlists', q='This'),
            headers=self.get_api_headers(token, 'password'))
        self.assertTrue(response.status_code == 200)

    def test_create_bucketlist(self):
        # test create bucketlist
        token = self.get_token()
        response = self.client.post(
            url_for('api_1.bucketlists'),
            headers=self.get_api_headers(token, 'password'),
            data=json.dumps({'name': 'I just created a bucketlist'}))
        self.assertTrue(response.status_code == 200)

    def test_get_bucketlist_by_id(self):
        # test return a bucketlist
        token = self.get_token()
        response = self.client.get(
            url_for('api_1.bucketlist', bucketlist_id=1),
            headers=self.get_api_headers(token, 'password'))
        self.assertTrue(response.status_code == 200)

    def test_update_bucketlist(self):
        # test update a bucketlist name
        token = self.get_token()
        response = self.client.put(
            url_for('api_1.bucketlist', bucketlist_id=1),
            headers=self.get_api_headers(token, 'password'),
            data=json.dumps({'name': 'I just changed this bucketlist'}))
        self.assertTrue(response.status_code == 200)

    def test_delete_bucketlist(self):
        # test delete a bucketlist
        token = self.get_token()
        response = self.client.delete(
            url_for('api_1.bucketlist', bucketlist_id=1),
            headers=self.get_api_headers(token, 'password'))
        self.assertTrue(response.status_code == 200)

    def test_create_bucketitem(self):
        # test create a bucketitem
        token = self.get_token()
        response = self.client.post(
            url_for('api_1.add_bucketitem', bucketlist_id=1),
            headers=self.get_api_headers(token, 'password'),
            data=json.dumps({'name': 'I just created this bucketitem'}))
        self.assertTrue(response.status_code == 200)

    def test_update_bucketitem(self):
        # test update a bucketitem status
        token = self.get_token()
        response = self.client.put(
            url_for('api_1.bucketitem',
                    bucketlist_id=1, bucketitem_id=1),
            headers=self.get_api_headers(token, 'password'),
            data=json.dumps({'done': True}))
        self.assertTrue(response.status_code == 200)

    def test_update_bucketitem_name(self):
        # test update a bucketitem name
        token = self.get_token()
        response = self.client.put(
            url_for('api_1.bucketitem',
                    bucketlist_id=1, bucketitem_id=1),
            headers=self.get_api_headers(token, 'password'),
            data=json.dumps({'name': 'I just changed this bucketlist'}))
        self.assertTrue(response.status_code == 200)

    def test_delete_bucketitem(self):
        # test delete a bucketitem
        token = self.get_token()
        response = self.client.delete(
            url_for('api_1.bucketitem',
                    bucketlist_id=1, bucketitem_id=1),
            headers=self.get_api_headers(token, 'password'))
        self.assertTrue(response.status_code == 200)

    # test errors
    def test_get_user_error(self):
        # test non-existing user
        response = self.client.get(
            url_for('api_1.get_user', username='timothy'),
            headers=self.get_api_headers('lade', 'password'))
        self.assertTrue(response.status_code == 400)

    def test_add_bucketlist_error(self):
        # test add empty bucketlist
        response = self.client.post(
            url_for('api_1.bucketlists'),
            headers=self.get_api_headers('lade', 'password'))
        self.assertTrue(response.status_code == 400)

    def test_get_bucketlist_error(self):
        # test get unauthorized access to bucketlist
        response = self.client.get(
            url_for('api_1.bucketlist', bucketlist_id=1),
            headers=self.get_api_headers('dave', 'password'))
        self.assertTrue(response.status_code == 404)

    def test_update_bucketlist_error(self):
        # test get and update unauthorized access to bucketlist
        response = self.client.put(
            url_for('api_1.bucketlist', bucketlist_id=1),
            headers=self.get_api_headers('dave', 'password'),
            data=json.dumps({
                'name': 'I should not have access to this bucketlist'
            }))
        self.assertTrue(response.status_code == 404)

    def test_delete_bucketlist_error(self):
        # test get and delete unauthorized access to bucketlist
        response = self.client.delete(
            url_for('api_1.bucketlist', bucketlist_id=1),
            headers=self.get_api_headers('dave', 'password'))
        self.assertTrue(response.status_code == 404)

    def test_create_bucketitem_error(self):
        # test create bucketitem with unauthorized access to bucketlist
        response = self.client.post(
            url_for('api_1.add_bucketitem', bucketlist_id=1),
            headers=self.get_api_headers('dave', 'password'),
            data=json.dumps({
                'name': 'I should not create an bucketitem in this bucketlist'
            }))
        self.assertTrue(response.status_code == 404)

    def test_update_bucketitem_error(self):
        # test update bucketitem with unauthorized access to bucketlist
        response = self.client.put(
            url_for('api_1.bucketitem',
                    bucketlist_id=1, bucketitem_id=1),
            headers=self.get_api_headers('dave', 'password'),
            data=json.dumps({'done': True}))
        self.assertTrue(response.status_code == 404)

    def test_delete_bucketitem_error(self):
        # test delete bucketitem with unauthorized access to bucketlist
        response = self.client.delete(
            url_for('api_1.bucketitem',
                    bucketlist_id=1, bucketitem_id=1),
            headers=self.get_api_headers('dave', 'password'))
        self.assertTrue(response.status_code == 404)
