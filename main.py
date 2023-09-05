from dotenv import load_dotenv
import os

import requests
import streamlit as st
import pandas as pd
import geopandas as gpd
from keplergl import KeplerGl
import random as rd
import numpy as np
import numbers
import plost

load_dotenv()

# st.set_page_config(layout="wide")
st.title('Clase Streamlit')
st.sidebar.header('Last news')
st.sidebar.write('##')

mex = gpd.read_file('mexico.geojson')  # cargar datos geoespaciales (multipolygon)
mex = mex.rename(columns={'name': 'estado'})
mex = mex.drop(columns=['created_at', "updated_at", "cartodb_id"])
mex['color'] = [rd.random() for i in range(mex.shape[0])]
mex.iloc[20, 1] = np.NaN
mex.iloc[20, 2] = np.NaN

map_1 = KeplerGl(height=300, width=1000)
map_1.add_data(data=mex.copy(), name='Mexico States')

map_1.config = {
    "version": "v1",
    "config": {
        "visState": {
            "layers": [
                {
                    "type": "geojson",
                    "config": {
                        "dataId": "Mexico States",
                        "label": "Estado",
                        "columns": {
                            "geojson": "geometry"
                        },
                        "isVisible": True,
                        "visConfig": {
                            "opacity": 0.8,
                            "strokeOpacity": 0.8,
                            "thickness": 0.5,
                            "strokeColor": [218, 112, 191],
                            "filled": True,
                            "colorField": {
                                "name": "color",
                                "type": "real"
                            },
                            "colorScale": "ordinal",
                            "strokeColorRange": {
                                "name": "ColorBrewer YlOrRd-6",
                                "type": "sequential",
                                "category": "ColorBrewer",
                                "colors": [
                                    "#FFFFB2",
                                    "#FED976",
                                    "#FEB24C",
                                    "#FD8D3C",
                                    "#FC4E2A",
                                    "#E31A1C"
                                ]
                            }
                        }
                    },
                    "visualChannels": {
                        "colorField": {"name": "color", "type": "real"},
                        "colorScale": "ordinal"
                    }
                }
            ]
        }
    }
}

api_url = f"{os.environ.get('API_HOST')}:{os.environ.get('API_PORT')}"

region_options = [i['region_name'] for i in requests.get(f'{api_url}/regions').json()]
region_selected_name = st.selectbox('Region', region_options)
region_selected_id = pd.DataFrame(
    requests.get(
        f'{api_url}/regions'
    ).json()).set_index('region_name').to_dict()['region_id'][region_selected_name]
country_options = [
    i['country_name'] for i in requests.get(f'{api_url}/countries').json()
    if i['region_id'] == region_selected_id
]
country_selected_name = st.selectbox('Country', country_options)
country_selected_id = pd.DataFrame(
    requests.get(f'{api_url}/countries').json()
).set_index('country_name').to_dict()['country_id'][country_selected_name]

default_country = 'No info available for this country.'
default_region = 'No info available for this region.'

col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

with col1:
    general_button = st.button('General')
with col2:
    politics_button = st.button('Politics')
with col3:
    footprint_button = st.button('Footprint')
with col4:
    sexism_button = st.button('Sexism')
with col5:
    economy_button = st.button('Economy')
with col6:
    inequality_button = st.button('Inequality')

news_text = 'economy'

if politics_button:
    news_text = 'politic'
    try:
        politics = requests.get(f'{api_url}/country/{str(country_selected_id)}/politics').json()
        for i, j in politics.items():
            if j is not None:
                if i == 'government_type':
                    st.header(i.replace('_', ' ').capitalize() + ': ')
                    st.subheader(j)
                elif i == 'conflict_type':
                    st.write("#")
                    st.header('Ongoing conflicts:')
                    st.error(j)

                else:
                    st.write(i.replace('_', ' ').capitalize() + ': ', j)

        if politics['conflict_type'] is None:
            st.write("#")
            st.subheader('Ongoing conflicts:')
            st.write('None')

    except:
        st.write(default_country)


elif footprint_button:
    news_text = 'footprint'
    st.subheader('General data')
    footprint = requests.get(f'{api_url}/countries_footprint').json()
    footprint_countries = footprint['countries']
    w = 0
    for i in footprint_countries:
        if i['country_id'] == country_selected_id:
            w = 1
            fpvals = []
            fpmedian_vals = []
            fpcols = []

            vals = []
            median_vals = []
            cols = []

            cvals = []
            cmedian_vals = []
            ccols = []

            columns = st.columns([1, 1])
            a = 0

            for j, k in i.items():
                if j != 'country_id' and k is not None:
                    if 'reserve' not in j and 'total' not in j and 'number' not in j:
                        if 'footprint' in j:
                            fpvals.append(k)
                            fpmedian_vals.append(footprint['median_' + j])
                            fpcols.append(j.replace('_', ' ').replace('consumption', '').capitalize())
                        else:
                            if isinstance(k, numbers.Number):
                                vals.append(k)
                                median_vals.append(footprint['median_' + j])
                                cols.append(j.replace('_', ' ').capitalize())

                            else:
                                with columns[0]:
                                    st.write(j.replace('_', ' ').capitalize() + ':', k)

                    elif 'total' in j:
                        cvals.append(k)
                        cmedian_vals.append(footprint['median_' + j])
                        ccols.append(j.replace('_', ' ').replace('consumption', '').capitalize())

                    else:
                        with columns[0]:
                            st.write(j.replace('_', ' ').capitalize() + ':', k)

            with columns[1]:
                source1 = pd.DataFrame([cvals, cmedian_vals], columns=ccols,
                                       index=[country_selected_name, 'Worldwide median']).T.reset_index()
                plost.bar_chart(
                    data=source1,
                    bar='index', height=100, width=120,
                    value=[country_selected_name, 'Worldwide median'],
                    legend=False,
                    group=True
                )

            data1 = {
                'Names': fpcols,
                'Values': fpvals
            }

            data2 = {
                'Names': cols,
                'Values': vals
            }

            st.subheader('Resources and consumption')
            st.write('##')
            col7, col8 = st.columns([1, 1])

            with col7:
                st.bar_chart(pd.DataFrame(pd.DataFrame(data2).set_index('Names')), color=(0, 150, 0))
            with col8:
                st.bar_chart(pd.DataFrame(pd.DataFrame(data1).set_index('Names')), color=(200, 50, 50))

    if w == 0:
        st.write(default_country)

try:
    news = requests.get(f'{api_url}/country/{str(country_selected_id)}/{news_text}/news').json()
    if len(news) > 0:
        for i in news[:5]:
            try:
                st.sidebar.subheader(i.get('title'))
                st.sidebar.write('Publish date: ', i.get('publish_date'))
                st.sidebar.info(i.get('text')[:300] + '...')
                st.sidebar.write('Author:', i.get('author'))
                st.sidebar.write('Article url:', i.get('url'))
                st.sidebar.write('##')
            except:
                pass
    else:
        st.sidebar.write('No news.')

except:
    st.sidebar.write('Limit of requests to news api exceeded.')

# keplergl_static(map_1)
