import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import plotly.figure_factory as ff
from mockingResponse import *


# define global vars
headers = {"accept": "application/json", "X-Api-key" : "key_96722ad209ed03b38756862ecdd76b01"}
background_color = '#fff'
max_hist_data_points = 200
on_market_data_points_limit = 10
weekly_price_threshold = 2000


def getHTMLText(url):
    try:
        hd = {"user-agent": 'Mozilla/5.0'}
        r = requests.get(url, timeout=30, headers=hd)
        r.raise_for_status()
        r.encoding = r.apparent_encoding

        return r.text
    except:
        return ""


def get_property_rent_history(address):
    raw_html = getHTMLText(
        'https://www.domain.com.au/building-profile/' + address + '?filtertype=rented&pagesize=1000&pageno=1')
    # print(raw_html)
    soup = BeautifulSoup(raw_html, 'html.parser')
    # print(soup)
    list_tags = soup.find_all(class_="css-t7tdkc")
    properties = list_tags[1].find_all(class_='css-3c3rcn')
    df = pd.DataFrame(columns=['building_name', 'room_no', 'price', 'date', 'bed', 'bath', 'parking'])
    print(len(properties))
    # loop through each property
    count = 0
    for pro in properties:
        # print(pro)
        if (count >= max_hist_data_points):
            break
        count += 1
        price = pro.find(class_='css-1cq7t6n').text[1:]
        if price[-1] == 'K' or price[-1] == 'k':
            price = float(price[:-1]) * 1000
        else:
            try:
                price = float(price)
            except ValueError:
                print(price)
                price = None

        # print(price)
        room_no = pro.find('meta')['content'].split('/')[0]
        # print(address1)
        year = pro.find(class_='css-bdklbo').text
        month_date = pro.find(class_='css-rxoubj').text
        # print(year)
        # print(month_date)
        # get room number
        no_rooms = pro.findAll(class_='css-1ie6g1l')
        res = []
        for r in no_rooms:
            # print(r.find(class_ = 'css-1rzse3v').text)
            temp = r.find(class_='css-1rzse3v').text.split(" ")[0]
            try:
                res.append(int(temp))
            except ValueError:
                res.append(0)

        try:
            df = df.append({
                'building_name': address,
                'room_no': int(room_no),
                'price': price,
                'date': pd.to_datetime(year + month_date, format='%Y%b %d'),
                'bed': res[0],
                'bath': res[1],
                'parking': res[2]
            }, ignore_index=True)
        except ValueError:
            print(room_no)

    new_dtypes = {"room_no": pd.Int64Dtype(),
                  "price": pd.Int64Dtype(),
                  'bed': pd.Int64Dtype(),
                  'bath': np.integer,
                  'parking': pd.Int64Dtype()}

    df = df.astype(new_dtypes)
    df['room_type'] = (df['room_no'] % 100).astype(str)

    df['level'] = df['room_no'] // 100

    return df


def get_hist_trend_plot(hist_df, title = ""):
    hist_df.loc[:, "room_type_2"] = hist_df['bed'].astype(int).astype(str) + "b" + hist_df['bath'].astype(int).astype(str) + "b"
    fig = px.scatter(hist_df[hist_df.price.notna()], x="date", y="price", color="room_type_2", title=title)
    fig.add_vline(x=pd.to_datetime('20200301', format='%Y%m%d'), line_width=3, line_dash="dash", line_color="green")
    #fig.update_layout( plot_bgcolor=background_color,paper_bgcolor=background_color)
    fig.update_layout(
        title = '<b>History Rentals Price vs. Time</b>',
        xaxis_title="Time",
        yaxis_title="Weekly Rent ($)",
        legend_title="Bed/Bath",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple"
        )
    )
    return fig


