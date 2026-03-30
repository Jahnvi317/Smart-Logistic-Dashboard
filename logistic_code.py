import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.markdown("""
            <h1 style='font-family : sans-serif; color: white;font-weight: 800;'>
             Smart Logistics Dashboard
            """
            ,unsafe_allow_html=True
             )

st.sidebar.header("Dataset Overview")
option = st.sidebar.selectbox("Select a analysis type",["","Logistics Delay Reasons Analysis","Top Assets with Inventory Shortage",
                                                        "Traffic Status vs Waiting Time Analysis","Average Waiting Time by Traffic Status and Delay Reason",
                                                        "Assets at Stock Risk Analysis","Customer Value Segmentation Analysis"])
df = pd.read_csv("smart_logistics_dataset.csv")
df['index'] = df.index


if st.sidebar.checkbox("Show raw data"):
     st.subheader("Raw Data")
     st.dataframe(df)

if st.sidebar.checkbox("Show summary statistics"):
     st.subheader("Summary Statistics")
     st.write(df.describe())

#-----------------------------------------------------------------------------------------------------------
# Clean and categorize delay reasons
if option == "Logistics Delay Reasons Analysis":
     st.subheader("Logistics Delay Reasons Analysis")

     #fill missing values in 'Logistics_Delay_Reason' with "Unknown"
     df['Logistics_Delay_Reason']=df['Logistics_Delay_Reason'].fillna("Unknown")

     #pivot table to count delay reasons by asset
     temp_df= df.pivot_table(index='Asset_ID',values='Logistics_Delay',columns ='Logistics_Delay_Reason',aggfunc='count')
     fig =px.imshow(temp_df,labels=dict(x="Logistics Delay Reason",y="Vehicle ID")
                          ,color_continuous_scale='Viridis',text_auto= True,aspect="auto")
     st.plotly_chart(fig)
     st.markdown("""This heatmap identifies specific delay patterns by mapping Logistics Delay Reasons against Vehicle IDs.
                  It highlights which assets are most frequently impacted by specific bottlenecks, 
                 allowing for targeted operational improvements.""")

#-----------------------------------------------------------------------------------------------------------
#Demand vs Inventory gap
if option == "Top Assets with Inventory Shortage":
     st.subheader("Top Assets with Inventory Shortage")

     df['Inventory_gap'] = df['Demand_Forecast'] - df['Inventory_Level']
     shortage_df = df[df['Inventory_gap']>0].sort_values('Inventory_gap',ascending=False)

     fig2=px.bar(shortage_df,x='Asset_ID',y='Inventory_gap',text_auto='.0s')
     fig2.update_layout(xaxis_title=None,yaxis_visible=False,template='plotly_dark')
     st.plotly_chart(fig2)
     st.write("A prioritized view of inventory gaps where demand exceeds current stock." \
     " This chart identifies the specific Asset IDs requiring immediate replenishment to prevent fulfillment failures.")

#-----------------------------------------------------------------------------------------------------------
#Traffic & Delay Correlation
if option == "Traffic Status vs Waiting Time Analysis":
     st.subheader("Traffic Status vs Waiting Time Analysis")
     st.plotly_chart(px.box(df,x='Traffic_Status',y='Waiting_Time'))
     st.write("This distribution analysis visualizes how different traffic conditions impact vehicle waiting times. It helps in understanding the variance and outliers in delivery performance caused by external traffic factors.")
#-----------------------------------------------------------------------------------------------------------
#the Multi factor pivot
if option == "Average Waiting Time by Traffic Status and Delay Reason":
     st.subheader("Average Waiting Time by Traffic Status and Delay Reason")
     pivot_analysis = df.groupby(['Traffic_Status','Logistics_Delay_Reason'])['Waiting_Time'].mean().unstack()
     st.write(pivot_analysis)
     st.plotly_chart(px.imshow(pivot_analysis,text_auto=True,title="Avg Waiting Time Heatmap",labels=dict(x="Delay Reason",
                              y="Traffic Status",color="Avg Waiting Time"),color_continuous_scale='Cividis'))
     st.write("A deep-dive into the combined impact of traffic and delay reasons on waiting times. This visualization pinpoint which specific combinations (e.g., Heavy Traffic + Documentation) cause the most significant delays.")
#-----------------------------------------------------------------------------------------------------------
#the stock risk analysis
if option == "Assets at Stock Risk Analysis":
     st.subheader("Assets at Stock Risk Analysis")
#calculate ratio
     df['supply_demand_ratio']=df['Inventory_Level']/(df['Demand_Forecast']+0.001)
#filter for "At Risk" assets
     at_risk=df[df['supply_demand_ratio']<1.0].sort_values('supply_demand_ratio')
     st.plotly_chart(px.bar(at_risk,x='Asset_ID',y='supply_demand_ratio',text_auto=True))

     st.write("this analysis identifies assets at risk of stockouts by calculating the supply-demand ratio. Assets with a ratio below 1.0 are highlighted as 'At Risk', indicating that current inventory levels are insufficient to meet forecasted demand, necessitating urgent attention for replenishment.")
#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
# customer value segmenting
if option == "Customer Value Segmentation Analysis":
     st.subheader("Customer Value Segmentation Analysis")
     #3d bubble chart on transaction value, purchase frequency, and shipment status
     fig3=px.scatter_3d(df,x='User_Purchase_Frequency',y='User_Transaction_Amount',z='Shipment_Status',size='User_Transaction_Amount',color='Shipment_Status')
     fig3.update_layout(scene=dict(xaxis_title='Purchase Frequency',yaxis_title='Transaction Amount',zaxis_title='Shipment Status'),template='plotly_dark')
     st.plotly_chart(fig3)

     st.write("This 3D scatter plot segments customers based on their purchase frequency, transaction amount, and shipment status. It helps identify high-value customers and those with potential delivery issues, enabling targeted marketing and improved customer service strategies.")
