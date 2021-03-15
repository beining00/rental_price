# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from api_handlers import *
import json



#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

# ----------------- Get figures ----------------------------------
start_address = ''

def get_toasts( toastid):
    toast = html.Div(
        [

            dbc.Toast(
                "make sure the address is entered correctly",
                id=toastid,
                header="Wrong Address",
                is_open=False,
                dismissable=True,
                icon="danger",
                # top: 66 positions the toast below the navbar
                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            ),
        ]
    )
    return toast

left_toast = get_toasts("left_wrong_address_toast")
right_toast = get_toasts("right_wrong_address_toast")
# --------------------------------------------------------------------
app.layout =html.Div(children = [

                        html.Div([
                                # app header
                                html.Div([

                                    html.Div(
                                        [
                                            html.H3(
                                                "apartment rent comparator",
                                                className="uppercase title",
                                            ),
                                            html.Span("Developed by ", className="uppercase bold"),
                                            html.Span(
                                                "Beining Chen   "
                                            ),
                                            html.Span("powered by ", className="uppercase bold"),
                                            html.Span("Plotly-Dash"),
                                            html.Br(),
                                            html.Span("input ", className="uppercase bold"),
                                            html.Span(
                                                "an apartment building address to obtain the rented/on-market properties report "
                                            ),
                                        ])
                                        ],className="app__header",
                                    ),

                                # split to two columns
                                dbc.Row(
                                    [
                                        # address input area
                                        dbc.Col(
                                            children=[
                                                dbc.Row(
                                                    [
                                                        dbc.Col(dcc.Input(id="left_street_address", type="text",
                                                                          value = start_address,placeholder="street address"
                                                                        , debounce=False),width={"size": 3}),
                                                        dbc.Col(dcc.Input(id="left_suburb_name", type="text",
                                                                          value=start_address,
                                                                          placeholder="suburb name"
                                                                          , debounce=False, ),width={"size": 3} ),
                                                        dbc.Col(dcc.Input(id="left_postcode", type="text",
                                                                          value=start_address,
                                                                          placeholder="postcode"
                                                                          , debounce=False), width={"size": 3}),
                                                        dbc.Col(dbc.Button("Search", disabled = True,color="primary", className="mr-1", id= "left_search"),width={"size": 3})

                                                    ]
                                                ),

                                                # toast
                                                left_toast,


                                                # On market
                                                html.H4("On Market Properties at"),
                                                html.H5(id = "left_on_market_title"),

                                                html.Hr(),

                                                # current listing
                                                dcc.Graph(
                                                    id='left_on_market_graph',
                                                    className="graph",
                                                ),

                                                # collapse specific property
                                                html.Div(
                                                    [
                                                        dbc.Button(
                                                            "Specific Property Lookup",
                                                            id="left_collapse_button",
                                                            className="mb-3",
                                                            color="primary",
                                                        ),
                                                        dbc.Collapse(dbc.Card(dbc.CardBody([
                                                                            html.Span("No history to show", id = "no_hist_text"),
                                                                            html.Span("Click on the dots in <b>the On-market graph<\b> to "
                                                                                      "see the renting history of a specific property",
                                                                                      id = "hist_instruction_text"),
                                                                           # current listing
                                                                           dcc.Graph(
                                                                               id='specific_property_hist',
                                                                               className="small_graph",
                                                                           ),



                                                                           ])),
                                                            id="left_collapse",
                                                            #className = "collapse_content"
                                                        ),
                                                    ]
                                                ),



                                                # on market table
                                                dcc.Graph(
                                                    id='left_on_market_table',
                                                    className="graph",

                                                ),

                                                # Rent History
                                                html.H4("Properties Renting History at"),
                                                html.H5(id = "left_history_title"),
                                                html.Hr(),



                                                # hist_trend_graph
                                                dcc.Graph(
                                                id='left_hist_trend_graph',
                                                    className= "graph",


                                                ),

                                                # increase and decease
                                                dcc.Graph(
                                                    id='left_price_change_table',
                                                    className="graph",



                                                ),




                                            ],
                                            width={"size": 6, "order": "first"},
                                            className = "my_column",


                                        ),

                                        dbc.Col(
                                            children=[
                                                      dcc.Input(id="address2", type="text", value = start_address,placeholder="apartment address",
                                                                debounce=True,className="app__input"),
                                                # On market
                                                html.H4("On Market Properties at"),
                                                html.H5(id = "right_on_market_title"),

                                                html.Hr(),

                                                # current listing
                                                dcc.Graph(
                                                    id='right_on_market_graph',
                                                    className="graph",



                                                ),

                                                # collapse specific property
                                                html.Div(
                                                    [
                                                        dbc.Button(
                                                            "Specific Property Lookup",
                                                            id="right_collapse_button",
                                                            className="mb-3",
                                                            color="primary",
                                                        ),
                                                        dbc.Collapse(
                                                            dbc.Card(
                                                                dbc.CardBody("This content is hidden in the collapse")),
                                                            id="right_collapse",
                                                        ),
                                                    ]
                                                ),



                                                # table
                                                dcc.Graph(
                                                    id='right_on_market_table',
                                                    className="graph",

                                                ),

                                                # Rent History
                                                html.H4("Properties Renting History at"),
                                                html.H5(id = "right_history_title"),
                                                html.Hr(),



                                                # hist_trend_graph
                                                dcc.Graph(
                                                id='right_hist_trend_graph',
                                                    className= "graph",


                                                ),

                                                # increase and decease
                                                dcc.Graph(
                                                    id='right_price_change_table',
                                                    className="graph",

                                                ),

                                                      ],
                                            width={"size": 6, "order": "last"},
                                            className = "my_column",


                                        ),

                                    ],
                                    justify = "center",

                                ),




                                ], className = "app__container"),

                    ])

