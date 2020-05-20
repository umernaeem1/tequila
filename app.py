import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
import json
import pandas as pd
import requests
import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import quote

df = pd.read_csv('./Data/ref_data.csv', encoding='latin1')
df_c = df.groupby(['municipal_code', 'year', 'crime_type']
                  )['total_crime'].sum().reset_index()
df_t = df_c.groupby(['municipal_code', 'year'])['total_crime'].sum().reset_index().rename(
    columns={'total_crime': 'total_crime_m'})
df_c = df_c.merge(df_t, on=['municipal_code', 'year'])
df_c['muni_code_str'] = df_c['municipal_code'].apply(str)

with open('./Data/mexico_correct.json') as f:
    geojsdata = json.load(f)

mapbox_access_token = "pk.eyJ1IjoidW1lcjI0NDM0IiwiYSI6ImNrOXkybGl3NTBrczAzZnAzbWs1bWx1YzkifQ.RoXKkWYd5XIU3WOp-qlWyA"

# API Requests for news div


def news_get(query):
    '''
    Getting news from google news page
    '''

    url = urlopen(
        'https://news.google.com/rss/search?q={0}&hl=en-PK&gl=PK&ceid=PK:en'.format(quote(query)))
    xml_page = url.read()
    url.close()
    soup = BeautifulSoup(xml_page, "xml")
    headline, date, url, source, source_web = [], [], [], [], []
    for i in soup.find_all('item'):
        headline.append(i.title.text)
        date.append(i.pubDate.text)
        url.append(i.link.text)
        source.append(i.source.text)
        source_web.append(i.source.attrs['url'])

    df = pd.DataFrame({'title': headline, 'date': date, 'url': url,
                       'news_source': source, 'news_source_web': source_web}).iloc[1:]
    return df

# API Call to update news


def update_news():
    news = news_get('amatitan crime')
    news = pd.DataFrame(news[["title", "url"]])
    max_rows = 10
    return html.Div(
        children=[
            html.P(className="p-news", children="Headlines"),
            html.P(
                className="p-news float-right",
                children="Last update : "
                + datetime.datetime.now().strftime("%H:%M:%S"),
            ),
            html.Table(
                className="table-news",
                children=[
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    html.A(
                                        className="td-link",
                                        children=news.iloc[i]["title"],
                                        href=news.iloc[i]["url"],
                                        target="_blank",
                                    )
                                ]
                            )
                        ]
                    )
                    for i in range(min(len(news), max_rows))
                ],
            ),
        ]
    )


# Making the map
pop = df.drop_duplicates(['municipal_code'])[
    ['municipal_code', 'municipal_name', 'geo-id', 'population']]

trace = go.Choroplethmapbox(z=pop['population'],
                            locations=pop['geo-id'],
                            colorbar=dict(thickness=20, ticklen=3),
                            geojson=geojsdata,
                            text=pop['municipal_name'],
                            hovertemplate='<b>Municipality</b>: <b>%{text}</b>' +
                            '<br> <b>Val </b>: %{z}<br>',
                            marker_line_width=0.1, marker_opacity=0.7)

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Mexico municipality population choropleth",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lat=20.7922, lon=-104.1953),
        zoom=5.5,
    ),
)

fig = dict(data=[trace], layout=layout)

external_stylesheets = ['assets/stylesheet.css']

# Options for dropdown
# Crime
key = ['C' + str(i) for i in range(1, 41)]
value = sorted(list(df.crime_type.value_counts().index))
crime_d = dict(zip(key, value))

crime_type_options = [
    {"label": str(crime_d[i]), "value": str(i)}
    for i in crime_d
]

temp = pd.DataFrame(crime_d.items(), columns=('crime_code', 'crime_type'))
df_c = df_c.merge(temp, on='crime_type')

# Municipality
key = list(df.drop_duplicates(['municipal_code'])['municipal_code'])
value = list(df.drop_duplicates(['municipal_code'])['municipal_name'])
municipal_d = dict(zip(key, value))

municipal_options = [
    {"label": str(municipal_d[i]), "value": str(i)}
    for i in municipal_d
]

#################################


def filtered_data(df, muni, crime):
    dff = df[
        (df['muni_code_str'] == str(muni))
        & (df['crime_code'].isin(crime))
    ]

    return dff

#################################
external_stylesheets = ['https://codepen.io/umernaeem1/pen/XWmoxbw']

<<<<<<< HEAD
app = dash.Dash('__main__', external_stylesheets = external_stylesheets)
=======

app = dash.Dash('__main__', external_stylesheets=external_stylesheets)

server = app.server
>>>>>>> fbe4a68fe674871eeffaafc69c1df33624753d63

app.layout = html.Div(children=[

    html.Div([
        # First row
        html.H3('Project Tequila')
    ], className='row', id='title'
    ),
    html.Div([                                                                                                  # this is going to be one row

        html.Div([
            html.Div(children=[
                html.Div(children=[
                    html.Div([
                        html.P('Select Crime Type'),
                        dcc.Dropdown(
                            id='crime_type',
                            options=crime_type_options,
                            value=['C19', 'C14', 'C32'],
                            multi=True,
                            className="dcc_control",
                        )
                    ], className='six columns'
                    ),
                    html.Div([
                        html.P('Select Municipality'),
                        dcc.Dropdown(
                            id='muni_type',
                            options=municipal_options,
                            value='14005',
                            # multi=True,
                            className="dcc_control"
                        ),
                    ], className='six columns'
                    )
                ], className='row pretty_container'
                ),

                html.Div([
                    html.H5('Crime by municipality'),
                    dcc.Graph(id='muni_output_fig')
                ], style={'text-align': 'center'}, className='pretty_container'
                )
            ], className='row', style={'maxHeight': '83ex',
                                       #'overflowY': 'scroll',
                                       'width': '100%',
                                       'minWidth': '100%',
                                       'padding-left': '3px'}
            ),

            html.Div([
                html.Div(children=[
                    dcc.Graph(
                        id='mapa',
                        figure=fig
                    )
                ]
                )
            ], className='row pretty_container'
            )
        ], className='nine columns'
        ),

        html.Div([                                                                                                 # for news
            html.Div(children=update_news())
        ], className='three columns pretty_container'
        )
    ], className='row'
    )
], className='container'
)


@app.callback(
    Output('muni_output_fig', 'figure'),
    [Input('muni_type', 'value'),
     Input('crime_type', 'value')])
def update_fig(selected_muni, crime_type):
    dff = filtered_data(df_c, selected_muni, crime_type)

    trace = go.Bar(
        x=dff['year'],
        y=dff['total_crime'],
        text=dff['total_crime'],
        textposition='outside',
        marker_color='lightblue'
    )

    return {
        'data': [trace],
        'layout': dict(
            yaxis={'title': 'number of crimes'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            transition={'duration': 500}
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
