from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from .models import NewsStory, Author
from datetime import datetime
import json
import uuid


# LOGIN
@csrf_exempt
@require_POST
def login_request(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    try:
        author = Author.objects.get(username=username, password=password)
        login_token = str(uuid.uuid4())
        print(f"Generated login token for {author.name}: {login_token}")
        
        author.login_token = login_token
        author.save()
        response = HttpResponse(f"Welcome, {author.name}!", status=200, content_type='text/plain')
        response.set_cookie('login_token', login_token, httponly=True, secure=True, samesite='Lax')

        return response
    except Author.DoesNotExist:
        return HttpResponse("Invalid username or password", status=401, content_type='text/plain')
    
    
# LOGOUT
@csrf_exempt
@require_POST
def logout_request(request):
    try:
        
        login_token = request.COOKIES.get('login_token')

        if login_token:
            Author.objects.filter(login_token=login_token).update(login_token=None)

        response = HttpResponse("You have been successfully logged out.", status=200, content_type='text/plain')
        response.delete_cookie('login_token')

        return response
    except Exception as e:
        return HttpResponse(f"An error occurred during logout: {str(e)}", status=500, content_type='text/plain')
    
    
# POST STORY & GET STORY
@csrf_exempt
@require_http_methods(["GET", "POST"])
def stories(request):
    
    if request.method == 'POST':
        login_token = request.COOKIES.get('login_token')
        
        if not login_token:
            return HttpResponse('Error: No active session found', status = 401, content_type = 'text/plain')
        
        try:
            author = Author.objects.get(login_token = login_token)
        except Author.DoesNotExist:
            return HttpResponse("Unauthorised", status = 503, content_type = 'text/plain')
        
        try:
            story_data = json.loads(request.body)
            new_story = NewsStory.objects.create(
                headline = story_data.get('headline'),
                category = story_data.get('category'),
                region = story_data.get('region'),
                details = story_data.get('details'),
                author = author,
                date = timezone.now()
            )
            
            return JsonResponse({'message': 'Story posted successfully', 'story_id': new_story.id}, status=201)
        
        except Exception as e:
            return HttpResponse(f"Error posting: {str(e)}", status=503, content_type='text/plain')
        
    elif request.method == 'GET':
        try:
            
            category = request.GET.get('category', None)
            region = request.GET.get('region', None)
            date_str = request.GET.get('date', None)
            
            stories_query = NewsStory.objects.all()

            if category:
                stories_query = stories_query.filter(category=category)
            if region:
                stories_query = stories_query.filter(region=region)
            if date_str:
                date_filter = datetime.strptime(date_str, '%Y-%m-%d').date()
                stories_query = stories_query.filter(date=date_filter)

            story = stories_query.first()

            if not story:
                return HttpResponse("No story found matching the criteria.", status=404, content_type='text/plain')

            story_data = {
                "key": str(story.pk),
                "headline": story.headline,
                "category": story.category,
                "region": story.region,
                "author": story.author.name,
                "date": story.date.strftime('%Y-%m-%d'),
                "details": story.details,
            }

            return JsonResponse({"story": story_data}, status=200)

        except Exception as e:
            return HttpResponse(f"Error processing request: {str(e)}", status=500, content_type='text/plain')  
    

# GET ALL STORIES
@csrf_exempt
@require_GET
def get_all_stories(request):
    try:
        
        stories = NewsStory.objects.all()

        stories_data = [{
            "key": str(story.pk),
            "headline": story.headline,
            "category": story.category,
            "region": story.region,
            "author": story.author.name,
            "date": story.date.strftime('%Y-%m-%d'),
            "details": story.details,
        } for story in stories]

        if not stories:
            return HttpResponse("No stories found.", status = 404, content_type='text/plain')

        return JsonResponse({"stories": stories_data}, safe = False, status = 200)

    except Exception as e:
        return HttpResponse(f"Error processing request: {str(e)}", status = 500, content_type = 'text/plain')

    
# DELETE STORY
@csrf_exempt
@require_http_methods(['DELETE'])
def delete_story(request, key):
    login_token = request.COOKIES.get('login_token')
    
    if not login_token:
        return HttpResponse("You're not logged in! Can't delete that story..", status = 503, content_type = 'text/plain')
    
    try:
       
        author = Author.objects.get(login_token = login_token)
    except Author.DoesNotExist:
        return HttpResponse("Unauthorized: Invalid token.", status = 503, content_type='text/plain')

    try:
        story = NewsStory.objects.get(pk = key, author = author)
    except NewsStory.DoesNotExist:
        return HttpResponse("No story found with the given key or you're not the author of the story.", status = 503, content_type='text/plain')

    try:
        story.delete()
        return HttpResponse("Story deleted successfully.", status = 200, content_type = 'text/plain')
    except Exception as e:
        return HttpResponse(f"Error processing request: {str(e)}", status = 503, content_type = 'text/plain')