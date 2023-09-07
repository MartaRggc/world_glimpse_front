from dotenv import load_dotenv
import os
import requests
import streamlit as st
import pandas as pd
import numbers
import plost
import geopandas as gpd
import random as rd
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static
import numpy as np

load_dotenv()
api_url = f"{os.environ.get('API_HOST')}:{os.environ.get('API_PORT')}"

# State keys initialization to control the front flow:

if "politics" not in st.session_state:
    st.session_state.politics = False
if "gender" not in st.session_state:
    st.session_state.gender = False
if "economy" not in st.session_state:
    st.session_state.economy = False
if "general" not in st.session_state:
    st.session_state.general = True
if "inequality" not in st.session_state:
    st.session_state.inequality = False
if "footprint" not in st.session_state:
    st.session_state.footprint = False
if "country_view" not in st.session_state:
    st.session_state.country_view = True
if "world_view" not in st.session_state:
    st.session_state.world_view = False


def activate_button(b):
    all_buttons = ['politics', 'gender', 'economy', 'general', 'inequality', 'region', 'footprint']
    st.session_state[b] = True  # We save True for this key
    for i in all_buttons:
        if i != b:
            st.session_state[i] = False  # We save False for the rest


def activate_button_view(b):
    all_buttons = ['country_view', 'world_view']
    st.session_state[b] = True  # We save True for this key
    for i in all_buttons:
        if i != b:
            st.session_state[i] = False  # We save False for the rest

st.title('World glimpse')

COLS = st.columns([1, 1, 1, 1])

with COLS[0]:
    countries_view = st.button('Countries view')

with COLS[1]:
    worldwide_view = st.button('Worldwide view')

if countries_view:
    activate_button_view('country_view')
elif worldwide_view:
    activate_button_view('world_view')


