import streamlit as st
import pandas as pd
import plotly.express as px
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Super Store Dashboard", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Super Store EDA")
st.markdown('<style>div.block-container{padding-top: 2rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload your CSV file", type=["csv", "txt", "xlsx", "xls"])
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(fl, encoding="ISO-8859-1")
else:
    os.chdir(r"C:\Users\AI NetMan\Documents\GitHub\Super_Store")
    df = pd.read_csv("Superstore.csv", encoding = "ISO-8859-1")

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

#Getting the min and max date from the dataset
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filter the dataframe based on the selected date range
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Filter Options")
st.sidebar.markdown("### Select the filters you want to apply")

# Create for region
region = st.sidebar.multiselect("Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Create for state
state = st.sidebar.multiselect("State", df2["State/Province"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State/Province"].isin(state)] 

# Create for city
city = st.sidebar.multiselect("City", df3["City"].unique())

#Filter the data based on Region, State and City

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State/Province"].isin(state)]
elif state and city:
    filtered_df = df3[df["State/Province"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State/Province"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State/Province"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by = ["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category by Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height = 200)

with col2:
    st.subheader("Region by Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((1, 1))
with cl1:
    with st.expander("category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues").set_properties(**{'text-align': 'left'}))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv, file_name="category.csv", mime="text/csv",
                             help="Download the data as a CSV file")
with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges").set_properties(**{'text-align': 'left'}))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv, file_name="region.csv", mime="text/csv",
                             help="Download the data as a CSV file")

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Sales by Month") 

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y = "Sales", labels={"month_year": "Month - Year","Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of Time Series"):
    st.write(linechart.style.background_gradient(cmap="Greens").set_properties(**{'text-align': 'left'}))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV", data=csv, file_name="linechart.csv", mime="text/csv",
                        help="Download the data as a CSV file")

#Create a tream based on Region, category, sub-category

st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", color="Sales",
                  color_continuous_scale="RdBu", template="seaborn")
fig3.update_traces(textinfo="label+value+percent entry")
fig3.update_layout(margin=dict(t=50, l=25, r=25, b=25), height=500, width=1000)
st.plotly_chart(fig3, use_container_width=True)


cln1, cln2 = st.columns(2)
with cln1:
    st.subheader("Sales by Segment, Category and Sub-Category")
    fig = px.sunburst(filtered_df, path=["Segment", "Category"], values="Sales", color="Sales",
                    color_continuous_scale="RdBu", template="seaborn")
    fig.update_traces(textinfo="label+percent entry", hovertemplate='%{label}<br>%{value: #}<br>%{percentParent:.2%}')
    fig.update_layout(coloraxis_showscale=False, margin=dict(t=50, l=25, r=25, b=25), height=500, width=1000)
    st.plotly_chart(fig, use_container_width=True)

with cln2:
    with st.expander("View Data of Sales by Segment and Category"):
        segment_category_df = filtered_df.groupby(by=["Segment", "Category"], as_index=False)["Sales"].sum()
        st.write(segment_category_df.style.background_gradient(cmap="Purples").set_properties(**{'text-align': 'left'}))
        csv = segment_category_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv, file_name="segment_category.csv", mime="text/csv",
                           help="Download the data as a CSV file")

import plotly.figure_factory as ff

st.subheader("Summary of Dataset")
with st.expander("View Data of Summary"):
    df_sample = df[0:5][["Region", "State/Province", "City", "Category", "Sales", "Profit", "Quantity",]]
    fig = ff.create_table(df_sample, height_constant=20, colorscale=[[0, "lightblue"], [1, "lightgreen"]])
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25), height=500, width=1000)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month by Sub-Category")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    month_subcategory_df = pd.pivot_table(filtered_df, index="Sub-Category", columns="month", values="Sales")
    month_subcategory_df = month_subcategory_df.fillna(0).reset_index()
    month_subcategory_df = month_subcategory_df.rename_axis(None, axis=1)
    st.write(month_subcategory_df.style.background_gradient(cmap="Reds").set_properties(**{'text-align': 'left'}))
    
#Create a scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1['layout'].update(title="Relationship b/w Sales and Profit")
st.plotly_chart(data1, use_container_width=True)