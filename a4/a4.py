"""
Strava Heatmap Generator

This module contains functions to work with the Strava API and create an interactive heatmap.
It allows you to fetch activities, extract GPS coordinates, and generate a heatmap using Folium.

Usage:
    Import the module to use the functions, get Strava data and make maps with the following functions:

from strava_heatmap import get_strava_activities, extract_gps_points, create_density_heatmap
    
    activities = get_strava_activities(client_id, client_secret, refresh_token)
    gps_points = extract_gps_points(activities)
    create_density_heatmap(gps_points, center_lat, center_lon)

    Note: You need a Strava API to use these functions. I wont post my Strava API here but will include it in the BB message, but you can also get your own from the Strava developer portal under Strava setting online.

Example:
    import strava_heatmap_utils as shu
    activities = shu.get_activities_in_area(token, lat, lon, radius)
    coordinates = shu.get_activity_coordinates(token, activity_id)
    map_obj = shu.create_route_overlay_map(coordinates_list)
"""
import requests
import pandas as pd
import folium
from folium.plugins import HeatMap
import polyline
import time


def get_strava_activities(client_id, client_secret, refresh_token, max_detailed=100):
   """
   Fetch Strava activities using API info, including detailed data for full polylines.
   
   Args:
       client_id (str): Strava client ID
       client_secret (str): Strava client secret  
       refresh_token (str): Strava refresh token
       max_detailed (int): Maximum number of activities to fetch detailed data for
       
   Returns:
       list: Detailed activity data from Strava API with full polylines
   """
   # Get access token
   auth_data = {
       'client_id': client_id,
       'client_secret': client_secret,
       'refresh_token': refresh_token,
       'grant_type': 'refresh_token'
   }
   auth_response = requests.post("https://www.strava.com/oauth/token", data=auth_data)
   access_token = auth_response.json()['access_token']
   
   # Get activity IDs only
   headers = {'Authorization': f'Bearer {access_token}'}
   params = {'page': 1, 'per_page': max_detailed}
   
   response = requests.get("https://www.strava.com/api/v3/activities", headers=headers, params=params)
   
   # Check if the request was successful
   if response.status_code != 200:
       print(f"Failed to fetch activities. Status code: {response.status_code}")
       print(f"Response: {response.text}")
       return []
   
   basic_activities = response.json()
   
   # Check if we got actual activity data
   if not basic_activities:
       print("No activities found in response")
       return []
   
   # Check if first item is a dict (proper activity data)
   if not isinstance(basic_activities[0], dict):
       print("API returned unexpected data format - likely hit rate limit")
       print(f"Response: {basic_activities}")
       return []
   
   print(f"Found {len(basic_activities)} activities, fetching detailed data...")
   
   # Get detailed data for each activity
   detailed_activities = []
   
   for i, activity in enumerate(basic_activities):
       try:
           detail_response = requests.get(f"https://www.strava.com/api/v3/activities/{activity['id']}", 
                                        headers=headers)
           
           if detail_response.status_code == 200:
               detailed_activities.append(detail_response.json())
               if (i + 1) % 10 == 0:
                   print(f"Fetched {i+1}/{len(basic_activities)} activities")
           else:
               print(f"Failed to fetch activity {activity['id']}: Status {detail_response.status_code}")
           
           time.sleep(0.1)  # Rate limit protection
           
       except Exception as e:
           print(f"Error fetching activity {activity['id']}: {e}")
           continue
   
   print(f"Retrieved {len(detailed_activities)} detailed activities")
   return detailed_activities


def extract_gps_points(activities_data):
    """
    Extract GPS coordinates from activity data using higher resolution polyline data.
    
    Args:
        activities_data (list): Activity data from Strava
        
    Returns:
        list: [latitude, longitude] coordinate pairs
    """
    gps_points = []
    full_polyline_count = 0
    summary_polyline_count = 0
    
    for activity in activities_data:
        if activity.get('map'):
            # Try to use full polyline first (higher resolution)
            if activity['map'].get('polyline'):
                decoded_points = polyline.decode(activity['map']['polyline'])
                for point in decoded_points:
                    gps_points.append([point[0], point[1]])
                full_polyline_count += 1
            # Fallback to summary_polyline if full polyline not available
            elif activity['map'].get('summary_polyline'):
                decoded_points = polyline.decode(activity['map']['summary_polyline'])
                for point in decoded_points:
                    gps_points.append([point[0], point[1]])
                summary_polyline_count += 1
    
    print(f"Extracted {len(gps_points)} GPS points")
    print(f"Used full polyline for {full_polyline_count} activities")
    print(f"Used summary polyline for {summary_polyline_count} activities")
    return gps_points

def create_density_heatmap(gps_points, map_center_lat, map_center_lon, output_file="strava_heatmap.html"):
    """
    Create interactive heatmap from GPS coordinates with refined styling, legend, and scale bar.
    
    Args:
        gps_points (list): [lat, lon] coordinate pairs
        map_center_lat (float): Map center latitude
        map_center_lon (float): Map center longitude
        output_file (str): Output HTML filename
        
    Returns:
        folium.Map: Generated heatmap
    """
    m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=11)
    
    # Create refined heatmap with reduced blur
    HeatMap(
        gps_points,
        radius=8,        # Smaller radius for less blur
        blur=7,           # Less blur for sharper edges
        min_opacity=0.4   # Better visibility
    ).add_to(m)
    
    # Add simple legend
    legend_html = '''
    <div style="position: fixed; 
            top: 10px; right: 10px; width: 120px; height: 90px; 
            background-color: white; border: 2px solid grey; z-index:9999; 
            font-size: 12px; padding: 8px;">
<p><b>Activity Density</b></p>
<div style="background: linear-gradient(to right, blue, green, yellow, red); 
            height: 20px; width: 100px; margin: 5px 0;"></div>
<div style="display: flex; justify-content: space-between; width: 100px;">
    <span>Low</span>
    <span>High</span>
</div>
</div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
         
    m.save(output_file)
    
    print(f"Heatmap saved as {output_file}")