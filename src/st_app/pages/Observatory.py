#-------------- Imports ----------------------#
import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import folium as fo
from folium.plugins import MarkerCluster


st.set_page_config(layout="wide")
st.title('Observatory page 🔍')
# Calculate figure width and height dynamically based on window width
WIN_WIDTH = st.sidebar.number_input('Enter window width (height is 40% of width)', value=1200)
FIG_WIDTH = 0.9 * WIN_WIDTH  # 90% of window width or maximum of 800 pixels
FIG_HEIGHT = 0.4 * FIG_WIDTH  # Maintain aspect ratio

@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath)
    list_drop_cols = ['RSI', 'ΑΙΤΗΣΗ', 'ΑΡ. ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ ΡΑΕ', 'ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ', 'ΔΗΜΟΣ ', 'ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ',
                      'ΘΕΣΗ', 'RSI_ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ', 'RSI_ΔΗΜΟΣ ', 'RSI_ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ', 'RSI_ΘΕΣΗ', 'ΔΙΑΡΚΕΙΑ',
                      'ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ', 'ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ', 'ΕΤΑΙΡΕΙΑ']
    df.drop(columns=list_drop_cols, inplace=True)
    df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'] = pd.to_datetime(df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    return df

df = load_data('/home/marios/projects/RAE_Forecasting/data/processed_data/all_ape_data_nodup_rsi.csv')

# Sidebar for selecting date range
st.sidebar.header('Filter Data')
start_date = st.sidebar.date_input('Start date', df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'].min(), min_value=df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'].min(), max_value=df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'].max())
end_date = st.sidebar.date_input('End date', df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'].max(), min_value=df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'].min(), max_value=df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'].max())

