#-------------- Imports ----------------------#
import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
st.title('Observatory page 🔍')
from streamlit_folium import st_folium
import folium as fo

## observatory pages was
##
##
##
##
##
##
##
##
##
##


# streamlit run C:\Users\Nikolas\PycharmProjects\Master_Projects\web_mining_project_2_final\RAE_Forecasting\src\st_app\bouzi_main_streamlit.py

# ./RAE_Forecasting/src/st_app/pages/observatory_page.csv
df = pd.read_csv('./RAE_FORECASTING/data/observatory_page.csv')
# df = pd.read_csv('./observatory_page.csv')

list_drop_cols = ['Unnamed: 0','RSI','ΑΙΤΗΣΗ','ΑΡ. ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ ΡΑΕ','ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ', 'ΔΗΜΟΣ ', 'ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ',
'ΘΕΣΗ','RSI_ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ', 'RSI_ΔΗΜΟΣ ', 'RSI_ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ','RSI_ΘΕΣΗ', 'ΔΙΑΡΚΕΙΑ','ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ','ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ','ΕΤΑΙΡΕΙΑ']
df.drop(columns=list_drop_cols,inplace=True)
df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'] = pd.to_datetime(df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'],format='%Y-%m-%d %H:%M:%S', errors='coerce')
# print(df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'][0],type(df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'][0]))

#----------------------------------------------- 1 PERMITS THE YEARS -------------------------------------------------------------------------#
st.header('Χρονοδιάγραμμα αδειών ΑΠΕ')
time_permits = df.copy()
time_permits = time_permits.set_index('ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ')
time_permits = time_permits.sort_index()
time_permits.index = time_permits.index.to_series().apply(lambda x: x + pd.DateOffset(years=100) if x in time_permits.index[:4] else x)
time_permits = time_permits.sort_index()

# print(time_permits['ΤΕΧΝΟΛΟΓΙΑ'].unique())
grouped_df = time_permits.groupby([pd.Grouper(freq='M'), 'ΤΕΧΝΟΛΟΓΙΑ']).size().unstack(fill_value=0)
# print(grouped_df.head())
# print(type(grouped_df),grouped_df.columns)
# print(time_permits.columns)

options_line_chart = st.multiselect("Επιλογή ΑΠΕ",['ΑΙΟΛΙΚΑ', 'ΒΙΟΑΕΡΙΟ', 'ΒΙΟΜΑΖΑ', 'ΒΙΟΜΑΖΑ-ΒΙΟΑΕΡΙΟ', 'ΒΙΟΜΑΖΑ-ΚΑΥΣΗ',
       'ΓΕΩΘΕΡΜΙΑ', 'ΗΛΙΟΘΕΡΜΙΚΑ', 'ΜΥΗΕ', 'Σ.Η.Θ.Υ.Α.', 'ΦΩΤΟΒΟΛΤΑΪΚΑ'],['ΦΩΤΟΒΟΛΤΑΪΚΑ'])

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

permit_type = df.copy()
st.header('ΣΥΝΟΛΙΚΟΣ ΑΡΙΘΜΟΣ ΑΔΕΙΩΝ ΑΝΑ ΑΠΕ ΚΑΙ ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ')
with st.container():
       permit_type = permit_type.groupby('ΤΕΧΝΟΛΟΓΙΑ').agg({'ΙΣΧΥΣ (MW)': ['count', 'sum']}).reset_index()
       permit_type.columns = ['ΤΕΧΝΟΛΟΓΙΑ', 'ΣΥΝΟΛΙΚΟΣ ΑΡΙΘΜΟΣ ΑΠΕ', 'ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)']
       permit_type['ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)'] = permit_type['ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)'].round(2)
       left_part,right_part = st.columns(2)
       with left_part:
              st.table(permit_type)
       with right_part:
              selecting_category = st.selectbox('Select column to visualize', permit_type.columns[1:],key='selecting_category')

              fig_some = px.bar(permit_type,x='ΤΕΧΝΟΛΟΓΙΑ',y=selecting_category,title='Αριθμός αδειών')
              st.plotly_chart(fig_some)



################ Graph to organize data per region and afterward per region and count ###################################

