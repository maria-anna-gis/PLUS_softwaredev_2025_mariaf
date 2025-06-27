# A4: Modules, functions and imports
## Strava API Heatmap Visualization with Route Overlay Analysis
*Practice: Software Development (Python)*
**Author: Maria Fedyszyn**
---
For this assignment, I created a Python module which inteerfaces with the Strava API to fetch activity data, making it possible to generate interactive heatmap visualisations. The routes are visualised as overlapping low resolution polylines on an interactive map, showing general activity density patterns in specific geographic areas. This feeds well into my groups' final project on building a detailed customised Strava dashboard.
---
## Features
- **Fetch** Strava activities using Strava API
- **Extract** detailed GPS coordinate streams from individual activities
- **Visualise** multiple route overlays on interactive maps with folium heatmap
- **Export** results as an HTML map for offline viewing

---

### Strava API Setup
1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Create a new application
3. Follow guidance to authenticate the API
4. Replace null tokens in the notebook with personal values

It is not reccomended to commit online token info for privacy reasons!

---
## Functions Overview

### 1. `get_strava_activities(client_id, client_secret, refresh_token, max_detailed=100)`
Fetches Strava activities near a specific location within a given radius.
- **Input**: Strava API details and number of activities requested
- **Output**: Detailed activity polylines

### 2. `extract_gps_points(activities_data)`
Retrieves detailed GPS coordinates using the high res polylines.
- **Input**: Activity data list
- **Output**: coordinate pairs

### 3. `create_density_heatmap(gps_points, map_center_lat, map_center_lon, output_file="strava_heatmap.html")`
Creates an interactive map with multiple route overlays showing activity density.
- **Input**: GPS coord pairs, map lat and long for centering, and html output filename
- **Output**: folium heatmap 

---
## File Structure
```
A4/
├── a4.py    # Main module with API functions
├── a4.ipynb  # Jupyter notebook demonstration
├── environment.yml            # Conda environment setup
└── README.md                  # This file
```

---
## Dependencies
- **pandas**: Data manipulation and analysis
- **requests**: HTTP requests for Strava API
- **folium**: Interactive map visualization
- **polyline**: Polylines from the Strava API
- **time**: Required to avoid timing out the API
- **jupyter**: Notebook environment
