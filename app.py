"""
# Streamlit demo app
    This app`s objective is to transform the Airbnb AED into an actual visual and interactive AED. Feel free to copy or
    use some of the code presented below on your projects! :)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import pickle as pk
# emojis for page_icon (favicon): https://www.webfx.com/tools/emoji-cheat-sheet/

# Basic page configuration: Page title, favicon (page_icon) and layout preposition
st.set_page_config(
    page_title='EDA - Airbnb no Rio de Janeiro',
    page_icon=':ocean:',
    layout='wide'
)


# Dataframe used for the whole page. Data transformation and a few changes to the dimensionality of it.
df = pd.read_csv(
    "http://data.insideairbnb.com/brazil/rj/rio-de-janeiro/2021-12-24/visualisations/listings.csv",
    usecols={"id", "name", "host_id", "host_name", "neighbourhood", "latitude", "longitude", "room_type", "price",
             "minimum_nights", "number_of_reviews", "availability_365"}
)
# For memory and performance wise, here we're gonna limit our dataset to places that costs less than 6000
# and more than 0
df = df.loc[(df['price'] > 0) & (df['price'] <= 6000)]
# Now let us rename our dataset columns to more good looking names
column_names = {
    "name": "Name",
    "host_name": "HostName",
    "neighbourhood": "Neighbourhood",
    "room_type": "RoomType",
    "price": "Price",
    "minimum_nights": "MinimumNights",
    "number_of_reviews": "NumberOfReviews",
    "availability_365": "Availability365"
}
df = df.rename(columns=column_names)

# ---- Sidebar ----
st.sidebar.header("Use the filters below to interact with the page! :smile:")
st.sidebar.markdown("-----")

neighbourhood = st.sidebar.multiselect(
    "Select one or more neighbourhoods:",
    options=df['Neighbourhood'].unique(),
    default=df['Neighbourhood'].loc[(df['Neighbourhood'] == 'Copacabana')].unique()
)

room_type = st.sidebar.multiselect(
    "Select one or more room types:",
    options=df['RoomType'].unique(),
    default=df['RoomType'].loc[(df['RoomType'] == 'Entire home/apt')].unique()
)


minimum_nights = st.sidebar.number_input(
    "Select a minimum number of nights:",
    1, 1000, value=1
)
maximum_nights = st.sidebar.number_input(
    "Select a maximum number of nights:",
    1, 1000, value=30
)


price_range = st.sidebar.slider(
    "Select a price range:",
    int(round(df['Price'].min())),
    int(round(df['Price'].max())),
    value=400
)

name_select = st.sidebar.text_input(
    "Wanna search for a specific location? Type it's name in here! (Attention: case sensitive)"
)


# Main Page: Main page and its graphical demonstrations
st.title(":ocean: Airbnb: Rio de Janeiro locations")
st.markdown("-----")

# Upper side KPI's
df_selection = df[["Name", "Neighbourhood", "RoomType", "MinimumNights", "Availability365", "NumberOfReviews", "Price"]].query(
    "Neighbourhood == @neighbourhood & RoomType == @room_type & MinimumNights >= @minimum_nights & MinimumNights <= @maximum_nights & Price <= @price_range & Name.str.contains(@name_select)", engine='python'
)
average_price = round(df_selection['Price'].mean(), 2)
money = ":moneybag:"
total_ratings = int(df_selection['NumberOfReviews'].sum())
star = ":star:"
average_availability = round(df_selection['Availability365'].mean(), 2)

# Structure
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.markdown("<strong style='font-size: 20px;'>Average price: </strong>",
                unsafe_allow_html=True)
    st.subheader(f"{money}    R${average_price:,}")
    st.write(' ')
with middle_column:
    st.markdown("<strong style='font-size: 20px;'>Total ratings: </strong>",
                unsafe_allow_html=True)
    st.subheader(f"{star} {total_ratings}")
    st.write(' ')
with right_column:
    st.markdown("<strong style='font-size: 20px;'>Availability 365: </strong>",
                unsafe_allow_html=True)
    st.subheader(f"{average_availability}")
    st.markdown("<i style='font-size: 14px;'>Average availability on the year, in days</i>",
                unsafe_allow_html=True)

st.markdown("----")

# Middle page content
# Dynamic table for individual listing and selections
st.markdown("<center><strong>Available places to rent<strong></center>",
            unsafe_allow_html=True)
st.markdown("<center><strong style='font-size:14px;'>You can order the listings by clicking on the columns name<strong></center>",
            unsafe_allow_html=True)
st.dataframe(df_selection)

# Plots
left_column, right_column = st.columns(2)
# Top 10 cheapest places
with left_column:
    top10_cheapest = px.bar(df_selection[:10],
                            y='Name',
                            x='Price',
                            orientation='h',
                            title="Top 10 cheapest listings")
    top10_cheapest.update_yaxes(categoryorder='total descending')
    top10_cheapest.update_layout(xaxis=dict(showgrid=False),
                                 yaxis=dict(showgrid=False))
    top10_cheapest.update_layout(yaxis_title=None)
    st.plotly_chart(top10_cheapest)

with right_column:
    top10_most_reviewed = px.bar(df_selection[:10],
                                 y='Name',
                                 x='NumberOfReviews',
                                 orientation='h',
                                 title="Top 10 most reviewed")
    top10_most_reviewed.update_yaxes(categoryorder='total ascending')
    top10_most_reviewed.update_layout(xaxis=dict(showgrid=False),
                                      yaxis=dict(showgrid=False))
    top10_most_reviewed.update_layout(yaxis_title=None)
    st.plotly_chart(top10_most_reviewed)


# Machine learning model to predict the value of a room with a few especifications.
# For this case, i've developed the model on a separate jupyter notebook, that you can find on the repo.
# Here we're gonna load our model and put all the necessary inputs to call the predict function.
filename = 'regr_model.sav'
model = pk.load(open(filename, 'rb'))


# First let'us creat our function to predict the value using the model parameters.

def make_prediction(bairro, quarto, noites, dias_disponiveis):
    bairro = bairro[0]
    bairro =int(bairro)
    quarto = quarto[0]
    quarto = int(quarto)
    values = (bairro, quarto, noites, dias_disponiveis)
    prediction = model.predict([values])
    return st.success("Probably, the cost of this rent will be around R$"+format(float(str(prediction).replace('[','').replace(']','')), '.2f')+" per night.")

# Now let's make our inputs
st.markdown('----')
st.markdown("<center><strong style='font-size:18px;'>Room value prediction<strong></center>",
            unsafe_allow_html=True)
st.markdown("<center><p style='font-size: 12px;'>Want to predict a room value that's not on the listing above? Use the inputs below!<p></center>",
            unsafe_allow_html=True)

# Neighbourhood
neighbourhood_list = pd.read_csv('bairros.csv', delimiter=';')

left_column3, right_column3 = st.columns(2)
with left_column3:
    neighbourhood_selected = st.selectbox(
        'Choose the neighbourhood:',
        neighbourhood_list,
        key='neighbourhood-selectbox'
    )
    minimum_nights_selected = st.number_input('For how many nights?',
                                              min_value=1,
                                              max_value=1000,
                                              format='%i',
                                              key="minimum_nights-input"
                                              )
with right_column3:
    room_type_selected = st.selectbox(
        'Select the room type:',
        ('0 - Entire home/apt', '1 - Private room', '2 - Shared room', '3 - Hotel room'),
        key="room_type_selected-selectbox"
    )
    availability_365_selected = st.number_input('And the availability 365?',
                                                min_value=1,
                                                max_value=365,
                                                format='%i',
                                                key='availability-input'
                                                )

predict_cost_button_disabled = st.button(
        'Predict the cost',
        key='enabled-button',
        on_click=make_prediction(neighbourhood_selected,
                                 room_type_selected,
                                 minimum_nights_selected,
                                 availability_365_selected)
)