permit_region_type = df.copy()
st.header('ΠΛΗΘΟΣ ΑΔΕΙΩΝ ΑΝΑ ΠΕΡΙΦΕΡΕΙΑ')
with st.container():
       select_region = st.selectbox('Επιλέξτε περιφέρεια', permit_region_type['ΠΕΡΙΦΕΡΕΙΑ'].unique())
       permit_region_type = permit_region_type.loc[permit_region_type['ΠΕΡΙΦΕΡΕΙΑ'] == select_region]
       permit_region_type.reset_index(inplace=True)
       permit_region_type_v1 = permit_region_type.groupby('ΤΕΧΝΟΛΟΓΙΑ').agg({'ΤΕΧΝΟΛΟΓΙΑ': ['count']}).reset_index()
       permit_region_type_v1.columns = ['ΤΕΧΝΟΛΟΓΙΑ', 'ΣΥΝΟΛΙΚΟΣ ΑΡΙΘΜΟΣ ΑΠΕ']
       left_part_region_type,right_part_region_type = st.columns(2)
       with left_part_region_type:
                     st.table(permit_region_type_v1)
       with right_part_region_type:
           fig_region_type = px.bar(permit_region_type_v1,x='ΤΕΧΝΟΛΟΓΙΑ',y='ΣΥΝΟΛΙΚΟΣ ΑΡΙΘΜΟΣ ΑΠΕ',title='Αριθμός αδειών ανά ΠΕΡΙΦΈΡΕΙΑ')
           st.plotly_chart(fig_region_type)
# --------------------------------------     TOTAL NUMBER OF PERMITS FOR ALL REGIONS -----------------------------------------------------------------#
st.header('ΠΛΗΘΟΣ ΑΔΕΙΩΝ ΓΙΑ ΟΛΕΣ ΤΙΣ ΠΕΡΙΦΕΡΕΙΕΣ')
permit_region_type_total = df.copy()
permit_region_type_total_v1 = permit_region_type_total.groupby('ΠΕΡΙΦΕΡΕΙΑ').agg({'ΤΕΧΝΟΛΟΓΙΑ':['count']}).reset_index()
permit_region_type_total_v1.columns = ['ΠΕΡΙΦΕΡΕΙΑ','ΠΛΗΘΟΣ ΑΔΕΙΩΝ']
st.table(permit_region_type_total_v1)


#--------------------------------------------  Total produces MW per APE AND PER REGION --------------------------------------------------------------#

power_region_df = df.copy()
st.header('ΣΥΝΟΛΙΚΑ MW ΑΝΑ ΑΠΕ ΚΑΙ ΠΕΡΙΦΕΡΕΙΑ')
with st.container():

    # print(power_region_df['ΠΕΡΙΦΕΡΕΙΑ'].unique())

    select_region1 = st.selectbox('Επιλέξτε περιφέρεια', power_region_df['ΠΕΡΙΦΕΡΕΙΑ'].unique(), key='select_region1')

    select_technology1 = st.multiselect('Επιλέξτε τεχνολογία',power_region_df['ΤΕΧΝΟΛΟΓΙΑ'].unique(),['ΦΩΤΟΒΟΛΤΑΪΚΑ'])
    power_region_df_1 = power_region_df.loc[power_region_df['ΠΕΡΙΦΕΡΕΙΑ']==select_region1]
    grouped_df_power_region = power_region_df_1.groupby('ΤΕΧΝΟΛΟΓΙΑ').agg({'ΙΣΧΥΣ (MW)':['sum']}).reset_index()
    grouped_df_power_region.columns = ['ΤΕΧΝΟΛΟΓΙΑ','ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)']
    grouped_df_power_region['ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)']=grouped_df_power_region['ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)'].round(2)
    grouped_df_power_region =grouped_df_power_region.loc[grouped_df_power_region['ΤΕΧΝΟΛΟΓΙΑ'].isin(select_technology1)]

    grouped_df_power_region['ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)']=grouped_df_power_region['ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)'].round(2)
    left_part_power_region,right_part_power_region = st.columns(2)
    with left_part_power_region:
        fig_region_power = px.bar(grouped_df_power_region, x='ΤΕΧΝΟΛΟΓΙΑ', y='ΣΥΝΟΛΙΚΗ ΙΣΧΥΣ (MW)',color='ΤΕΧΝΟΛΟΓΙΑ',
                                   title=f'ΙΣΧΥΣ  ΑΝΑ ΑΠΕ \n ΣΤΗΝ ΠΕΡΙΦΕΡΕΙΑ {select_region1}')
        st.plotly_chart(fig_region_power)
    with right_part_power_region:
          st.table(grouped_df_power_region)