def get_percentage_price_change_table(hist_df, group_col, price_col,split_on = '20200301'):

    median_price_before_df = hist_df[hist_df.date <= pd.to_datetime(split_on, format='%Y%m%d')]
    median_price_after_df = hist_df[hist_df.date > pd.to_datetime(split_on, format='%Y%m%d')]
    perc_change_df = pd.DataFrame(median_price_after_df.groupby(group_col)[price_col].median())
    perc_change_df = perc_change_df.rename({price_col: 'med_price_after'}, axis=1)
    perc_change_df.loc[:, "med_price_before"] = median_price_before_df.groupby(group_col)[price_col].median()
    perc_change_df.loc[:, "raw_change"] =  perc_change_df["med_price_after"] - perc_change_df["med_price_before"]
    perc_change_df.loc[:, "perc_change"] = perc_change_df["raw_change"] / perc_change_df["med_price_before"]
    perc_change_df = perc_change_df.join(pd.DataFrame(hist_df[group_col].value_counts()).rename({group_col: "count"}, axis = 1))

    #tdata = [['room<br>type', "median<br>price<br>before", "median<br>price<br>after", "raw<br>difference",
    #          "percentage<br>change"]]
    #print(perc_change_df)
    tdata = []
    for room_type in perc_change_df.index:
        #print(perc_change_df.loc[room_type,:])
        if pd.isna(perc_change_df.loc[room_type,'med_price_before']) or pd.isna(perc_change_df.loc[room_type,'med_price_after']) :
            tdata.append([room_type,
                          "$" + str(perc_change_df.loc[room_type, 'med_price_before']),
                          "$" + str(perc_change_df.loc[room_type, 'med_price_after']),
                          "N/A",
                           "N/A",
                          ])

        else:
            tdata.append([room_type,
                          "$" + str(perc_change_df.loc[room_type, 'med_price_before']),
                          "$" + str(perc_change_df.loc[room_type, 'med_price_after']),
                          "$" + str(perc_change_df.loc[room_type, 'raw_change']),
                          str(round(perc_change_df.loc[room_type, 'perc_change'] * 100, 2)) + " %",
                          ])

    perc_change_df = perc_change_df.reset_index()

    perc_change_df["color"] = perc_change_df['raw_change'].map(lambda p: "green" if ( pd.isna(p) or p <=0) else "red")

    col_to_show = ["room_type_2", 'med_price_after', 'med_price_before', 'raw_change', 'perc_change']

    text_color = []
    n = len(perc_change_df)
    for col in col_to_show:
        if col != 'raw_change' and col != "perc_change":
            text_color.append(['#808080'] * n)
        else:
            text_color.append(perc_change_df["color"].to_list())

    header_text = ['<b>room<br>type</b>', "<b>median<br>rent<br>before</b>", "<b>median<br>rent<br>after</b>",
                   "<b>raw<br>difference</b>", "<b>percentage<br>change</b>"]
    data = [go.Table(
        #     columnwidth = [15,20,30],
        header=dict(values=header_text,
                    fill_color='#e3e3e3',
                    line_color='white',
                    align='center',
                    font=dict(color="#808080", family="Lato", size=15),
                    height=30
                    ),
        cells=dict(values=pd.DataFrame(tdata).values.T,

                   # line_color='darkslategray',
                   align='left',
                   font=dict(color=text_color, family="Lato", size=15),
                   fill_color=['#f5f5f5'],
                   height=30
                   ))
    ]

    fig = go.Figure(data=data)
    fig.update_layout(
        title="<b>Median Rent Before and After Covid</b>",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple"
        )
    )
    #fig.update_layout(plot_bgcolor=background_color,paper_bgcolor=background_color)
    #fig.update_layout(width=600, height=600)
    return fig