if st.session_state.country_view:
    st.info('In this view mode you will be able to search for individual countries and get their insights.')
    country_options = [i['country_name'] for i in requests.get(f'{api_url}/countries').json()]
    country_selected_name = st.selectbox('Country', country_options)
    country_selected_id = pd.DataFrame(
        requests.get(f'{api_url}/countries').json()
    ).set_index('country_name').to_dict()['country_id'][country_selected_name]

    st.sidebar.title(f'Last news in {country_selected_name}')
    st.sidebar.subheader('##', divider='blue')

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
        sexism_button = st.button('Gender gap')
    with col5:
        economy_button = st.button('Economy')
    with col6:
        inequality_button = st.button('Inequality')

    if general_button:
        activate_button('general')
    elif politics_button:
        activate_button('politics')
    elif footprint_button:
        activate_button('footprint')
    elif sexism_button:
        activate_button('gender')
    elif economy_button:
        activate_button('economy')
    elif inequality_button:
        activate_button('inequality')

    st.write('##')

    if st.session_state.politics:

        try:
            politics = requests.get(f'{api_url}/country/{str(country_selected_id)}/politics').json()
            for i, j in politics.items():
                if j is not None:
                    if i == 'government_type':
                        st.header('Government structure', divider='blue')

                        st.subheader(j)
                    elif i == 'conflict_type':
                        st.write("#")
                        st.header('Ongoing conflicts', divider='red')
                        st.error(j)
                    elif i == 'conflict_description':
                        st.subheader(i.replace('_', ' ').capitalize() + ':')
                        st.write(j)
                    elif i == 'conflict_casualties':
                        st.markdown(f"{i.replace('_', ' ').capitalize()}: :red[{j}]")

                    else:
                        st.write(i.replace('_', ' ').capitalize() + ': ', j)

            if politics['conflict_type'] is None:
                st.write("#")
                st.subheader('Ongoing conflicts', divider='green')
                st.markdown(':green[None]')

        except:
            st.write(default_country)

    elif st.session_state.footprint:

        st.header('General footprint indicators', divider='green')
        st.write('##')
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

                if len(fpcols) > 0:
                    st.subheader('Resources and consumption by sector')
                    st.write('##')
                    col7, col8 = st.columns([1, 1])

                    data1 = {'Names': fpcols, 'Values': fpvals}
                    data2 = {'Names': cols, 'Values': vals}
                    with col7:
                        st.bar_chart(pd.DataFrame(pd.DataFrame(data2).set_index('Names')), color=(0, 150, 0))
                    with col8:
                        st.bar_chart(pd.DataFrame(pd.DataFrame(data1).set_index('Names')), color=(200, 50, 50))

        if w == 0:
            st.write(default_country)

    elif st.session_state.gender:

        ggi = requests.get(f'{api_url}/countries_ggi').json()
        ggi_countries = ggi['countries']
        w = 0

        vals = []
        mvals = []
        cols = []

        for i in ggi_countries:
            if i['country_id'] == country_selected_id:
                w = 1
                c1, c2 = st.columns([1, 1])

                with c1:
                    st.subheader('Global Gender Gap Index:', divider='violet')
                    st.header(i['global_ggi'])

                with c2:
                    st.subheader('Rank within scored countries:')
                    st.header(i['rank_global_ggi'])

                for j, k in i.items():
                    if 'global' not in j and 'id' not in j and 'rank' not in j:
                        vals.append(k)
                        mvals.append(ggi['median_' + j])
                        cols.append(j)

                displayggi = st.selectbox(label='GGI by sectors', options=['Table', 'Chart'])

                if displayggi == 'Table':
                    st.dataframe(
                        pd.DataFrame(
                            [vals, mvals],
                            columns=[i.replace('_', ' ').capitalize() for i in cols],
                            index=[country_selected_name, 'Worldwide median']
                        )
                    )
                elif displayggi == 'Chart':
                    source2 = pd.DataFrame([vals, mvals], columns=cols,
                                           index=[country_selected_name, 'Worldwide median']).T.reset_index()
                    plost.bar_chart(
                        data=source2,
                        bar='index', height=100, width=120,
                        value=[country_selected_name, 'Worldwide median'],
                        legend=False,
                        group=True
                    )

        if w == 0:
            st.write(default_country)

    elif st.session_state.general:

        general_info = requests.get(f'{api_url}/country/{country_selected_id}/general').json()
        st.header(country_selected_name, divider='rainbow')
        try:
            if country_selected_name == 'Iceland':
                st.write("Iceland (Icelandic: Ísland, pronounced [ˈistlant] i)[d] is a Nordic island country between "
                         "the North Atlantic and Arctic Oceans, on the Mid-Atlantic Ridge between North America "
                         "and Europe. It is linked culturally and politically with Europe, and is the region's most "
                         "sparsely populated country.[12] Its capital and largest city is Reykjavík, which is home to "
                         "about 36% of the country's roughly 380,000 residents. The official language of the country "
                         "is Icelandic.")
                st.write('#')

            else:
                st.write('.'.join(general_info['summary'].split('.')[:7]) + '...')
                st.write('#')
        except:
            pass

        if general_info['summary'] is None:
            if country_selected_name == 'Spain':
                st.write("Spain (Spanish: España, [esˈpaɲa] i), or the Kingdom of Spain (Reino de España),[f] is a "
                         "country located in Southwestern Europe, with parts of its territory in the Atlantic Ocean, "
                         "in the Mediterranean Sea and in Africa.[11][g] It is the largest country in Southern Europe "
                         "and the fourth-most populous European Union member state. "
                         "Spanning across the majority of the Iberian Peninsula, its territory also includes the "
                         "Canary Islands in the Atlantic Ocean, the Balearic Islands in the Mediterranean Sea, and the "
                         "autonomous cities of Ceuta and Melilla in Africa. Peninsular Spain is bordered to the north "
                         "by France, Andorra, and the Bay of Biscay; to the east and south by the Mediterranean "
                         "Sea and Gibraltar; and to the west by Portugal and the Atlantic Ocean. ")
                st.write('#')

            else:
                st.info(
                    f"Hi! I'm Wikipedia-API python library. I do make a lot of mistakes.. sorry. I cannot provide you"
                    f" with information about {country_selected_name}. "
                    f"However, check out this other data from restcountries api! :")
                st.write('##')

        c3, c4 = st.columns([1, 1])
        with c3:
            st.subheader('Capital:')
            st.write(general_info['capital'])
            st.subheader('Population:')
            st.write(f"{round(general_info['population'] / (1e6), 2)} M")
            try:
                st.markdown(f"**Languages:** {', '.join([i['name'] for i in general_info['languages']])}")
            except:
                pass
            st.markdown(f"**Area:** {int(general_info['area'])} km²")

        with c4:
            rel_country = st.selectbox('Population and size in terms of..', options=country_options)
            rel_country_id = pd.DataFrame(
                requests.get(f'{api_url}/countries').json()
            ).set_index('country_name').to_dict()['country_id'][rel_country]
            general_rel_info = requests.get(f'{api_url}/country/{rel_country_id}/general').json()
            rel_pop = round(general_info['population'] / general_rel_info['population'], 2)
            rel_size = round(general_info['area'] / general_rel_info['area'], 2)
            st.subheader(f"{rel_pop} times")
            st.write(f"the population of {rel_country}.")
            st.subheader(f"{rel_size} times")
            st.write(f"the size of {rel_country}.")



    elif st.session_state.economy:

        w = 0
        gdp = requests.get(f'{api_url}/countries_gdp').json()
        countries_gdp = gdp['countries']

        for i in countries_gdp:
            if i['country_id'] == country_selected_id:
                w = 1
                st.subheader('Total annual Gross Domestic Product, GDP (USD$)', divider='orange')

                c5, c6 = st.columns([1, 1])
                with c5:
                    tgdp = i['total_gdp']
                    if tgdp < 1e6:
                        st.header(f"{tgdp / (1e3)} K")
                    elif tgdp > 1e6 and tgdp < 1e9:
                        st.header(f"{tgdp / (1e6)} M")
                    else:
                        st.header(f"{tgdp / (1e9)} B")
                    st.subheader(f"World share:  {round(100 * i['world_share'], 2)} %")
                    st.write("#")
                    st.subheader("GDP per capita", divider='blue')
                    source3 = pd.DataFrame([i['gdp_capita'], i['ppp_gdp_capita'], gdp['median_ppp_gdp_capita']],
                                           index=['Country GDP per capita', 'Per capita (PPP)',
                                                  'Worldwide median (PPP)']).T.reset_index()
                    plost.bar_chart(
                        data=source3,
                        bar='index', height=100, width=120,
                        value=['Country GDP per capita', 'Per capita (PPP)', 'Worldwide median (PPP)'],
                        legend=False,
                        group=True
                    )

        if w == 0:
            st.write(default_country)


    elif st.session_state.inequality:

        w = 0
        ineq = requests.get(f'{api_url}/countries_inequality').json()
        countries_ineq = ineq['countries']

        for i in countries_ineq:
            if i['country_id'] == country_selected_id:
                w = 1
                st.header('General indicators', divider='grey')
                if i['gini_coefficient'] is not None:
                    st.info('The Gini index is a measure of statistical dispersion intended to '
                            'represent the income inequality, the wealth inequality, or the consumption inequality '
                            'within a nation or a social group. A gini value of 0% reflects perfect equality and'
                            'one of 100% represents maximum inequality '
                            '(see its [definition](https://en.wikipedia.org/wiki/Gini_coefficient)).')
                colss = st.columns([1, 1, 1])
                toplot = [i['gini_coefficient'], i['richest_10_percent_share'], i['richest_1_percent_share']]
                names = ['Gini index (%):', 'Richest 10% share', 'Richest 1% share']

                a = 0
                for l in range(3):
                    if toplot[l] is not None:
                        with colss[a]:
                            st.subheader(names[l])
                            st.header(toplot[l])
                            a += 1

                if isinstance(i['vulnerable_MP_pop'], float):
                    st.write('#')
                    st.subheader('Multidimensional poverty (MP)', divider='red')
                    st.warning(f"{country_selected_name} is a country with a multidimensional poverty problem. "
                               f"\nA person is considered to be MP poor when is deprived in a third or more of several indicators, "
                               f"concerning health, education and living standard (see [ref](https://ophi.org.uk/multidimensional-poverty-index/)).")
                    col7, col8 = st.columns([1, 1])

                    with col7:
                        st.subheader('Population at MP risk:')
                        st.header(f"{round(i['vulnerable_MP_pop'], 2)} %")
                    with col8:
                        st.subheader('Av. intensity of depravation:')
                        st.header(f"{round(i['intensity_depravation_perc'], 2)} %")

                    st.write("#")
                    st.subheader('Poverty contribution of each dimension (%)', divider='green')
                    data = {
                        'Names': ['Education', 'Health', 'Living standard'],
                        'Values': [
                            i['education_contribution'],
                            i['health_contribution'],
                            i['living_standard_contribution']
                        ]
                    }

                    st.bar_chart(pd.DataFrame(pd.DataFrame(data).set_index('Names')), color=(0, 50, 100))

        if w == 0:
            st.write(default_country)

    try:
        news = requests.get(f'{api_url}/country/{str(country_selected_id)}/news').json()
        if len(news) > 0:
            for i in news:
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