# ----------- left Callbacks ---------------------------
@app.callback(
    Output("left_on_market_graph", "figure"),
    Output("left_on_market_table", "figure"),
    Input("left_on_market_title", "children"),
)
def left_update_on_market(address):
    if (address is None) or (address == ""):
        return px.bar(),px.bar()
    #return px.bar(),px.bar() # TOBE comment out
    return get_on_market_plots(address)



# this will also check and store the address
@app.callback(
    Output("left_on_market_title", "children"),
    Output("left_history_title", "children"),
    Output("left_wrong_address_toast", "is_open"),
    Input("left_search", "n_clicks"),
    Input("left_street_address", 'value'),
    Input("left_postcode", "value"),
    Input("left_suburb_name", "value")

)
def left_update_titles(n_clicks,street_address, postcode,suburb_name):
    ctx = dash.callback_context

    if not ctx.triggered:
        ele_id = 'No clicks yet'
    else:
        ele_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # if not button is clicked
    if not ele_id == "left_search":
        return "", "", False

    address = search_check(street_address, suburb_name, postcode)
    if address is None:
        return "", "", True
    return  address,  address, False


@app.callback(
    Output("left_hist_trend_graph", "figure"),
    Output("left_price_change_table", "figure"),
    Input("left_on_market_title", "children"),
)
def left_update_hist_trend(address):
    if (address is None) or (address == ""):
        return px.bar(), px.bar()
    df = get_property_rent_history(address)
    return get_hist_trend_plot(df),get_percentage_price_change_table(df, "room_type_2", "price")

@app.callback(
    Output("left_collapse", "is_open"),
    [Input("left_collapse_button", "n_clicks")],
    [State("left_collapse", "is_open")],
)
def left_toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("left_search", "disabled"),
    Input("left_street_address", 'value'),
    Input("left_postcode", "value"),
    Input("left_suburb_name", "value")
)
def left_set_search_available(street, postcode, city):
    if street.strip() == "" or postcode.strip() == "" or city.strip() == "":
        return True
    return False



@app.callback(
    Output('specific_property_hist', 'figure'),
    Output('specific_property_hist', 'style'),
    Output('no_hist_text', 'style'),
    Output('hist_instruction_text', 'style'),
    Input('left_on_market_graph', 'clickData'),
    Input("left_on_market_title", "children"))
def display_click_data(clickData, address):
    if clickData is None:
        return px.bar(), {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    #plot_figure  = timeline_plot("3201",'27-therry-street-melbourne-vic-3000', 620, 11,'14955899')
    data_dict = clickData["points"][0]
    print(json.dumps(clickData, indent=2))
    plot_figure = timeline_plot(data_dict["customdata"][0], address, data_dict["y"], data_dict["customdata"][2],
                  "agency_placeholder")
    if plot_figure is None:
        return px.bar(), {'display': 'none'}, {'display': 'block'},{'display': 'none'}
    else:
        return plot_figure, {'display': 'block'}, {'display': 'none'},{'display': 'none'}



# ----------- right Callbacks ---------------------------
@app.callback(
    Output("right_on_market_graph", "figure"),
    Output("right_on_market_table", "figure"),
    Input("address2", "value"),
)
def right_update_on_market(address):
    if (address is None) or (address == ""):
        return px.bar(),px.bar()
    #return px.bar(),px.bar() # TOBE comment out
    return get_on_market_plots(address)



@app.callback(
    Output("right_on_market_title", "children"),
    Output("right_history_title", "children"),
    Input("address2", "value")

)
def right_update_titles(address):
    return  address,  address


@app.callback(
    Output("right_hist_trend_graph", "figure"),
    Output("right_price_change_table", "figure"),
    Input("address2", "value"),
)
def right_update_hist_trend(address):
    if (address is None) or (address == ""):
        return px.bar(), px.bar()
    df = get_property_rent_history(address)
    return get_hist_trend_plot(df),get_percentage_price_change_table(df, "room_type_2", "price")

@app.callback(
    Output("right_collapse", "is_open"),
    [Input("right_collapse_button", "n_clicks")],
    [State("right_collapse", "is_open")],
)
def right_toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



if __name__ == '__main__':
    app.run_server(debug=True)