from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Author, NewsStory
import json


class ViewTestCases(TestCase):
    def setUp(self):
        # Set up a test author in the database
        self.test_author = Author.objects.create(name="Chen Ve Co", username="vecochen", password="Veco123@", login_token="dummy_token")
        
        self.news_story = NewsStory.objects.create(
            headline = "First story !!",
            category="tech",
            region="eu",
            details="This course is killing me",
            author=self.test_author,
            date=timezone.now()
        )


    def test_login_success(self):
        
        login_url = reverse('login') 
        login_data = {'username': 'vecochen', 'password': 'Veco123@'}

        response = self.client.post(login_url, data = json.dumps(login_data), content_type = 'application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome, Chen Ve Co!", response.content.decode())


    def test_login_failure(self):
        
        login_url = reverse('login')  
        login_data = {'username': 'vecochen', 'password': 'wrongpassword'}

        response = self.client.post(login_url, data = json.dumps(login_data), content_type = 'application/json')

        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid username or password", response.content.decode())
    
    
    def test_logout(self):
        
        logout_url = reverse('logout') 

        self.client.cookies.load({'login_token': self.test_author.login_token})

        response = self.client.post(logout_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("You have been successfully logged out.", response.content.decode())

        updated_author = Author.objects.get(username="vecochen")
        self.assertIsNone(updated_author.login_token)

        self.assertTrue('login_token' not in self.client.cookies or self.client.cookies['login_token'].value == '')
        
        
    def test_post_story(self):
        
        post_story_url = reverse('stories') 

        self.client.cookies.load({'login_token': self.test_author.login_token})
        print (self.test_author.login_token)

        story_data = {
            'headline': 'Test Headline',
            'category': 'tech',
            'region': 'eu',
            'details': 'Test details of the story.'
        }

        response = self.client.post(post_story_url, data=json.dumps(story_data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertIn('Story posted successfully', response_data['message'])
        self.assertTrue('story_id' in response_data)

        self.assertTrue(NewsStory.objects.filter(id=response_data['story_id']).exists())
        
        
    def test_get_all_stories(self):
        
        get_stories_url = reverse('all_stories')

        response = self.client.get(get_stories_url)

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data["stories"]), 1)  
        
    
    def test_get_story_by_filter(self):
       
        story_date_str = self.news_story.date.strftime('%Y-%m-%d')
        get_story_url = reverse('stories') + f'?category={self.news_story.category}&region={self.news_story.region}&date={story_date_str}'

        response = self.client.get(get_story_url)

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertEqual(response_data["story"]["key"], str(self.news_story.pk))
        self.assertEqual(response_data["story"]["headline"], self.news_story.headline)
        self.assertEqual(response_data["story"]["category"], self.news_story.category)
        self.assertEqual(response_data["story"]["region"], self.news_story.region)
        self.assertEqual(response_data["story"]["author"], self.test_author.name)
        self.assertEqual(response_data["story"]["date"], story_date_str)
        self.assertEqual(response_data["story"]["details"], self.news_story.details)
    
    