else:

    ##### KEPLER MAP
    st.info('In this view mode you can compare all countries regarding a reference indicator of each category.')

    ccol1, ccol2, ccol3, ccol4, ccol5, ccol6 = st.columns([1, 1, 1, 1, 1, 1])

    with ccol1:
        conflicts_bbuton = st.button(' Conflicts ')  # Population
    with ccol2:
        politics_bbutton = st.button(' Politics ')  # Government type
    with ccol3:
        footprint_bbutton = st.button(' Footprint ')  # Total footprint
    with ccol4:
        sexism_bbutton = st.button(' Gender gap ')  # Gender Gap Index
    with ccol5:
        economy_bbutton = st.button(' Economy ')  # PPP GPD per capita
    with ccol6:
        inequality_bbutton = st.button(' Inequality ')  # Gini Index


    map = 0

    # Load geospatial data (multipolygon):
    mex = gpd.read_file('countries_geo.geojson')

    # Add country names (tagged only with id yet):
    mex['Country Name'] = [pd.DataFrame(requests.get(f'{api_url}/countries').json()).set_index('country_id').to_dict()
                           ['country_name'][i] for i in mex.country_id]

    if conflicts_bbuton:
        conflict_state = []

        def get_conflict(i):
            conf = requests.get(f'{api_url}/country/{str(i)}/politics').json()['conflict_type']
            if conf is None:
                return 'No declared conflicts'
            else:
                return 'At current conflict'

        mex['Peace status'] = mex.country_id.apply(get_conflict)
        mex = mex.dropna()
        mex = mex.drop(columns='country_id')

        color = 'Peace status'
        var_type = 'string'
        scale = 'ordinal'
        label = 'Political stability'

    elif politics_bbutton:
        political_system = []
        for i in mex['country_id']:
            gov_struct = requests.get(f'{api_url}/country/{str(i)}/politics').json()['government_type']
            political_system.append(gov_struct)

        mex['Political system'] = [i for i in political_system]
        mex = mex.dropna()
        mex = mex.drop(columns='country_id')

        color = 'Political system'
        var_type = 'string'
        scale = 'ordinal'
        label = 'Political structure'

    elif footprint_bbutton:
        c_footprints = []
        all_footprints = requests.get(f'{api_url}/countries_footprint').json()['countries']
        data_fp = pd.DataFrame(all_footprints)
        for i in mex['country_id']:
            try:
                c_footprints.append(data_fp[data_fp.country_id == i]['number_of_earths_required'].iloc[0])
            except:
                c_footprints.append(None)

        mex['Earths required'] = [i for i in c_footprints]
        mex = mex.dropna()
        mex = mex.drop(columns='country_id')

        color = 'Earths required'
        var_type = 'real'
        scale = 'linearGradient'
        label = 'Ecological footprint'

    elif sexism_bbutton:
        c_genders = []
        all_ggi = requests.get(f'{api_url}/countries_ggi').json()['countries']
        data_fp = pd.DataFrame(all_ggi)
        for i in mex['country_id']:
            try:
                c_genders.append(data_fp[data_fp.country_id == i]['global_ggi'].iloc[0])
            except:
                c_genders.append(None)

        mex['Gender Gap index, GGI'] = [i for i in c_genders]
        mex = mex.dropna()
        mex = mex.drop(columns='country_id')

        color = 'Gender Gap index, GGI'
        var_type = 'real'
        scale = 'linearGradient'
        label = 'Gender Gap'

    elif economy_bbutton:
        c_ecos = []
        all_ec = requests.get(f'{api_url}/countries_gdp').json()['countries']
        data_fp = pd.DataFrame(all_ec)
        for i in mex['country_id']:
            try:
                c_ecos.append(data_fp[data_fp.country_id == i]['ppp_gdp_capita'].iloc[0])
            except:
                c_ecos.append(None)

        mex['GDP per capita (PPP)'] = [i for i in c_ecos]
        mex = mex.dropna()
        mex = mex.drop(columns='country_id')

        color = 'GDP per capita (PPP)'
        var_type = 'real'
        scale = 'linearGradient'
        label = 'Gross Domestic Product'

    else:
        c_ineq= []
        all_in = requests.get(f'{api_url}/countries_inequality').json()['countries']
        data_fp = pd.DataFrame(all_in)
        for i in mex['country_id']:
            try:
                c_ineq.append(data_fp[data_fp.country_id == i]['gini_coefficient'].iloc[0])
            except:
                c_ineq.append(None)

        mex['Gini index'] = [i for i in c_ineq]
        mex = mex.dropna()
        mex = mex.drop(columns='country_id')

        color = 'Gini index'
        var_type = 'real'
        scale = 'linearGradient'
        label = 'Economic inequality'



    map_1 = KeplerGl(height=500, width=2000)
    map_1.add_data(data=mex.copy(), name='World View')

    map_1.config = {
        "version": "v1",
        "config": {
            "visState": {
                "layers": [
                    {
                        "type": "geojson",
                        "config": {
                            "dataId": "World View",
                            "label": label,
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
                                    "name": color,
                                    "type": var_type
                                },
                                "colorScale": scale
                            }
                        },
                        "visualChannels": {
                            "colorField": {"name": color, "type": var_type},
                            "colorScale": scale
                        }
                    }
                ]
            }
        }
    }

    keplergl_static(map_1, center_map=True)
