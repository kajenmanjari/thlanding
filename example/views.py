from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from concurrent.futures import ThreadPoolExecutor
import json
import requests
from urllib.parse import urlparse


def main_page(request):
    absolute_uri = request.build_absolute_uri('/')
    redirect_url = get_redirect(absolute_uri)

    if(redirect_url == 404):
        return render(request, '404.html')
    else:
       return redirect(redirect_url)

@csrf_exempt
def cta_clicked(request):
    if request.method == "POST":
        # Load the JSON data from the request
        data = json.loads(request.body)

        # Get the uid from the data
        uid = data.get('uid')
        
        update_database(uid, "TH_Lead", "cta_clicked", "1")
        return JsonResponse({"message": "Successful"})

@csrf_exempt
def exit_page(request):
    if request.method == "POST":
        # Load the JSON data from the request
        data = json.loads(request.body)

        # Get the uid and watch time from the data
        uid = data.get('uid')
        watchTime = data.get('watchTime')
        print(watchTime)

        # Update value with maximum watch time
        currentWatch = get_data_field(uid, "TH_Lead", "watch_time")

        if(isinstance(currentWatch, list)):
            if(currentWatch == ['404']):
                # Update Database
                update_database(uid, "TH_Lead", "watch_time", watchTime)
                print("updated watch time")
        else:
            if(float(watchTime) > currentWatch):
                # Update Database
                update_database(uid, "TH_Lead", "watch_time", watchTime)
                print("updated watch time")
        
                
        # Update video watches if watch time > 0.5
        if(watchTime > 0.5):
            num_views = get_data_field(uid, "TH_Lead", "video_views")
            print(num_views)
            
            if(isinstance(num_views, list)):
                if(num_views == ['404']):
                    update_database(uid, "TH_Lead", "video_views", 1)
            else:
                update_database(uid, "TH_Lead", "video_views", num_views + 1)

        
        return JsonResponse({"message": "Successful"})

@xframe_options_exempt
def index(request, slug=None):  # Make slug an optional parameter
    valid_slug = False
    video_title = ''
    video_url = ''
    cta_text = ''
    cta_link = ''
    embed_code = ''
    embed_status = ''
    cta_status = ''
    lead_id = ''

    # Search for a specific field value in the Bubble database
    data_type = "TH_Lead"  
    field_name = "lead_slug"

    data, status = search_data_field(data_type, field_name, slug)

    if status["request_status"] and status["item_found"] and (slug is not None):
        campaign_id = data['campaign_id']
        video_title = data['video_title']
        video_url = data['bucket_url']
        lead_id = data['lead_id']

        # Find other values using campaign_id
        with ThreadPoolExecutor(max_workers=5) as executor:
            future1 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "embed_status")
            future2 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "embed_code")
            future3 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "cta_link")
            future4 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "cta_text")
            future5 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "cta_status")

        embed_status = future1.result()
        embed_code = future2.result()
        cta_link = future3.result()
        cta_text = future4.result()
        cta_status = future5.result()

        if(not("http" in cta_link)):
            cta_link = "https://" + cta_link

        valid_slug = True

    else:
        valid_slug = False

    absolute_uri = request.build_absolute_uri('/')

    if(valid_slug):
        return render(request, 'index.html', {'valid_slug': valid_slug,
                                            'video_title': video_title, 
                                            'lead_id': lead_id,
                                            'video_url': video_url, 
                                            'cta_text': cta_text,
                                            'cta_link': cta_link,
                                            'embed_code': embed_code,
                                            'cta_status': cta_status,
                                            'embed_status': embed_status,
                                            'slug': slug,
                                            'absolute_uri': absolute_uri
                                            })
    # Redirect function
    else: 
        return redirect(absolute_uri)

@xframe_options_exempt
def player(request, slug=None):  # Make slug an optional parameter
    valid_slug = False
    video_title = ''
    video_url = ''
    cta_text = ''
    cta_link = ''
    embed_code = ''
    embed_status = ''
    cta_status = ''
    lead_id = ''

    # Search for a specific field value in the Bubble database
    data_type = "TH_Lead"  
    field_name = "lead_slug"

    data, status = search_data_field(data_type, field_name, slug)

    if status["request_status"] and status["item_found"] and (slug is not None):
        campaign_id = data['campaign_id']
        video_title = data['video_title']
        video_url = data['bucket_url']
        lead_id = data['lead_id']

        # Find other values using campaign_id
        with ThreadPoolExecutor(max_workers=7) as executor:
            future1 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "embed_status")
            future2 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "embed_code")
            future3 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "cta_link")
            future4 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "cta_text")
            future5 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "cta_status")
            future6 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "logo_status")
            future7 = executor.submit(get_data_field, campaign_id, "TH_Campaign", "logo_img")

        embed_status = future1.result()
        embed_code = future2.result()
        cta_link = future3.result()
        cta_text = future4.result()
        cta_status = future5.result()
        logo_status = future6.result()
        logo_url = future7.result()

        valid_slug = True

    else:
        valid_slug = False

    return render(request, 'player.html', {'valid_slug': valid_slug, 
                                          'video_title': video_title,
                                          'lead_id': lead_id, 
                                          'video_url': video_url, 
                                          'cta_text': cta_text,
                                          'cta_link': cta_link,
                                          'embed_code': embed_code,
                                          'cta_status': cta_status,
                                          'embed_status': embed_status,
                                          'slug': slug,
                                          'logo_status': logo_status,
                                          'logo_url': logo_url
                                          })