# Filter the dataframe based on the selected date range
df = df[(df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'] >= pd.to_datetime(start_date)) & 
                 (df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'] <= pd.to_datetime(end_date))]


#----------------------------------------------- 1 PERMITS THE YEARS -------------------------------------------------------------------------#
st.header('Χρονοδιάγραμμα αδειών ΑΠΕ')
time_permits = df.copy()
time_permits = time_permits.set_index('ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ')
time_permits = time_permits.sort_index()
time_permits.index = time_permits.index.to_series()#.apply(lambda x: x + pd.DateOffset(years=25) if x in time_permits.index[:4] else x)
time_permits = time_permits.sort_index()


grouped_df = time_permits.groupby([pd.Grouper(freq='M'), 'ΤΕΧΝΟΛΟΓΙΑ']).size().unstack(fill_value=0)

all_options = grouped_df.columns
all_regions = ['All Regions'] + df['ΠΕΡΙΦΕΡΕΙΑ'].unique().tolist()
options_line_chart = st.multiselect("Επιλογή ΑΠΕ",all_options,[])

if len(options_line_chart) < 1:
      options_line_chart = all_options

linechart_df = grouped_df.loc[:,options_line_chart]
fig_linechart = go.Figure()

for col in linechart_df.columns:
       fig_linechart.add_trace(go.Scatter(x=linechart_df.index,y=linechart_df[col],mode='lines',name=col))
fig_linechart.update_layout(
       title = 'Αριθμός ΑΠΕ/έτος',
       xaxis_title = 'Έτος',
       yaxis_title='Σύνολο ΑΠΕ'
)
st.plotly_chart(fig_linechart)


################################ Graph 2 Create the total number of permits ###########################################

st.header('ΣΥΝΟΛΙΚΟΣ ΑΡΙΘΜΟΣ ΑΔΕΙΩΝ ΑΝΑ ΑΠΕ ΚΑΙ ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ')

@st.cache_data
def calculate_permit_type(df):
    permit_type = df.groupby('ΤΕΧΝΟΛΟΓΙΑ').agg({'ΙΣΧΥΣ (MW)': ['count', 'sum']}).reset_index()
    permit_type.columns = ['ΤΕΧΝΟΛΟΓΙΑ', 'ΣΥΝΟΛΙΚΟΣ ΑΡΙΘΜΟΣ ΑΠΕ', 'ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)']
    permit_type['ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)'] = permit_type['ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)'].round(2)
    return permit_type

permit_type = calculate_permit_type(df)

with st.container():
    left_part, right_part = st.columns(2)
    with left_part:
        st.table(permit_type)
    with right_part:
        selecting_category = st.selectbox('Select column to visualize', permit_type.columns[1:], key='selecting_category')
        fig_some = px.bar(permit_type, x='ΤΕΧΝΟΛΟΓΙΑ', y=selecting_category, title='Αριθμός αδειών')
        st.plotly_chart(fig_some)
#--------------------------------------------  Total produces MW per APE AND PER REGION --------------------------------------------------------------#

st.header('ΣΥΝΟΛΙΚΑ MW ΑΝΑ ΑΠΕ ΚΑΙ ΠΕΡΙΦΕΡΕΙΑ')

def get_power_region_df(df, region, _technologies):
    if region == 'All Regions':
        power_region_df_1 = df
    else:
        power_region_df_1 = df[df['ΠΕΡΙΦΕΡΕΙΑ'] == region]

    grouped_df_power_region = power_region_df_1.groupby('ΤΕΧΝΟΛΟΓΙΑ').agg({'ΙΣΧΥΣ (MW)': 'sum'}).reset_index()

    if len(_technologies)>0:
        grouped_df_power_region = grouped_df_power_region[grouped_df_power_region['ΤΕΧΝΟΛΟΓΙΑ'].isin(_technologies)]
    grouped_df_power_region['ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)'] = grouped_df_power_region['ΙΣΧΥΣ (MW)'].round(2)
    return grouped_df_power_region

select_region1 = st.selectbox('Επιλέξτε περιφέρεια', all_regions, key='select_region1')
select_technology1 = st.multiselect('Επιλέξτε τεχνολογία', df['ΤΕΧΝΟΛΟΓΙΑ'].unique(), ['ΦΩΤΟΒΟΛΤΑΪΚΑ', 'ΑΙΟΛΙΚΑ'])

if len(select_technology1) < 1:
    select_technology1 = all_options

grouped_df_power_region = get_power_region_df(df, select_region1, select_technology1)

with st.container():
    left_part_power_region, right_part_power_region = st.columns(2)
    with left_part_power_region:
        fig_region_power = px.bar(grouped_df_power_region, x='ΤΕΧΝΟΛΟΓΙΑ', y='ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)', color='ΤΕΧΝΟΛΟΓΙΑ',
                                  title=f'ΙΣΧΥΣ  ΑΝΑ ΑΠΕ \n ΣΤΗΝ ΠΕΡΙΦΕΡΕΙΑ {select_region1}')
        st.plotly_chart(fig_region_power)
    with right_part_power_region:
        st.table(grouped_df_power_region)


# ------------------------------------------- Folium map
st.header('ΧΑΡΤΗΣ ΜΕ ΑΡΙΘΜΟ ΑΔΕΙΩΝ ΑΝΑ ΠΕΡΙΦΕΡΕΙΑ')

@st.cache_data
def get_map_data(df, technology):
    mapping_region = {
        'ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ': 'ΛΑΜΙΑ',
        'ΝΟΤΙΟΥ ΑΙΓΑΙΟΥ': 'ΕΡΜΟΥΠΟΛΗ',
        'ΚΡΗΤΗΣ': 'ΗΡΑΚΛΕΙΟ',
        'ΒΟΡΕΙΟΥ ΑΙΓΑΙΟΥ': 'ΜΥΤΙΛΗΝΗ',
        'ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ': 'ΘΕΣΣΑΛΟΝΙΚΗ',
        'ΘΕΣΣΑΛΙΑΣ': 'ΛΑΡΙΣΑ',
        'ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ': 'ΚΟΖΑΝΗ',
        'ΗΠΕΙΡΟΥ ': 'ΙΩΑΝΝΙΝΑ',
        'ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ': 'ΚΟΜΟΤΗΝΗ',
        'ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ': 'ΠΑΤΡΑ',
        'ΠΕΛΟΠΟΝΝΗΣΟΥ': 'ΤΡΙΠΟΛΗ',
        'ΑΤΤΙΚΗΣ': 'ΑΘΗΝΑ',
        'ΙΟΝΙΩΝ ΝΗΣΙΩΝ': 'ΚΕΡΚΥΡΑ'}
    city_cor = {
        'ΛΑΜΙΑ': (38.895973, 22.4349),
        'ΕΡΜΟΥΠΟΛΗ': (37.45, 24.9),
        'ΗΡΑΚΛΕΙΟ': (35.3387, 25.1442),
        'ΜΥΤΙΛΗΝΗ': (39.053322, 26.604367),
        'ΘΕΣΣΑΛΟΝΙΚΗ': (40.640063, 22.944419),
        'ΛΑΡΙΣΑ': (39.639022, 22.419125),
        'ΚΟΖΑΝΗ': (40.300581, 21.789813),
        'ΙΩΑΝΝΙΝΑ': (39.665029, 20.853747),
        'ΚΟΜΟΤΗΝΗ': (41.122439, 25.406558),
        'ΠΑΤΡΑ': (38.24664, 21.734574),
        'ΤΡΙΠΟΛΗ': (37.510136, 22.372644),
        'ΑΘΗΝΑ': (37.983917, 23.72936),
        'ΚΕΡΚΥΡΑ': (39.625, 19.9223)
    }
    map_df_1 = df[df['ΤΕΧΝΟΛΟΓΙΑ'] == technology]
    map_df_1['ΠΟΛΗ'] = map_df_1['ΠΕΡΙΦΕΡΕΙΑ'].map(mapping_region)
    map_df_1['coordinates'] = map_df_1['ΠΟΛΗ'].map(city_cor)
    map_df_1 = map_df_1.groupby('ΠΕΡΙΦΕΡΕΙΑ').agg({'ΙΣΧΥΣ (MW)': 'count', 'coordinates': 'first'}).reset_index()
    map_df_1.columns = ['ΠΕΡΙΦΕΡΕΙΑ', 'ΙΣΧΥΣ (MW)', 'coordinates']
    return map_df_1

select_technology = st.selectbox('Επιλέξτε τεχνολογία', df['ΤΕΧΝΟΛΟΓΙΑ'].unique())
map_df_1 = get_map_data(df, select_technology)

# Initialize the map with specific size settings
my_map = fo.Map(location=(36.402550, 25.472894), zoom_start=6, width='100%', height='100%')

# Ensure the marker cluster is created within the dynamic part of the code
marker_cluster = MarkerCluster().add_to(my_map)

for ind, row in map_df_1.iterrows():
    if pd.notna(row['coordinates']):
        # Custom popup content with better readability
        popup_content = f'<strong>ΠΕΡΙΦΕΡΕΙΑ:</strong> {row["ΠΕΡΙΦΕΡΕΙΑ"]}<br><strong>Αριθμός αδειών:</strong> {row["ΙΣΧΥΣ (MW)"]}'
        popup = fo.Popup(popup_content, max_width=250)

        # Custom marker with a different icon
        marker = fo.Marker(
            location=row['coordinates'],
            popup=popup,
            icon=fo.Icon(color='blue', icon='info-sign')
        )
        marker.add_to(marker_cluster)

# Display the map in Streamlit with adjusted width and height
st_folium(my_map, width=FIG_WIDTH, height=FIG_HEIGHT)