# ------------------------------------------- Folium map
st.header('ΧΑΡΤΗΣ ΜΕ ΑΡΙΘΜΟ ΑΔΕΙΩΝ ΑΝΑ ΠΕΡΙΦΕΡΕΙΑ')

map_df = df.copy()
select_technology = st.selectbox('Επιλέξτε περιφέρεια', power_region_df['ΤΕΧΝΟΛΟΓΙΑ'].unique())
map_df_1 = map_df.loc[map_df['ΤΕΧΝΟΛΟΓΙΑ']==select_technology]

mapping_region ={
    'ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ':'ΛΑΜΙΑ',
    'ΝΟΤΙΟΥ ΑΙΓΑΙΟΥ':'ΕΡΜΟΥΠΟΛΗ',
    'ΚΡΗΤΗΣ':'ΗΡΑΚΛΕΙΟ',
    'ΒΟΡΕΙΟΥ ΑΙΓΑΙΟΥ':'ΜΥΤΙΛΗΝΗ',
    'ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ':'ΘΕΣΣΑΛΟΝΙΚΗ',
    'ΘΕΣΣΑΛΙΑΣ':'ΛΑΡΙΣΑ',
    'ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ':'ΚΟΖΑΝΗ',
    'ΗΠΕΙΡΟΥ ':'ΙΩΑΝΝΙΝΑ',
    'ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ':'ΚΟΜΟΤΗΝΗ',
    'ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ':'ΠΑΤΡΑ',
    'ΠΕΛΟΠΟΝΝΗΣΟΥ':'ΤΡΙΠΟΛΗ',
    'ΑΤΤΙΚΗΣ':'ΑΘΗΝΑ',
    'ΙΟΝΙΩΝ ΝΗΣΙΩΝ':'ΚΕΡΚΥΡΑ'}

map_df_1['ΠΟΛΗ'] =  map_df_1['ΠΕΡΙΦΕΡΕΙΑ'].map(mapping_region)


# print(map_df_1['ΠΟΛΗ'].unique())
city_cor={
 'ΛΑΜΙΑ':(38.895973,22.4349),
'ΕΡΜΟΥΠΟΛΗ':(37.45,24.9),
'ΗΡΑΚΛΕΙΟ':(35.3387,25.1442),
'ΜΥΤΙΛΗΝΗ':(39.053322,26.604367),
 'ΘΕΣΣΑΛΟΝΙΚΗ':(40.640063,22.944419),
   'ΛΑΡΙΣΑ':(39.639022,22.419125),
    'ΚΟΖΑΝΗ':(40.300581,21.789813),
    'ΙΩΑΝΝΙΝΑ':(39.665029,20.853747),
    'ΚΟΜΟΤΗΝΗ':(41.122439,25.406558),
    'ΠΑΤΡΑ':(38.24664,21.734574),
    'ΤΡΙΠΟΛΗ':(37.510136,22.372644),
    'ΑΘΗΝΑ':(37.983917, 23.72936),
    'ΚΕΡΚΥΡΑ':(39.625,19.9223)
}
map_df_1['cor'] =  map_df_1['ΠΟΛΗ'].map(city_cor)

map_df_1 = map_df_1.groupby('ΠΕΡΙΦΕΡΕΙΑ').agg({'ΙΣΧΥΣ (MW)':'count','cor':'first'}).reset_index()
map_df_1.columns = ['ΠΕΡΙΦΕΡΕΙΑ','ΙΣΧΥΣ (MW)','coordinates']

my_map = fo.Map(location=(36.402550,25.472894),zoom_start=6)
for ind,row in map_df_1.iterrows():
    popup_content = f'ΠΕΡΙΦΕΡΕΙΑ: {row["ΠΕΡΙΦΕΡΕΙΑ"]} \n Αριθμός αδειών: {row["ΙΣΧΥΣ (MW)"]}'
    fo.Marker(row['coordinates'],popup=popup_content).add_to(my_map)


st_folium(my_map,width=900)
