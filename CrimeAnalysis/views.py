import os
import re
import json
import base64
import numpy as np
import pandas as pd
import folium
from folium import plugins
import geopandas as gpd
import networkx as nx
import plotly.express as px
# from langchain import OpenAI
from langchain_community.llms import OpenAI
from django.views import View
from dotenv import load_dotenv
# from langchain.chat_models import ChatOpenAI
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from CrimeMapping.views import crime
from CrimeMapping.models import FirData
from plotly.subplots import make_subplots
from django.shortcuts import render, redirect
from langchain_experimental.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent
from django.core.paginator import Paginator
from django.http import JsonResponse
from CrimeAnalysis.models import Fir_Karnataka

load_dotenv()

# Not to run below command
# git rm --cached db.sqlite


rjdf = pd.DataFrame(FirData.objects.all().values())
# ukdf = pd.read_csv("CrimeMapping/data/UK-Dataset-Final.csv", on_bad_lines='skip' )
# dfr= pd.read_csv("CrimeMapping/data/Rowdy_Preprocessed.csv")
# dfc=pd.read_csv("CrimeMapping/data/Complaints_Preprocessed.csv")
# dfm= pd.read_csv("CrimeMapping/data/MOBs_Preprocessed.csv")
# dfv=pd.read_csv("CrimeMapping/data/Victims_Preprocessed.csv")
print("_________________________________________________________________________")
# print(dfk.info())
# dfm = dfm[dfm['AGE'].le(90)]
# dfm['AGE'] = dfm['AGE'].abs()
# dfv['age'] = dfv['age'].abs()

tempTable = []
ChartTemp:any = []


class CrimeAnalysis(View):
    
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'CrimeAnalysis/crimeanalysis.html')
        return redirect('/login')

    def agent_llm(self, rjdf):
        llm = ChatOpenAI(
        model_name='gpt-3.5-turbo-16k',
        openai_api_key=os.getenv('OPENAI_API_KEY') )
        return create_pandas_dataframe_agent(llm, rjdf, verbose=False, handle_parsing_errors=True)

    def query_llm(self, agent, query):
        prompt = (
            """
                For the following query, if it requires drawing a table, reply as follows:
                {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

                If the query requires creating a bar chart, reply as follows:
                {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

                If the query requires creating a line chart, reply as follows:
                {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

                The various types of chart, "bar", "line" and "pie" plot

                If it is just asking a question that requires neither, reply as follows:
                {"answer": "answer"}
                Example:
                {"answer": "The title with the highest rating is 'Gilead'"}

                If you do not know the answer, reply as follows:
                {"answer": "I do not know."}

                Return all output as a string.

                All strings in "columns" list and data list, should be in double quotes,

                For example: {"columns": ["title", "ratings_count"], "data": [["Gilead", 361], ["Spider's Web", 5164]]}

                Lets think step by step.

                Below is the query.
                Query: 
                """
            + query
        )

        response = agent.run(prompt)
        return response.__str__()

    def decode_response(self, response: str) -> dict:
        if response.startswith('{"'):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
        
                return {}
        else:
    
            return {"answer": response}
 
    def post(self, request):
        if request.method == 'POST':
            query = request.POST['query']
            agent = self.agent_llm(rjdf)
            response = self.query_llm(agent=agent, query=query)
            decoded_response = self.decode_response(response)

            context={
                'result1': decoded_response,
            }
            return render(request, 'CrimeAnalysis/crimeanalysis.html', context)


class CrimeAnalysisTable(View):

    def get(self, request):
        if request.user.is_authenticated:
            # if tempTable is None or len(tempTable) == 0:
                rjdf = Fir_Karnataka.objects.all().values()
                # Paginate the data
                count = rjdf.count()
                paginator = Paginator(rjdf, 10000)  # Show 1000 records per page
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                data_dict = list(page_obj)
                JSONdata = json.dumps(data_dict, ensure_ascii=False)
                tempTable.append(JSONdata)
                # Pass the JSON data and pagination information to the template
                return render(request, 'CrimeAnalysis/table.html', {'JSONdata': JSONdata, 'page_obj': page_obj, 'count': count})
            # else:
                # return render(request, 'CrimeAnalysis/table.html', {'JSONdata': tempTable[0]})
        return redirect('/login')
    
    # Add this method to handle AJAX requests from DataTables
    def post(self, request):
        if request.user.is_authenticated:
            rjdf = Fir_Karnataka.objects.all().values()
            count = rjdf.count()
            paginator = Paginator(rjdf, 10000)
            page_number = request.POST.get('page')
            page_obj = paginator.get_page(page_number)
            data_dict = list(page_obj)
            JSONdata = json.dumps(data_dict, ensure_ascii=False)
            return JsonResponse({'data': data_dict, 'draw': request.POST.get('draw'), 'recordsTotal': paginator.count, 'recordsFiltered': paginator.count, 'JSONdata': JSONdata, 'count': count})
        return redirect('/login')
        