#@mock.patch('requests.get', side_effect=mocked_requests_get)
def get_on_market_plots(address):
    #  ----------- get a list of listing id for on market listing -----------
    page_no = 1
    on_market_list = []
    while True:
        cur_list_url = 'https://www.domain.com.au/building-profile/' + address + '?filtertype=forRent&pagesize=10&pageno=' + str(
            page_no)
        raw_html = getHTMLText(cur_list_url)
        page_no += 1

        soup = BeautifulSoup(raw_html, 'html.parser')
        # print(soup)
        list_tags = soup.find_all(class_="css-t7tdkc")
        properties = list_tags[0].find_all(class_='css-3c3rcn',
                                           attrs={"data-testid": 'nearby-properties__on-market-property'})
        for prop in properties:
            list_id = prop.find_all("a")[0]['href'].split("-")[-1]
            # print(list_id)
            on_market_list.append(list_id)
        if (len(properties) == 0):
            break

        # TODO remove this check to get full list of properties
        if len(on_market_list) >= on_market_data_points_limit:
            break

                #  ----------- init the info df -------------------------------
    on_market_df = pd.DataFrame(
        columns=["list_id", "status", 'room_no', 'price', 'list_date', 'bed', 'bath', 'parking', 'agency_id'])
    #requests_count += len(on_market_list)
    # ----------- fetch from listing API  ---------------------------------
    print(on_market_list)
    for list_id in on_market_list:
        list_url = 'https://api.domain.com.au/sandbox/v1/listings/'
        list_res = requests.get(list_url + str(list_id), headers=headers)
        if (list_res.status_code == 200):
            json_res = list_res.json()
            #print(list_id)
            try:
                carspaces = json_res['carspaces']
            except:
                carspaces = 0
            try:
                room_no = re.search("[0-9][0-9]*", json_res["addressParts"]["unitNumber"]).group()
            except:
                room_no = re.search("[0-9][0-9]*", json_res["addressParts"]["streetNumber"]).group()

            raw_price = json_res['priceDetails']['displayPrice']
            price = float(re.search("[0-9][0-9]*", raw_price).group())
            re.search("[0-9][0-9]*[^0-9]", raw_price)
            on_market_df = on_market_df.append({"list_id": list_id,
                                                'room_no': room_no,
                                                "price": price,
                                                "list_date": json_res['dateListed'],
                                                "status": json_res["status"],
                                                "bed": float(json_res['bedrooms']),
                                                "bath": float(json_res['bathrooms']),
                                                "parking": float(carspaces),
                                                "agency_id": json_res['advertiserIdentifiers']['advertiserId'],


                                                }, ignore_index=True)
        else:
            print("status code: " + str(list_res.status_code))
    #print(requests_count)

    # ----------- data cleaning   --------------------------------
    #print(on_market_df)
    on_market_df[ "list_date"] = pd.to_datetime(on_market_df['list_date'].map(lambda p: p.split("T")[0]),
                                                              format="%Y-%m-%d")
    on_market_df[ "up_days"] = on_market_df["list_date"].map(lambda p: (date.today() - p.date()).days)

    on_market_df[ "up_days"] = on_market_df["list_date"].map(lambda p: (date.today() - p.date()).days)
    on_market_df[ "room_type"] = on_market_df['bed'].astype(int).astype(str) + "b" + on_market_df['bath'].astype(int).astype(str) + "b"
    #print(on_market_df["up_days"])
    # ------------ strip Plot ---------------------------------
    fig0 = px.strip(on_market_df[on_market_df.price.notna()], x="room_type", y="price", hover_data=['up_days', 'list_id'],
                    color="room_type",custom_data=["room_no", "agency_id","up_days", "list_id"])
    fig0.update_layout(showlegend=False,clickmode='event+select')


    # -------------- info table ----------------------------------
    table_data = [['room<br>type', 'on market<br>count', 'median<br>price(pw)', 'lowest<br>price', "highest<br>price",
                   "standard<br>deviation"]]

    def fill_table_data(df):
        try:
            table_data.append([df.iloc[0, :]["room_type"],
                               len(df), "$" + str(df.price.median()),
                               "$" + str(df.price.min()),
                               "$" + str(df.price.max()),
                               "$" + str(round(df.price.std(), 2))
                               ])
        except:
            print("fill_table_data_error")
            print(df)

    on_market_df.groupby("room_type").apply(fill_table_data)

    fig = ff.create_table(table_data)

    # ------------ update layouts -----------------

    fig.update_layout(
        title='<b>On Market Price Summary</b>',
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple"
        )
    )

    fig0.update_layout(
        title='<b>'+ str(len(on_market_list)) + ' properties are On Market for Rent</b>',
        xaxis_title="Bed/Bath",
        yaxis_title="Weekly Rental Price ($)",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple"
        )
    )
    return fig0, fig



