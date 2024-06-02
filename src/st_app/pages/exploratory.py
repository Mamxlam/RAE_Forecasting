import pandas as pd
import streamlit as st
from collections import Counter
import math

# streamlit run C:\Users\Nikolas\PycharmProjects\Master_Projects\web_mining_project_2_final\RAE_Forecasting\src\st_app\bouzi_main_streamlit.py
st.title('Exparatory Data Analysis (EDA) page')

# Step 1 -->
st.header('STEP 1: Files info for the inital dataset')


step_1_df = pd.read_csv('./RAE_FORECASTING/data/exploratory_page/exploratory_step_1.csv')
step_1_df.drop(columns=['Unnamed: 0'],inplace= True)
st.table(step_1_df)

# Step 2 --> present the unique values of the column
st.header('STEP 2: Dataset columns')
step_2_df = pd.read_csv('./RAE_FORECASTING/data/exploratory_page/exploratory_step_2.csv')
step_2_df.drop(columns=['Unnamed: 0'],inplace= True)
# step_2_df.drop
st.info('Columns ΑΙΤΗΣΗ,ΤΕΧΝΟΛΟΓΙΑ,ΠΕΡΙΦΕΡΕΙΑ,ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤA,ΔΗΜΟΣ,ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ,ΘΕΣΗ are common.')
st.info('Columns ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ,ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ,ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ	  are common.')
st.table(step_2_df.head())
st.info('RENAME column from ΙΣΧΥΣ (MW) to ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)')
st.info('RENAME column from ΑΡ. ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ ΡΑΕ to AΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ')
st.warning('Column ΑΡ. ΒΕΒΑΙΩΣΗΣ ΡΑΕ should be dropped')

# st.write('') # Να γράψω ότι η  'ΙΣΧΥΣ (MW)' renmame σε 'ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)'
# st.warning
# ΕΠΕΙΔΗ ΕΧΟΥΜΕ ΚΕΝΕΣ ΤΙΜΕΣ ΣΤΟΝ ΑΡΙΘΜΟ ΒΕΒΑΙΩΣΗΣ ΡΑΕ ΘΑ ΠΡΕΠΕΙ ΝΑ ΤΟ ΠΕΤΑΞΟΥΜΕ



# Step 3 --> present the initial dataframe
st.header('STEP 3: Rae initial dataset')
step_3_df = pd.read_csv('./RAE_FORECASTING/data/exploratory_page/exploratory_step_3.csv')
step_3_df.drop(columns=['Unnamed: 0'],inplace= True)
st.write(step_3_df)
st.write(f'{step_3_df.shape}')

# Step 4 --> present the dataframe after removing duplicates
st.header('STEP 4: Rae permits after dropping duplicates')
step_4_df = step_3_df.copy()
step_4_df.drop_duplicates(keep='first',inplace=True)
st.table(step_4_df.head())
st.write(step_4_df.shape)
st.info('How a procedure is conducted? Duplicated should remove or one customer can aplly many requests?')
st.warning('Expertise advice required')


# Step 5 --> investigeate the αίτηση column δείξε ένα table για μία τυχαία αίτηση κάνε το με αίτηση για όλες τις αιτήσεις
st.header('STEP 5: Investigation of COL ΑΙΤΗΣΗ')
step_5_df = step_4_df.copy()
# print(step_5_df.columns)
vals_permits_count = step_5_df ['ΑΙΤΗΣΗ'].value_counts()
non_unique_permits_number = len(vals_permits_count[vals_permits_count!=1])
unique_permits_number = len(vals_permits_count[vals_permits_count==1])
table_5_dict = {'Total number permits':len(vals_permits_count),'Unique values':unique_permits_number,'Non-unique permits':non_unique_permits_number}
table_step_5 =pd.DataFrame(data=table_5_dict,index=[0])
st.write(table_step_5)
st.warning('Expertise advice required!!')
st.subheader('Top 5 number  non-unique permits')
st.write(vals_permits_count[vals_permits_count!=1].head(5))
st.subheader('Specific for permits Ι-68749')
investigate_perm_df = step_5_df.loc[step_5_df['ΑΙΤΗΣΗ']=='Ι-68749']
st.write(investigate_perm_df)
st.info('Same permit for the different region/companies/licence number/technologies')
st.warning('Expertise advice required!!')
st.error('ΑΙΤΗΣΗ column should be dropped.')