class CrimeAnalysisChart(View):

    
    def get(self, request):
        if request.user.is_authenticated:
            if ChartTemp is None or len(ChartTemp) == 0:
                # dfk = pd.read_csv("CrimeMapping/data/FIR_Details.csv", on_bad_lines='skip')
                dfk = pd.DataFrame(Fir_Karnataka.objects.all().values()[0:100000])
                
                # rjdf_2 = pd.DataFrame(Fir_Karnataka.objects.all().values()[20000:40000])
                # print("================")
                # rjdf_3 = pd.DataFrame(Fir_Karnataka.objects.all().values()[40000:60000])
                # print("================")
                # rjdf_4 = pd.DataFrame(Fir_Karnataka.objects.all().values()[80000:100000])
                # print("================")
                # rjdf_5 = pd.DataFrame(Fir_Karnataka.objects.all().values()[100000:120000])
                # print("================")
                # rjdf=pd.concat([rjdf_1, rjdf_2, rjdf_3, rjdf_4, rjdf_5], ignore_index=True)

                # tempDF = ukdf.copy()
                # tempDF['Arrest'] = tempDF['Arrest'].map({True: 'True', False: 'False'})
                # tempDF['Domestic'] = tempDF['Domestic'].map({True: 'True', False: 'False'})
                # tempDF['Date']=tempDF['Date'].astype(str)
                # Samp=tempDF[tempDF["Community_area"]==""]

                # Q1 Which Type of Crime is most recorded ?
                # crime['Type'] = tempDF["Type"].unique()
                # crime['Where'] = tempDF["Where"].unique()
                # crime['District'] = tempDF["District"].unique()
                # q1=tempDF.Type.value_counts().rename_axis('Crime_Type').reset_index(name='counts')
                # df_type=list(q1["Crime_Type"].head(13))
                # type_count=list(q1["counts"].head(13))
        
                # Q1 Most Frequent Time of FIR Reported to the Station
                tempDF1= rjdf.copy()
                tempDF1['time'] = pd.to_datetime(tempDF1['time'], errors='coerce')
                tempDF1['hour'] = tempDF1['time'].dt.hour
                fir_counts = tempDF1['hour'].value_counts().sort_index()
                # Assuming 'fir_counts is your DataFrame
                df_type = fir_counts.index.tolist()
                type_count = fir_counts.values.flatten().tolist() 
                

                #Object of Array (Dictionary) for Different Questions representation in analytics
                #Use Js Ternary Operator
                # Q2 Where most no. of crimes are recorded?
                # Top 5 place where 
                # q2=tempDF.Where.value_counts().rename_axis('Where_Type').reset_index(name='counts')
                # df_type2=list(q2["Where_Type"].head(5))
                # type_count2=list(q2["counts"].head(5))


                # Q2 Which Day most no. of FIR's are reported
                tempDF1['date'] = tempDF1['date'].replace('.', '-')
                tempDF1['date'] = pd.to_datetime(tempDF1['date'], errors='coerce')
                tempDF1.sort_values(by='date', inplace=True)
                
                fir_counts2 = tempDF1['date'].dt.date.value_counts().sort_index()
                # Assuming 'df' is your DataFrame and 'date' is your column
                

                dates = fir_counts2.index.tolist()
                type_count2 = fir_counts2.values.flatten().tolist() 
                df_type2 = [date.strftime('%Y-%m-%d') for date in dates]


                # Q3 Which IPC Section is most recorded in FIR
                counts_ipc = tempDF1['ipc_no'].value_counts()
                df_type3 = counts_ipc.index.tolist()
                type_count3 = counts_ipc.values.flatten().tolist()


                #Q4 Age Distribution of the victim reported in the FIR Records
                tempDF2= rjdf.copy()
                tempDF2['age'] = tempDF2['age'].apply(lambda x: ''.join(re.findall('\d+', str(x))))
                tempDF2['age'] = pd.to_numeric(tempDF2['age'])
                tempDF2['age']=tempDF2['age'].dropna()
                counts = tempDF2['age'].value_counts()
                print(counts)
                df_type4 = counts.index.tolist()
                type_count4 = counts.values.tolist()


                # #Which Type of Crime is more and arrest is done?
                # df_arrest=tempDF[tempDF["Arrest"]=="True"]
                # q3=df_arrest.Type.value_counts().rename_axis('Crime_Type1').reset_index(name='counts')
                # df_type3=list(q3["Crime_Type1"].head(5))
                # type_count3=list(q3["counts"].head(5))
                '''
                # Q4 On which day of week; the crime is more?
                df_type4=['Monday','Tuesday','Wednesday',  'Thursday', 'Friday', 'Saturday', 'Sunday']
                type_count4=tempDF.groupby([tempDF.index.dayofweek]).size()
                print("*******", type_count4)
        
                # Q5 In which month, most no. of crime is recorded?

                df_type5=['Jan','Feb','Mar',  'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                type_count5=tempDF.groupby([tempDF.index.month]).size()
                '''
                # On page load graph will be shown
                df_typeAll=list(tempDF2["ipc_no"].unique())
                type_countAll=[]
                for x in range(len(tempDF2.ipc_no.value_counts())):
                    type_countAll.append(int(tempDF2.ipc_no.value_counts()[x]))
                dataX = type_countAll
                dataY = df_typeAll
            
                #tempDF.drop("Arrest", inplace=True, axis=1)
                #tempDF.drop("Domestic", inplace=True, axis=1)
                # dumbdata = tempDF.to_dict('records')
                # print(tempDF.to_dict('records'))
                # JSONdata =json.dumps(rjdf.to_dict('records'))

                print('''
                *****************
                *****************
                *****************
                *****************
                ''', type_count)
                print(df_type)
                print('''
                *****************
                *****************
                *****************
                *****************
                ''', type_count2)
                print(df_type2)
                print('''
                *****************
                *****************
                *****************
                *****************
                ''', type_count3)
                print(df_type3)
                print('''
                *****************
                *****************
                *****************
                *****************
                ''', type_count4)
                print(df_type4)



                # # #RowdySetters Data Analaysis

                # # Age Distribution of the RowdySetters
                # counts, bin_edges = np.histogram(dfr['Age'], bins=20)

                # x_age_rowdy = bin_edges.tolist()
                # y_age_rowdy = counts.tolist()


                fig_age_rowdy = px.histogram(dfr, x="Age", nbins=20, title="Age Distribution of Rowdy Setters",
                                            color="Age")
                fig_age_rowdy.update_layout(
                xaxis_title="Age",
                yaxis_title="Count", 
                bargap=0.1
                )
                plot_div_age_rowdy = fig_age_rowdy.to_html(full_html=False, include_plotlyjs='cdn')

                # fig_age_rowdy.show()



                # RowdySetter Category
                x_rowdy_category = dfr['Rowdy_Category'].unique().tolist()
                y_rowdy_category = dfr['Rowdy_Category'].value_counts().tolist()

                # #Top 10 District Name
                district_counts = dfr['District_Name'].value_counts().nlargest(10).reset_index()
                print(district_counts)
                x_rowdy_district = district_counts['District_Name'].tolist()
                y_rowdy_district = district_counts['count'].tolist()    

                # #Top 10 Unit Name
                unit_counts = dfr['Unit_Name'].value_counts().nlargest(10).reset_index()
                x_rowdy_units = unit_counts['Unit_Name'].tolist()
                y_rowdy_units = unit_counts['count'].tolist()


                # #MOBs Data Analaysis

                # MOBs Age vs Gang Strength more than 0, Scatter Plot

                sorted_dfm = dfm.sort_values(by='AGE', ascending=True)

                # Filter the DataFrame to only include rows where 'Gang_Strength' is greater than 0
                gang_strength_gt_zero = sorted_dfm[sorted_dfm['Gang_Strength'] > 0]

                # Convert the 'AGE' and 'Gang_Strength' columns to lists
                # x_age = gang_strength_gt_zero['AGE'].tolist()
                # y_strength = gang_strength_gt_zero['Gang_Strength'].tolist()
                gang_strength_gt_zero = dfm[dfm['Gang_Strength'] > 0]

                fig_strength_gt_zero= px.scatter(gang_strength_gt_zero, x='AGE', y='Gang_Strength', color='Crime_Group1',
                                title='Age vs Gang Strength (Gang_Strength > 0)',
                                hover_data={'MOB_Number':True, 'MobOpenDate':True})

                plot_div_strength_gt_zero = fig_strength_gt_zero.to_html(full_html=False, include_plotlyjs='cdn')
         


                # Top 6 Caste of MOBs
                caste_counts = dfm['Caste'].value_counts().sort_values(ascending=False).head(6)
                caste_values = caste_counts.values.tolist()
                caste_names = caste_counts.index.tolist()

                # Top 10 Crime Groups
                crime_group_counts = dfm['Crime_Group1'].value_counts().sort_values(ascending=False).head(20)
                x_crime_group = crime_group_counts.index.tolist()
                y_crime_group = crime_group_counts.values.tolist()


                # Age vs Crime Head2
                # age_crime_type = dfm.groupby(['AGE', 'Crime_Head2']).size().reset_index().rename(columns={0: 'Count'})
                # x_crime_head2 = age_crime_type['AGE'].tolist()
                # y_crime_head2 = age_crime_type['Count'].tolist()
                tempdf_age_crime= dfm[dfm['AGE']>=10]
                age_crime_type = tempdf_age_crime.groupby(['AGE', 'Crime_Head2']).size().reset_index().rename(columns={0: 'Count'})
                fig_age_crime_type = px.scatter(age_crime_type, x='AGE', y='Count', color='Crime_Head2', title='Crime Count by Age and Crime Type')
                # fig.show()
                plot_div_age_crime_type = fig_age_crime_type.to_html(full_html=False, include_plotlyjs='cdn')



                
                # Sankey Chart - MOBs Class 1 and Cass 2
                sankey_data = dfm[['Crime_Group1', 'Crime_Head2', 'class']].dropna()
                sankey_data = sankey_data.groupby(['Crime_Group1', 'Crime_Head2', 'class']).size().reset_index(name='Count')
                plot_div21 = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=sankey_data['Crime_Group1'].unique().tolist() + sankey_data['Crime_Head2'].unique().tolist() + sankey_data['class'].unique().tolist(),
                        color="blue"
                    ),
                    link=dict(
                        source=[sankey_data['Crime_Group1'].tolist().index(source) for source in sankey_data['Crime_Group1']],
                        target=[len(sankey_data['Crime_Group1'].unique()) + len(sankey_data['Crime_Head2'].unique()) + sankey_data['class'].tolist().index(target) for target in sankey_data['class']],
                        value=sankey_data['Count'],
                        label=sankey_data['Crime_Head2'].tolist()
                    )
                )])
                plot_div21.update_layout(title_text="Crime Group Flow", font_size=10)

                # image_data1 = fig.to_image(format="png")
                # encoded_string1 = base64.b64encode(image_data1).decode('utf-8')
                # plot_div21.update_layout(autosize=True, height=500)
                plot_div_Sankey_MOB = plot_div21.to_html(full_html=False, include_plotlyjs='cdn')


                #Top 10 Occupation
                occupation_counts = dfm['Occupation'].value_counts().sort_values(ascending=False).head(10)
                x_occupation = occupation_counts.index.tolist()
                y_occupation = occupation_counts.values.tolist()

                #AGE vs Grading
                # x_values = dfm['Grading'].tolist()
                # y_values = dfm['AGE'].tolist()
                x_categories = [0, 1, 2, 3, 99]
                fig_grading_MOB = px.scatter(
                    dfm,
                    x='Grading',
                    y='AGE',
                    title='Correlation between Grading and Age',
                    category_orders={'Grading': x_categories}
                )
                plot_div_grading_MOB = fig_grading_MOB.to_html(full_html=False, include_plotlyjs='cdn')


                #Network Analysis
                # offender_network = dfm[['Person_No', 'Gang_Strength']].dropna()
                # G = nx.from_pandas_edgelist(offender_network, source='Person_No', target='Gang_Strength')
                # pos = nx.spring_layout(G)
                # plt.figure(figsize=(10, 8))
                # nx.draw(G, pos, node_color='lightgreen', with_labels=True)

                # plt.savefig('graph.png')

                # with open('graph.png', 'rb') as image_file:
                #     encoded_string2 = base64.b64encode(image_file.read()).decode('utf-8')

                offender_network = dfm[['Person_No', 'Gang_Strength']].dropna()
                G = nx.from_pandas_edgelist(offender_network, source='Person_No', target='Gang_Strength')
                pos = nx.spring_layout(G)
                for node in G.nodes():
                    G.nodes[node]['pos'] = pos[node]

                edges = []
                for edge in G.edges():
                    x0, y0 = G.nodes[edge[0]]['pos']
                    x1, y1 = G.nodes[edge[1]]['pos']
                    trace = go.Scatter(x=tuple([x0, x1]), y=tuple([y0, y1]),
                                        mode='lines',
                                        line=dict(color='rgb(210,210,210)', width=1),
                                        hoverinfo='none'
                                        )
                    edges.append(trace)

                node_trace = go.Scatter(x=[], y=[], text=[], mode='markers', hoverinfo='text',
                                    marker=dict(color='lightgreen', size=20, line=dict(color='rgb(50,50,50)', width=0.5)))

                for node in G.nodes():
                    x, y = G.nodes[node]['pos']
                    node_trace['x'] += tuple([x])
                    node_trace['y'] += tuple([y])
                    node_trace['text'] += tuple(['<b>' + str(node) + '</b>'])

                layout = go.Layout(title='Offender Network',
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20, l=5, r=5, t=40),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                height=600,
                                width=800
                                )

                fig = go.Figure(layout=layout)

                for edge in edges:
                    fig.add_trace(edge)
                    fig.add_trace(node_trace)

                plot_div_network_MOB = fig.to_html(full_html=False, include_plotlyjs='cdn')
                # fig.show()



                #FIR Details
                print(dfk.info())
                # Month vs Crime Count
                dfk['Month'] = pd.to_datetime(dfk['Month'])
                monthly_crimes = dfk["Month"]
                labels_monthly_crimes = monthly_crimes.index.tolist()
                values_monthly_crimes = monthly_crimes.values.tolist()
                print(labels_monthly_crimes, values_monthly_crimes)
                print("++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++++++++++++++++++++")

                # # Various Crimes at different District
                # grouped_df_district_fir = dfk.groupby(['District_Name', 'CrimeGroup_Name']).size().reset_index(name='Count')
                # labels_district_fir = grouped_df_district_fir[['District_Name', 'CrimeGroup_Name']].values.tolist()
                # values_district_fir = grouped_df_district_fir['Count'].values.tolist()

                grouped_df_district = dfk.groupby(['District_Name', 'CrimeGroup_Name']).size().reset_index(name='Count')
                fig_karnataka_district = px.bar(grouped_df_district, x='District_Name', y='Count', color='CrimeGroup_Name', title='Crime Distribution by District and Crime Group')
                plot_div_karnataka_district= fig_karnataka_district.to_html(full_html=False) 

                # # Victim Counts vs Accused Counts
                # victim_counts = dfk['VICTIM_COUNT'].tolist()
                # accused_counts = dfk['Accused_Count'].tolist()

                # Top 5 Mean of Victim Count wrt CrimeGroup Name - Pie Plot
                grouped_df = dfk.groupby('CrimeGroup_Name')['VICTIM_COUNT'].mean()
                top_5_crime_groups = grouped_df.nlargest(5)
                X_top_5_crime_groups = top_5_crime_groups.index.tolist()
                Y_top_5_crime_groups = top_5_crime_groups.values.tolist()

                # Top 10 Sum of Victim Count wrt CrimeGroup Name - Bar Graph
                grouped_df = dfk.groupby('CrimeGroup_Name')['VICTIM_COUNT'].sum()
                top_10_crime_groups = grouped_df.nlargest(10)
                X_top_10_crime_groups = top_10_crime_groups.index.tolist()
                Y_top_10_crime_groups = top_10_crime_groups.values.tolist()

                # # Distribution of the count of FIR Recorded at which Hour
                # dfk['Hour'] = pd.to_datetime(dfk['FIR_Reg_DateTime']).dt.hour
                # hourly_crimes = dfk.groupby('Hour')['FIR_ID'].count().reset_index()
                # labels_hourly_crimes = hourly_crimes['Hour'].tolist()
                # values_hourly_crimes = hourly_crimes['FIR_ID'].tolist()

                # Time Series Behavior of the Offence Recorded
                dfk['Offence_From_Date'] = pd.to_datetime(dfk['Offence_From_Date'])
                dfk = dfk[dfk['Offence_From_Date'] >= pd.to_datetime('2014-01-01')]
                crime_trend = dfk.groupby([pd.Grouper(key='Offence_From_Date', freq='M')])['FIR_ID'].count().reset_index()
                crime_trend = crime_trend.rename(columns={'Offence_From_Date': 'Date', 'FIR_ID': 'Crime Count'})
                labels_crime_trend = crime_trend['Date'].tolist()
                values_crime_trend = crime_trend['Crime Count'].tolist()
                print(labels_crime_trend, values_crime_trend)

                # Counts of FIR Type
                fir_type = dfk.groupby('FIR_Type')['FIR_ID'].count().reset_index()
                labels_fir_type = fir_type['FIR_Type'].tolist()
                values_fir_type = fir_type['FIR_ID'].tolist()


                #Complaints RecordedDetails

                # Complaints Recorded by Month

                complaints_by_month = dfc.groupby('Month')['FIRNo'].count().reset_index()
                labels_complaints_by_month = complaints_by_month['Month'].tolist()
                values_complaints_by_month = complaints_by_month['FIRNo'].tolist()

                # Age Distribution of the Complaints Recorded

                df_age = dfc['Age']
                labels_age_complaints = df_age.index.tolist()
                values_age_complaints = df_age.tolist()

                # Religion and Caste Relation of the Recorded Complaint - Sun Burst Format

                df_filtered_religion = dfc[dfc['Caste'] != 'N/A']
                labels_filtered_religion = df_filtered_religion['Caste'].tolist() + df_filtered_religion['Religion'].tolist()
                values_filtered_religion = df_filtered_religion['FIRNo'].tolist()

                # Complaints by Year 

                complaints_by_year = dfc.groupby('Year')['FIRNo'].count().reset_index()
                labels_complaints_by_year = complaints_by_year['Year'].tolist()
                values_complaints_by_year = complaints_by_year['FIRNo'].tolist()


                # Complaint Recorded as per the Gender

                sex_counts = dfc['Sex'].value_counts()
                labels_sex_counts  = sex_counts.index.tolist()
                values_sex_counts  = sex_counts.values.tolist()

                # Age Distribution by Occupation of the Complaint Recorded

                occupation_counts = dfc['Occupation'].value_counts()
                labels_occupation_counts = occupation_counts.index.tolist()
                counts_occupation_counts = occupation_counts.values.tolist()

                # Nationality Distribution of the complaint recorded

                nationality_counts = dfc['Nationality'].value_counts()
                labels_nationality_counts = nationality_counts.index.tolist()
                counts_nationality_counts = nationality_counts.values.tolist()

                # Occupation Distribution Top 6 - Pie Chart Format

                occupation_counts = dfc['Occupation'].value_counts().nlargest(6)
                labels_occupation_counts = occupation_counts.index.tolist()
                counts_occupation_counts = occupation_counts.values.tolist()

                #Sunburst Chart - Religion and Caste Associated - nan issue to be rectified
                temp_dfc=dfc.dropna()
                df_filtered = temp_dfc[temp_dfc['Caste'] != 'N/A']
                fig_suburst_religion= px.sunburst(df_filtered, path=['Caste', 'Religion'], title='Caste and Religion Distribution')
                plot_div_suburst_religion= fig_suburst_religion.to_html(full_html=False, include_plotlyjs='cdn') 
                # # image_data1 = fig2.to_image(format="png")
        

                # # Number of Crimes by District and Unit - Treemap format

                crime_count = dfc.groupby(['District_Name', 'UnitName'])['FIRNo'].count().reset_index()
                crime_count.columns = ['District_Name', 'UnitName', 'Count']

                fig_fir_treemap = px.treemap(crime_count, path=['District_Name', 'UnitName'], values='Count',
                                color='Count', color_continuous_scale='Viridis',
                                title='Number of Crimes by District and Unit')

                fig_fir_treemap.update_layout(
                    margin=dict(t=50, l=25, r=25, b=25),
                    font_family='Arial',
                    font_size=12
                )
                plot_div_fir_treemap = fig_fir_treemap.to_html(full_html=False, include_plotlyjs='cdn') 
                # # fig2.show()



                #Victims Info Data
                
                # # Age Distribution of the Victims
                # hist_data = np.histogram(dfv['age'], bins=30)
                # labels_victims_age = hist_data[1] 
                # values_victims_age = hist_data[0]


                # Profession wrt Age - Box Plot
                labels_profession_age = dfv['Profession'].unique()
                values__profession_age = dfv.groupby('Profession')['age'].apply(list).tolist()

                # Crime by Months - Recorded in the Victims Info - Bar Graph
                # crimes_v_month = dfv.groupby('Month')['Crime_No'].count().reset_index()
                # labels_crimes_v_month = crimes_v_month['Month'].tolist()
                # values_crimes_v_month = crimes_v_month['Crime_No'].tolist()

                crimes_by_month = dfv.groupby('Month')['Crime_No'].count().reset_index()
                fig_month_victims = px.bar(crimes_by_month, x='Month', y='Crime_No', title='Distribution of CrimeRates in Monthwisemanner', color='Month')
                plot_div_month_victims = fig_month_victims.to_html(full_html=False, include_plotlyjs='cdn') 

                # Relation of Sex and Age - Voilon Chart

                labels_sex = dfv['Sex'].unique()
                values_sex_age = dfv.groupby('Sex')['age'].apply(list).tolist()

                # Top 10 districts from Victims Info Recorded
                district_v_crimes = dfv.groupby('District_Name')['Crime_No'].count().reset_index().sort_values('Crime_No', ascending=False).head(10)
                labels_district_v_crimes = district_v_crimes['District_Name'].tolist()
                values_district_v_crimes = district_v_crimes['Crime_No'].tolist()

                # Radar Chart for the Top Profession with the Highest Crime Recorded wrt InjuryType
                filtered_df = dfv[(dfv['Profession'].notnull()) & (dfv['InjuryType'].notnull()) & (dfv['InjuryType'] != 'N/A')]
                crimes_by_prof_injury = filtered_df.groupby(['Profession', 'InjuryType'])['Crime_No'].count().reset_index()
                top_20 = crimes_by_prof_injury.sort_values('Crime_No', ascending=False).head(20)
                fig_radar_profession = px.bar_polar(top_20, r='Crime_No', theta='Profession', color='InjuryType', title='Top 20 Combinations of Profession and Injury Type by Crime Count (Excluding N/A)')
                plot_div_radar_profession = fig_radar_profession.to_html(full_html=False, include_plotlyjs='cdn') 
                # fig3.show()


                # Victim Distribution by Age Groups - Funnel Chart

                # age_bins = [0, 18, 30, 45, 60, 100]
                # age_labels = ['<18', '18-30', '30-45', '45-60', '60+']
                # dfv['age_group'] = pd.cut(dfv['age'], bins=age_bins, labels=age_labels)
                # victim_dist = dfv.groupby('age_group')['Victim_ID'].count().reset_index()
                # victims_age = victim_dist['age_group'].tolist()
                # victims_value = victim_dist['Victim_ID'].tolist()
                age_bins = [0, 18, 30, 45, 60, 100]
                age_labels = ['<18', '18-30', '30-45', '45-60', '60+']
                dfv['age_group'] = pd.cut(dfv['age'], bins=age_bins, labels=age_labels)
                victim_dist = dfv.groupby('age_group')['Victim_ID'].count().reset_index()
                fig_age_victims = px.funnel(victim_dist, x='Victim_ID', y='age_group', title='Victim Distribution by Age Groups')
                plot_div_age_victims = fig_age_victims.to_html(full_html=False, include_plotlyjs='cdn') 


                unique_crime_groups = dfm['Crime_Group1'].unique()
                color_map = {group: i for i, group in enumerate(unique_crime_groups)}
                colors = dfm['Crime_Group1'].map(color_map)

                fig_unique_crime = go.Figure(data=[go.Scatter3d(
                    x=dfm['AGE'],
                    y=dfm['Gang_Strength'],
                    z=dfm['Crime_Group1'],
                    mode='markers',
                    marker=dict(
                        size=12,
                        color=colors, # Use the color map to assign colors to each crime group
                        colorscale='Viridis', # Choose a colorscale
                        opacity=0.8
                    )
                )])

                fig_unique_crime.update_layout(scene=dict(xaxis_title='Age', yaxis_title='Gang Strength', zaxis_title='Crime Group'))
                plot_div_fig_unique_crime = fig_unique_crime.to_html(full_html=False, include_plotlyjs='cdn') 


                # Last two plots are meant to be plot on the geojson or Folium chart
                # Crimes by State - Chloropleth Plot Data
                # crimes_by_state = dfv.groupby('PresentState')['Crime_No'].count().reset_index()

                # # Crimes by City (Karnataka) - Folium Chart
                # crimes_by_city = dfv.groupby('PresentCity')['Crime_No'].count().reset_index()

                # # url = "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States"
                gdf = gpd.read_file('CrimeMapping/data/Indian_States.json')
                india_states = gdf.rename(columns={"NAME_1": "ST_NM"}).__geo_interface__
                crimes_by_state = dfv.groupby('PresentState')['Crime_No'].count().reset_index()
                fig_gpd = px.choropleth(
                    crimes_by_state,
                    locations="PresentState",
                    geojson=india_states,
                    featureidkey="properties.ST_NM",
                    locationmode="geojson-id",
                    color="Crime_No",
                    scope="asia",
                    title='Crime Distribution by State in India'
                )

                fig_gpd.update_geos(fitbounds="locations", visible=False)
                # fig.show()
                plot_div_gpd = fig_gpd.to_html(full_html=False, include_plotlyjs='cdn') 


                tempDF_Prof = dfv[dfv['age'] <= 120]

                fig_prof_comp = px.box(tempDF_Prof, x='Profession', y='age', title='Comparison of Age by Profession')
                plot_div_prof_comp = fig_prof_comp.to_html(full_html=False, include_plotlyjs='cdn') 



                # dataT = str(tempDF.values.tolist())
                data = [
                    {
                    'title': 'Most Frequent Time of FIR Reported to the Station',
                    'dataX': type_count,
                    'dataY': df_type,
                    'chartType': 'bar'
                    },
                    # {
                    # 'title': 'Which Day most no. of FIRs are reported',
                    # 'dataX': type_count2,
                    # 'dataY': df_type2,
                    # 'chartType': 'bar'
                    # },
                    {
                    'title': 'Which IPC Section is most recorded in FIR',
                    'dataX': type_count3,
                    'dataY': df_type3,
                    'chartType': 'bar'
                    }, 
                    {
                    'title': 'Age Distribution of the victim reported in the FIR Records',
                    'dataX': type_count4,
                    'dataY': df_type4,
                    'chartType': 'bar',
                    
                    },
                                    
                    # {
                    # 'title': 'Age Distribution of the RowdyShetters',
                    # 'dataX': y_age_rowdy,
                    # 'dataY': x_age_rowdy,
                    # 'chartType': 'bar'
                    # },                
                    {
                    'title': 'Category Count of Rowdy Shetter',
                    'dataX': y_rowdy_category,
                    'dataY': x_rowdy_category,
                    'chartType': 'bar'
                    },
                    {
                    'title': 'Top 10 District Name with the most Rowdy Details Recorded',
                    'dataX': y_rowdy_district,
                    'dataY': x_rowdy_district,
                    'chartType': 'bar'
                    },
                    {
                    'title': 'Top 10 Unit Name with the most Rowdy Details Recorded',
                    'dataX': y_rowdy_units,
                    'dataY': x_rowdy_units,
                    'chartType': 'bar'
                    },
                    # {
                    # 'title': 'MOBs Age vs Gang Strength more than 0, Scatter Plot',
                    # 'dataX': y_strength,
                    # 'dataY': x_age,
                    # 'chartType': 'scatter'
                    # },
                    {
                    'title': 'Top 6 Caste Recorded of MOBs',
                    'dataX': caste_values,
                    'dataY': caste_names,
                    'chartType': 'bar'
                    },
                    {
                    'title': 'Top 10 Crime Groups Recorded in MOBs',
                    'dataX': y_crime_group,
                    'dataY': x_crime_group,
                    'chartType': 'bar'
                    },
                    # {
                    # 'title': 'Relation between the Age and Crime Head2',
                    # 'dataX': y_crime_head2,
                    # 'dataY': x_crime_head2,
                    # 'chartType': 'bar'
                    # },
                    {
                    'title': 'Top 10 Occupation of Offenders Recorded in MOBs',
                    'dataX': y_occupation,
                    'dataY': x_occupation,
                    'chartType': 'bar'
                    },
                    # {
                    # 'title': 'Relation betwee the Age and the Grading',
                    # 'dataX': y_values,
                    # 'dataY': x_values,
                    # 'chartType': 'bar'
                    # },
                    # {
                    # 'title': 'Sankey Chart - MOBs Class 1 and Cass 2',
                    # 'dataX': encoded_string1,
                    # },
                    # {
                    # 'title': 'Offender Network based on the Person_No and Gang Strength',
                    # 'dataX': encoded_string2,
                    # },
                    
                    # {
                    # 'title': 'Distribution of the Crime Rates in Month wisemanner',
                    # 'dataX': labels_monthly_crimes,
                    # 'dataY': values_monthly_crimes,
                    # 'chartType': 'bar'
                    # },
                    # {
                    # 'title': 'Various Crimes at different District',
                    # 'dataX': values_district_fir,
                    # 'dataY': labels_district_fir,
                    # 'chartType': 'bar'
                    # },

                    # {
                    # 'title': 'Victim Counts vs Accused Counts',
                    # 'dataX': accused_counts,
                    # 'dataY': victim_counts,
                    # 'chartType': 'bar'
                    # },
                    #                 {
                    # 'title': 'Victim Distribution by Age',
                    # 'dataX': victims_age,
                    # 'dataY': victims_value,
                    # 'chartType': 'bar'
                    # },
                    {
                    'title': 'Top 5 Mean of Victim Count wrt CrimeGroup Name - Pie Plot',
                    'dataX': Y_top_5_crime_groups,
                    'dataY': X_top_5_crime_groups,
                    'chartType': 'bar'
                    },

                    {
                    'title': 'Top 10 Sum of Victim Count wrt CrimeGroup Name - Bar Graph',
                    'dataX': Y_top_10_crime_groups,
                    'dataY': X_top_10_crime_groups,
                    'chartType': 'bar'
                    },
                    # # {
                    # # 'title': 'Distribution of the count of FIR Recorded at which Hour',
                    # # 'dataX': values_hourly_crimes,
                    # # 'dataY': labels_hourly_crimes
                    # # },

                    # {
                    # 'title': 'Time Series Behavior of the Offence Recorded',
                    # 'dataX': values_crime_trend,
                    # 'dataY': labels_crime_trend,
                    # 'chartType': 'line'
                    # },
                    {
                    'title': 'Counts of FIR Type',
                    'dataX': values_fir_type,
                    'dataY': labels_fir_type,
                    'chartType': 'bar'
                    },
                ]
                # Convert rjdf to List of object
                # from plotly.offline import plot
                # from plotly.graph_objs import Scatter
                # x_data = [0,1,2,3]
                # y_data = [x**2 for x in x_data]
                # plot_div = plot([Scatter(x=x_data, y=y_data,
                #                     mode='lines', name='test',
                #                     opacity=0.8, marker_color='green')],
                #         output_type='div')
                # tempChart = {
                #     'crime':crime,
                #     'dataX':dataX,
                #     'dataY':dataY,
                #     'df_type':df_type,
                #     'df_type2':df_type2,
                #     'df_type3':df_type3,
                #     'df_type4':df_type4,
                #     'type_count':type_count,
                #     'type_count2':type_count2,
                #     'type_count3':type_count3,
                #     'type_count4':type_count4,
                #     'image00':plot_div_age_rowdy,
                #     'image2':plot_div_Sankey_MOB,
                #     'image3':plot_div_network_MOB,
                #     'image31':plot_div_suburst_religion,
                #     'image32':plot_div_grading_MOB,
                #     'image4':plot_div_fir_treemap,
                #     'image5':plot_div_radar_profession,
                #     'image6':plot_div_month_victims,
                #     'image7':plot_div_age_victims,
                #     'questions':data,
                # }
                # data = json.dumps(data)
                context = {
                    'crime':crime,
                    'dataX':dataX,
                    'dataY':dataY,
                    'df_type':df_type,
                    'df_type2':df_type2,
                    'df_type3':df_type3,
                    'df_type4':df_type4,
                    'type_count':type_count,
                    'type_count2':type_count2,
                    'type_count3':type_count3,
                    'type_count4':type_count4,
                    'image001':plot_div_karnataka_district,
                    'image002': plot_div_age_crime_type,
                    'image003':plot_div_strength_gt_zero,
                    'image004':plot_div_fig_unique_crime,
                    'image00':plot_div_age_rowdy,
                    'image2':plot_div_Sankey_MOB,
                    'image3':plot_div_network_MOB,
                    'image31':plot_div_suburst_religion,
                    'image32':plot_div_grading_MOB,
                    'image4':plot_div_fir_treemap,
                    'image5':plot_div_radar_profession,
                    'image6':plot_div_month_victims,
                    'image7':plot_div_age_victims,
                    
                    'image8': plot_div_gpd,
                    'image9':plot_div_prof_comp,

                    # 'x_age_rowdy':x_age_rowdy,
                    # 'x_rowdy_category':x_rowdy_category,
                    # 'x_rowdy_district':x_rowdy_district,
                    # 'x_rowdy_units':x_rowdy_units,
                    # 'x_age':x_age,
                    # 'caste_names':caste_names,
                    # 'x_crime_group':x_crime_group,
                    # 'x_crime_head2':x_crime_head2,
                    # 'x_occupation':x_occupation,
                    # 'x_values':x_values,

                    # 'labels_monthly_crimes':labels_monthly_crimes,
                    # 'labels_district_fir':labels_district_fir,
                    # 'victim_counts':victim_counts,
                    # 'X_top_5_crime_groups':X_top_5_crime_groups,
                    # 'X_top_10_crime_groups':X_top_10_crime_groups,
                    # # 'labels_hourly_crimes':labels_hourly_crimes,
                    # 'labels_crime_trend':labels_crime_trend,
                    # 'labels_fir_type':labels_fir_type,
            
                    # 'y_age_rowdy':y_age_rowdy,
                    # 'y_rowdy_category':y_rowdy_category,
                    # 'y_rowdy_district':y_rowdy_district,
                    # 'y_rowdy_units':y_rowdy_units,
                    # 'y_strength':y_strength,
                    # 'caste_values':caste_values,
                    # 'y_crime_group':y_crime_group,
                    # 'y_crime_head2':y_crime_head2,
                    # 'y_occupation':y_occupation,
                    # 'y_values':y_values,

                    # 'values_monthly_crimes':values_monthly_crimes,
                    # 'values_district_fir':values_district_fir,
                    # 'accused_counts':accused_counts,
                    # 'Y_top_5_crime_groups':Y_top_5_crime_groups,
                    # 'Y_top_10_crime_groups':Y_top_10_crime_groups,
                    # # 'values_hourly_crimes':values_hourly_crimes,
                    # 'values_crime_trend':values_crime_trend,
                    # 'values_fir_type':values_fir_type,

                    'questions':data,
                    'size':len(data),
                    }
                ChartTemp.append(context)
                return render(request, 'CrimeAnalysis/chart.html', context)
            else:
                print( ChartTemp[0], type(ChartTemp[0]),  type(ChartTemp))
                context = ChartTemp[0]
                return render(request, 'CrimeAnalysis/chart.html', context)
        else:
            return redirect('/login')

        
    def post(self, request):
        pass

