def search_data_field(data_type, field_name, field_value):
    api_key = "cb49dfd6e576e3153fcf8d3b211698b0"
    search_constraints = [
        {
            "key": field_name,
            "constraint_type": "equals",
            "value": field_value,
        }
    ]
    constraints_json = json.dumps(search_constraints)
    bubble_url = f"https://scalifyv4.bubbleapps.io/version-test/api/1.1/obj/{data_type}?constraints={constraints_json}"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(bubble_url, headers=headers)

    status = {"request_status": False, "item_found": False}

    if response.status_code == 200:
        data = response.json()
        print("Data retrieved successfully!")
        status["request_status"] = True
        if 'response' in data and 'results' in data['response'] and len(data['response']['results']) > 0:
            result_data = data['response']['results'][0]
            if 'campaign_id' in result_data and 'video_title' in result_data and 'bucket_url' and '_id' in result_data:
                status["item_found"] = True
                return {'campaign_id': result_data['campaign_id'], 'video_title': result_data['video_title'], 'bucket_url': result_data['bucket_url'], 'lead_id': result_data['_id']}, status
        print("Error: 'campaign_id', 'video_title' or 'bucket_url' not found in the data.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

    return None, status


# Returns Json File of Data for the Data Entry with the Uniuqe ID
def get_data(unique_id, data_type):
    api_key = "cb49dfd6e576e3153fcf8d3b211698b0"

    bubble_url = f"https://scalifyv4.bubbleapps.io//version-test/api/1.1/obj/{data_type}/{unique_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(bubble_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Data retrieved successfully!")
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return 404

# Returns a data field from data base
def get_data_field(unique_id, data_type, field_name):
    jsondata = get_data(unique_id, data_type)

    if jsondata != 404:
        try:
            lead_list = jsondata['response'][field_name]
            return lead_list
        except:
            print(jsondata)
            message = ["404"]
            return message
    else:
        message = ["404"]
        return message
    
# Updates the database with a new value
def update_database(unique_id, data_type, field_name, new_value):
    api_key = 'cb49dfd6e576e3153fcf8d3b211698b0'


    bubble_url = f"https://scalifyv4.bubbleapps.io/version-test/api/1.1/obj/{data_type}/{unique_id}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {field_name: new_value}
    
    response = requests.patch(bubble_url, json=data, headers=headers)

    if response.status_code == int(204):
        print("Value updated successfully!")
        print(new_value)
        return 204
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return -1

# Updates the database with a new value
def update_database_put(unique_id, data_type, field_name, new_value):
    api_key = 'cb49dfd6e576e3153fcf8d3b211698b0'


    bubble_url = f"https://scalifyv4.bubbleapps.io/version-test/api/1.1/obj/{data_type}/{unique_id}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {field_name: new_value}
    
    response = requests.post(bubble_url, json=data, headers=headers)

    if response.status_code == int(204):
        print("Value updated successfully!")
        print(new_value)
        return 204
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return -1




def get_redirect(absolute_uri):
    # Make main URL in lowercase
    # Take out HTTPS "https://targify.io" -> "targify.io"

    main_url = get_main_url(absolute_uri)

    if(main_url == "Invalid URL"):
        return (404)

    print("main_url: ", main_url)

    # Search main url with https:// and www. removed
    redirect_domain, status = search_for_redirect("custom_domain", "domain_name", main_url)

    if not status['item_found']:
        # Search domain with www.
        new_url = "www." + main_url
        redirect_domain, status = search_for_redirect("custom_domain", "domain_name", new_url)
        
    if not status['item_found']:
        # Search domain with https://
        redirect_domain, status = search_for_redirect("custom_domain", "domain_name", absolute_uri)
    
    if not status['item_found']:
        # Search domain with https://
        redirect_domain, status = search_for_redirect("custom_domain", "domain_name", "http://" + main_url)

    if not status['item_found']:
        return (404)

    if status['item_found']:
        return format_redirect(redirect_domain)

def get_main_url(url):
    url = url.strip()  # Remove leading and trailing whitespace.

    # Prepend with 'http://' if the scheme is missing and if not a path.
    if '://' not in url and not url.startswith('/'):
        url = 'http://' + url
    
    if url.startswith('/'):
        # If the url is a path, strip the slashes and return.
        return url.strip('/')
    else:
        parsed_url = urlparse(url)

        if parsed_url.hostname:
            hostname_parts = parsed_url.hostname.split('.')
            if len(hostname_parts) > 2 and hostname_parts[0] == 'www':
                main_url = '.'.join(hostname_parts[1:])
            else:
                main_url = parsed_url.hostname
            return main_url
        else:
            return "Invalid URL"


def search_for_redirect(data_type, field_name, field_value):
    api_key = "cb49dfd6e576e3153fcf8d3b211698b0"
    search_constraints = [
        {
            "key": field_name,
            "constraint_type": "equals",
            "value": field_value,
        }
    ]
    constraints_json = json.dumps(search_constraints)
    bubble_url = f"https://scalifyv4.bubbleapps.io/version-test/api/1.1/obj/{data_type}?constraints={constraints_json}"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(bubble_url, headers=headers)

    status = {"request_status": False, "item_found": False}

    if response.status_code == 200:
        data = response.json()
        status["request_status"] = True
        if 'response' in data and 'results' in data['response'] and len(data['response']['results']) > 0:
            result_data = data['response']['results'][0]
            if 'redirect' in result_data:
                status["item_found"] = True
                return result_data['redirect'], status
            
    return None, status


def format_redirect(redirect_url):
    main_url = get_main_url(redirect_url)

    # Prepend 'https://' to the main url
    return 'https://' + main_url