def timeline_plot(room_no,address, current_price, cur_up_days,cur_agency):
    prop_url = 'https://www.domain.com.au/property-profile/' + str(room_no) + "-" + address
    print(prop_url)
    raw_html = getHTMLText(prop_url)
    soup = BeautifulSoup(raw_html, 'html.parser')
    # print(soup)
    list_tags = soup.find_all(class_="css-m3i618")
    timeline_df = pd.DataFrame(columns=["Date", "Price","raw_price", "days", "Type", "Agency"])
    # for each record
    if len(list_tags) == 0:
        print("wrong url " + prop_url)
        return None

    for hist in list_tags[0].find_all(class_="css-16ezjtx"):
        #print(hist.prettify())

        agency = hist.find(class_='css-1b9tx6v')
        if agency is None:
            agency = None
        else:
            agency = agency.text

        # this_type = hist.find(class_='css-bl2deh')
        # if this_type is None:
        #     this_type = hist.find(class_='css-jcs3kb').text
        # else:
        #     this_type = this_type.text

        timeline_df = timeline_df.append({
            "Date": hist.find(class_='css-vajoca').text + hist.find(class_='css-1qi20sy').text,
            "Price": hist.find(class_='css-6xjfcu').text + hist.find(class_='css-obiveq').text,
            "raw_price":  hist.find(class_='css-6xjfcu').text[1:],
            "Type": hist.find(class_='css-1oi8ih3').text,
            "days": hist.find(class_='css-zwto9f').text,
            "Agency": agency

        },
            ignore_index=True)

    print(timeline_df)
    if (len(timeline_df) == 0):
        return None

    timeline_df["date_date"] = pd.to_datetime(timeline_df["Date"], format="%b%Y")

    def convert_num_price(p):
        # some weekly price are monthly price
        if p[-1] == 'k' or p[-1] == 'K':
            price_num = int(p[:-1].replace(',', ''))
            return price_num * 1000
        price_num = int(p.replace(',', ''))
        if price_num > weekly_price_threshold:
            # this is a monthly price
            price_num = int(price_num/30 * 7)
        return price_num



    timeline_df["price_num"] = timeline_df["raw_price"].map(convert_num_price)

    timeline_df["description"] = "<b>$" + timeline_df["price_num"].astype(int).astype(str) + "</b> per week<br>Listed for <b>" + \
                             timeline_df["days"] + " </b>days<br>by " + timeline_df["Agency"]

    # get the rent hist
    df = timeline_df[timeline_df.Type == "Listed by"]
    if len(df) ==0:
        return None
    df['marker_color'] = "blue"


    # TODO add the current list
    df = df.append({
        "date_date":pd.to_datetime('today') ,
        "price_num": current_price,
        "Type": "Listed by",
        "days": str(cur_up_days),
        "Agency": cur_agency,
        "description" : "current listing",
        "marker_color" : 'red',

    },
        ignore_index=True)


    # plot ------
    fig = go.Figure(data=go.Scatter(x=df['date_date'],
                                    y=df["price_num"],
                                    mode="lines+text+markers",
                                    text=df["description"],
                                    textposition="top center",
                                    textfont={'family': "Times", 'size': 13},
                                    marker=dict(size=8, color = df["marker_color"])
                                    ),
                    layout = go.Layout(margin=dict(t=22, b= 1, r=0,l=0))
                    )

    # TODO make xaxis-range dynamic
    # TODO make yaxis-range fix with min, max price
    time_range = df.date_date.max() - df.date_date.min()
    fig.update_layout(yaxis_range=[df.price_num.min() * 0.7, df.price_num.max() * 1.5],
                      xaxis_range=[df.date_date.min() - time_range/4,  df.date_date.max() + time_range/4])

    fig.update_layout(
        title='Rent History of Room ' + str(room_no),
        xaxis_title="Time",
        yaxis_title="Weekly Rental Price ($)",
        font=dict(
            family="Courier New, monospace",
            color="RebeccaPurple"
        )
    )

    return fig