# Step 6 --> investigate coll
step_6_df = step_4_df.copy()
st.header('STEP 6: Investigation of COL ΑΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ')
vals_count_license = step_6_df['AΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ'].value_counts()
non_unique_licence_number = len(vals_count_license[vals_count_license!=1])
unique_licence_number = len(vals_count_license[vals_count_license==1])
table_6_dict = {'Total number permits':len(vals_count_license),'Unique values':unique_licence_number,'Non-unique permits':non_unique_licence_number}
table_step_6 =pd.DataFrame(data=table_6_dict,index=[0])
st.write(table_step_6)
st.warning('Expertise advice required!!')
st.subheader('Top 5 number  non-unique licences')
st.write(vals_count_license[vals_count_license!=1].head(5))

st.subheader('Specific for licence ΑΔ-02383')
investigate_linc_df = step_6_df.loc[step_6_df['AΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ']=='ΑΔ-02383']
st.write(investigate_linc_df)
st.info('Same licence for the different companies/power/permits')
st.warning('ΑΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ column should be dropped?')
# st.info('One licence for many parks')


# STEP 7 --> ΠΕΡΙΦΕΡΕΙΑ
st.header('STEP 7: Investigation of COL ΠΕΡΙΦΕΡΕΙΑ')
step_7_df = step_4_df.copy()
vals_count_region= step_7_df['ΠΕΡΙΦΕΡΕΙΑ'].unique()

table_7_dict = {'Total unique regions':vals_count_region}
table_step_7 =pd.DataFrame(data=table_7_dict)
st.table(table_step_7)
st.info('Manual correction or with regular expressions because 13 regions of Greece')
weird_region = ['ΠΕΛΟΠΟΝΝΗΣΟΥ ΚΑΙ ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ',
 'ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ',
 'ΘΕΣΣΑΛΙΑΣ ΚΑΙ ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ','ΑΤΤΙΚΗΣ ΚΑΙ ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ',
 'ΘΕΣΣΑΛΙΑΣ ΚΑΙ ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ','ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ ΚΑΙ ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ',
 'ΑΤΤΙΚΗΣ ΚΑΙ ΠΕΛΟΠΟΝΝΗΣΟΥ','ΘΕΣΣΑΛΙΑΣ ΚΑΙ ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ',
 'ΠΕΛΟΠΟΝΝΗΣΟΥ ΚΑΙ ΔΥΤΙΚΗΣ ΕΛΛΑΔOΣ', 'ΘΕΣΣΑΛΙΑΣ ΚΑΙ ΗΠΕΙΡΟΥ',
 'ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ']
weird_region_dict = {'Region':weird_region}
weird_region_df = pd.DataFrame(data=weird_region_dict)
st.table(weird_region_df)
st.info('Aforementioned regions are exteme values')

# STEP 8 -> ALL timestamps some investigation between the εκδοση/υποβολη και λήξη

st.header('STEP 8: INVESTIGATION OF COL ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ AND ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ')
step_8_df = step_4_df.copy()
# print(step_8_df.columns)
#TODO Θα μπορούσαμε να ψάξουμε για τιμές όπου ξεφεύγουν οι τιμες των υποβολών και των εκδόσεων/ κάτω απο το 1985 έχουμε ότι θα πρέπει να διερεθνηθούν
#TODO --> να οριστούν με αυτόν τον τρόπο outliers
step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ']=pd.to_datetime(step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ'],format='%Y-%m-%d %H:%M:%S',errors='coerce')
step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ']=pd.to_datetime(step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'],format='%Y-%m-%d %H:%M:%S',errors='coerce')
step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ']=pd.to_datetime(step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ'],format='%Y-%m-%d %H:%M:%S',errors='coerce')

step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗ-ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'] = step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'] - step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ']
step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗ-ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'] = step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗ-ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'].dt.total_seconds().astype(float)

issuance_app_list = step_8_df['ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗ-ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'].values
issuance_app_list = issuance_app_list/(3600*24*365) #Convert to years
issuance_app_list = issuance_app_list.round()
count_issuance_app = Counter(issuance_app_list) # Count the occurences of each timestamp difference
nan_count_issue_submit = sum(1 for tup in count_issuance_app.most_common() if math.isnan(tup[0]) and tup[1] == 1)
nan_timestamp_issue_submit = {'Nan values between issuance/submit timestamps':nan_count_issue_submit}
nan_timestamp_issue_submit_df = pd.DataFrame(data=nan_timestamp_issue_submit,index=[0])
st.table(nan_timestamp_issue_submit_df)
nan_count_issue_submit_1 =[tup  for tup in count_issuance_app.most_common() if not math.isnan(tup[0])]
st.subheader('Common values between issuance and submit timestamps')
not_nan_difference_years = [tupa[0] for tupa in nan_count_issue_submit_1]
not_nan_ccurences = [extra_tupa[1] for extra_tupa in nan_count_issue_submit_1]
not_nan_timestamp_issue_submit = {'Difference years':not_nan_difference_years,'Occurences':not_nan_ccurences}
not_nan_timestamp_issue_submit_df = pd.DataFrame(data=not_nan_timestamp_issue_submit)
st.write(not_nan_timestamp_issue_submit_df)
st.info('There is no standard format of between submit and issuance timestamps. Negative value included. A standard pattern must be provided to form the timeseries.')
st.error('Some permits were issued before being submitted?')

#Step 9
st.header('STEP 9: INVESTIGATION OF COL ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ AND ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ')
step_9_df = step_8_df.copy()
step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ.-ΛΗΞΗ ΑΔ.ΠΑΡΑΓΩΓΗΣ'] = step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ'] - step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ']
step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ.-ΛΗΞΗ ΑΔ.ΠΑΡΑΓΩΓΗΣ'] = step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ.-ΛΗΞΗ ΑΔ.ΠΑΡΑΓΩΓΗΣ'].dt.total_seconds().astype(float)
step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ.-ΛΗΞΗ ΑΔ.ΠΑΡΑΓΩΓΗΣ']=step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ.-ΛΗΞΗ ΑΔ.ΠΑΡΑΓΩΓΗΣ'].round()/(3600*24*365)
terminate_issuance= step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ.-ΛΗΞΗ ΑΔ.ΠΑΡΑΓΩΓΗΣ'].values
terminate_issuance = terminate_issuance.round()
count_terminate_issuance = Counter(terminate_issuance)
nan_count_terminated = sum(1 for tup in count_terminate_issuance.most_common() if math.isnan(tup[0]) and tup[1] == 1)
nan_count_terminated_dict = {'Nan values betteen issue and terminate': nan_count_terminated }
nan_count_terminated_df = pd.DataFrame(data=nan_count_terminated_dict,index=[0])
st.table(nan_count_terminated_df)

not_nan_count_terminated = [tup for tup in count_terminate_issuance.most_common() if not math.isnan(tup[0])]
st.subheader('Common values between issuance and terminate timestamp')
not_nan_difference_years_term = [tupak[0] for tupak in not_nan_count_terminated]
not_nan_ccurences_term = [tupak_sa[1] for tupak_sa in not_nan_count_terminated]
not_nan_timestamp_submit_terminate_dict = {'Difference years':not_nan_difference_years_term,'Occurences':not_nan_ccurences_term}
not_nan_timestamp_submit_terminate_df = pd.DataFrame(data=not_nan_timestamp_submit_terminate_dict)
st.table(not_nan_timestamp_submit_terminate_df)
st.info('It is assumed that the average difference between issuance and termination is 25 years')

st.subheader('Nan values between issue and terminate timestamps')
length_nan_values_terminate_timestamp = len(step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ'][step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ'].isna()])
length_nan_values_issue_timestamp = len(step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'][step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'].isna()])
length_nan_values_terminate_timestamp_both = len(step_9_df[(step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ'].isna())&(step_9_df['ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ'].isna())])
nan_vals_both_dict= {'Both':length_nan_values_terminate_timestamp_both ,'Issuance':length_nan_values_issue_timestamp ,'Terminate':length_nan_values_terminate_timestamp}
nan_cols_issue_term_df = pd.DataFrame(data=nan_vals_both_dict,index=[0])
st.table(nan_cols_issue_term_df)
st.warning('If both columns are zero we cannot define it')

