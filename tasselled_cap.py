#!/usr/bin/env python
# coding: utf-8

# In[3]:


get_ipython().system('pip install earthengine-api')


# In[5]:


from IPython.display import Image
import ee, folium
ee.Initialize()


# In[7]:


get_ipython().system('earthengine authenticate')


# In[8]:


from IPython.display import Image
import ee, folium
ee.Initialize()


# In[9]:


image = ee.Image('LANDSAT/LC08/C02/T1_TOA/LC08_137042_20211112')


# In[10]:


# Function
def tasseled_cap_transformation(image):
    b = image.select("B2", "B3", "B4", "B5", "B6", "B7");
    #Coefficients are only for Landsat 8 TOA imagery
    brightness_coefficents= ee.Image([0.3029, 0.2786, 0.4733, 0.5599, 0.508, 0.1872])
    greenness_coefficents= ee.Image([-0.2941, -0.243, -0.5424, 0.7276, 0.0713, -0.1608]);
    wetness_coefficents= ee.Image([0.1511, 0.1973, 0.3283, 0.3407, -0.7117, -0.4559]);
    fourth_coefficents= ee.Image([-0.8239, 0.0849, 0.4396, -0.058, 0.2013, -0.2773]);
    fifth_coefficents= ee.Image([-0.3294, 0.0557, 0.1056, 0.1855, -0.4349, 0.8085]);
    sixth_coefficents= ee.Image([0.1079, -0.9023, 0.4119, 0.0575, -0.0259, 0.0252]);
    
    #Calculate tasseled cap transformation
    brightness = image.expression(
        '(B * BRIGHTNESS)',
        {
            'B':b,
            'BRIGHTNESS': brightness_coefficents
        })
    greenness = image.expression(
        '(B * GREENNESS)',
        {
            'B':b,
            'GREENNESS': greenness_coefficents
        })
    wetness = image.expression(
        '(B * WETNESS)',
        {
            'B':b,
            'WETNESS': wetness_coefficents
        })
    fourth = image.expression(
        '(B * FOURTH)',
        {
            'B':b,
            'FOURTH': fourth_coefficents
        })
    fifth = image.expression(
        '(B * FIFTH)',
        {
            'B':b,
            'FIFTH': fifth_coefficents
        })
    sixth = image.expression(
        '(B * SIXTH)',
        {
            'B':b,
            'SIXTH': sixth_coefficents
        })
    bright = brightness.reduce(ee.call("Reducer.sum"));
    green = greenness.reduce(ee.call("Reducer.sum"));
    wet = wetness.reduce(ee.call("Reducer.sum"));
    four = fourth.reduce(ee.call("Reducer.sum"));
    five = fifth.reduce(ee.call("Reducer.sum"));
    six = sixth.reduce(ee.call("Reducer.sum"));
    tasseled_cap = ee.Image(bright).addBands(green).addBands(wet).addBands(four).addBands(five).addBands(six)
    return tasseled_cap.rename('brightness','greenness','wetness','fourth','fifth','sixth')


# In[11]:


tasseled_cap = tasseled_cap_transformation(image)


# In[12]:


palette = ['FFFFFF','C0C0C0','808080','000000','FF0000','800000','FFFF00','808000','00FF00','008000','00FFFF','008080','0000FF','000080','FF00FF','800080']
palette = ','.join(palette)


# In[13]:


region = tasseled_cap.geometry().getInfo()

vis_tct = {'min':-1,'max':2,'size':'800',
           'bands':['brightness'],
           'palette':palette,
           'region':region}


mapid = tasseled_cap.getMapId(vis_tct)

map = folium.Map(location=[17.49,-95.09],zoom_start=8, height=500,width=700)
folium.TileLayer(
    tiles=mapid['tile_fetcher'].url_format,
    attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
    overlay=True,
    name='Tasseled Cap Transformation Brightness',
  ).add_to(map)

map.add_child(folium.LayerControl())
map


# In[15]:


vis_tct = {'min':-1,'max':2,'size':'800',
           'bands':['greenness'],
           'palette':['ffffe5','f7fcb9','d9f0a3','addd8e','78c679','41ab5d','238443','006837','004529'],
           'region':region}

mapid = tasseled_cap.getMapId(vis_tct)

map = folium.Map(location=[26.16,91.69],zoom_start=8, height=500,width=700)
folium.TileLayer(
    tiles=mapid['tile_fetcher'].url_format,
    attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
    overlay=True,
    name='Tasseled Cap Transformation Greenness',
  ).add_to(map)

map.add_child(folium.LayerControl())
map


# In[18]:


vis_tct = {'min':-1,'max':2,'size':'800',
           'bands':['wetness'],
           'palette':palette,
           'region':region}

mapid = tasseled_cap.getMapId(vis_tct)

map = folium.Map(location=[26.16,91.69],zoom_start=8, height=500,width=700)
folium.TileLayer(
    tiles=mapid['tile_fetcher'].url_format,
    attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
    overlay=True,
    name='Tasseled Cap Transformation Wetness',
  ).add_to(map)

map.add_child(folium.LayerControl())
map


# In[23]:


region = ee.Geometry.Point([91.69, 26.16]).buffer(10000)
export_task = ee.batch.Export.image.toDrive(
    image=tasseled_cap.select(['wetness']),
    description='tct_wetness_export',
    folder='Tasselled_cap',  # Replace with your desired folder in Google Drive
    region=region.bounds(),
    scale=30  # Adjust the scale as needed based on your requirements
)

# Start the export task
export_task.start()


# In[ ]:




