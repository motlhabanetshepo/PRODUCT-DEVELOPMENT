import pandas as pd
import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import random
import numpy as np
from faker import Faker
from dash.dependencies import Input, Output, State
from io import StringIO
import base64

# Set random seeds for reproducibility
fake = Faker()
np.random.seed(42)
random.seed(42)

# Generate sample dataset
num_rows = 500500
start_date = pd.to_datetime('2022-05-01')
end_date = pd.to_datetime('2025-03-31')
date_range = pd.date_range(start=start_date, end=end_date).tolist()

countries = ['South Africa', 'Botswana', 'Namibia', 'Zambia', 'Libya', 'Malawi', 'Cameroon', 'Niger', 'Sudan', 'Togo',
             'Democratic Republic of Congo', 'Kenya', 'Algeria', 'Ethiopia', 'Morocco', 'Senegal', 'Rwanda', 'Tunisia',
             'Zimbabwe', 'Mozambique', 'Lesotho', 'Swaziland', 'Angola', 'Egypt', 'Ghana', 'Nigeria']
job_titles = ['Software Engineer', 'Data Scientist', 'IT Support Specialist', 'Network Engineer', 'Systems Analyst',
              'DevOps Engineer', 'Cybersecurity Analyst', 'Cloud Engineer', 'Database Administrator', 'AI/ML Engineer',
              'Web Developer', 'Mobile App Developer', 'IT Project Manager', 'Computer Engineer', 'Embedded Systems Engineer']
products = ['Antivirus Software', 'Cloud Storage Subscription', 'DevOps Platform', 'Project Management Tool',
            'AI/ML Toolkit', 'Data Visualization Software', 'CRM Software', 'ERP System', 'Cybersecurity Suite',
            'Database Management System', 'API Integration Tool', 'Code Repository Hosting', 'Virtual Machine Instance',
            'Container Orchestration Service', 'Cloud IDE']
regions = ['North Africa', 'East Africa', 'Central Africa', 'West Africa', 'Southern Africa']
promo_events = ['Discount', 'Flash Sale', 'Buy1Get1', 'None']
salespersons = ['John Doe', 'Jane Smith', 'Alex Brown', 'Emily Davis', 'Michael Chen', 'Sarah Lee', 'David Kim', 'Laura Wilson', 'Chris Taylor', 'Anna Patel']
marketing_channels = ['LinkedIn', 'Facebook', 'Twitter', 'Email', 'Direct']

seen = set()
data = []
conversion_rate_target = 0.05  # 5% conversion rate
data_gen_start_date = pd.to_datetime('2022-05-01')
base_target = 10000  # Monthly sales target per salesperson ($10,000)
while len(data) < num_rows:
    date = random.choice(date_range)
    country = random.choice(countries)
    job_title = random.choice(job_titles)
    product = random.choice(products)
    region = regions[countries.index(country) % len(regions)]
    salesperson = random.choice(salespersons)
    channel = random.choice(marketing_channels)
    unit_price = round(random.uniform(20, 200), 2)
    quantity = random.randint(1, 5)
    days_since_start = (date - data_gen_start_date).days
    growth_factor = 1 + 0.000274 * days_since_start  # ~10% annual growth
    sales = (unit_price * quantity * growth_factor) if random.random() < conversion_rate_target else 0
    user_engagement = random.randint(1, 10)
    promo_event = random.choice(promo_events)
    # Calculate monthly target (10% annual increase)
    months_since_start = days_since_start // 30
    monthly_target = base_target * (1 + 0.00833 * months_since_start)  # ~10% annual (0.833% monthly)
    combo = (country, product, job_title, promo_event, date.date(), salesperson, channel)
    if combo not in seen:
        seen.add(combo)
        converted = 1 if sales > 0 else 0
        data.append([date, country, region, product, job_title, sales, user_engagement, promo_event, converted, salesperson, channel, monthly_target, unit_price])

df = pd.DataFrame(data, columns=['date', 'country', 'region', 'product', 'job_title', 'sales', 'user_engagement', 'promo_event', 'converted', 'salesperson', 'marketing_channel', 'sales_target', 'unit_price'])
df.to_csv('weblog.csv', index=False)

# Load data
df = pd.read_csv("weblog.csv", parse_dates=['date'])

# Calculate cost and profit_margin per row
df['cost'] = df['sales'] * np.random.uniform(0.5, 0.7, size=len(df))
df['profit_margin'] = ((df['sales'] - df['cost']) / df['sales'] * 100).round(2).fillna(0)

# Simulate missing columns
df['age_group'] = np.random.choice(['18-25', '26-35', '36-45', '46+'], size=len(df))
df['session_duration'] = np.random.uniform(30, 300, size=len(df))
df['job_status'] = np.random.choice(['Pending', 'In Progress', 'Completed'], size=len(df))
df['job_priority'] = np.random.choice(['Low', 'Medium', 'High'], size=len(df))
df['log_type'] = np.random.choice(['Info', 'Error', 'Warning'], size=len(df))
df['month'] = df['date'].dt.to_period('M').astype(str)
df['quantity'] = (df['sales'] / df['unit_price']).where(df['sales'] > 0, 0).round().clip(1, 5)

# Create details column for Logs Tab
df['details'] = df['job_title'] + ' - ' + df['log_type'] + ' - ' + df['salesperson']

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[
    'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
    '/assets/styles.css'
])
app.title = "AI-Solutions Sales Dashboard"

# KPIs
total_sales = df['sales'].sum()
total_users = len(df)
conversion_rate = (df['converted'].sum() / total_users * 100) if total_users > 0 else 0
sales_by_product = df.groupby('product')['sales'].sum().reset_index()
top_product = sales_by_product.loc[sales_by_product['sales'].idxmax(), 'product'] if not sales_by_product.empty else "N/A"
low_product = sales_by_product.loc[sales_by_product['sales'].idxmin(), 'product'] if not sales_by_product.empty else "N/A"
avg_profit_margin = df['profit_margin'].mean().round(2)

# Placeholder data for promotion_data
promotion_data = [
    {'promo_event': e, 'start_date': '2022-05-01', 'end_date': '2025-03-31', 'target': 'All', 'redemption_rate': random.uniform(0.1, 0.5)}
    for e in promo_events
]

# Layout
app.layout = html.Div([
    html.H1("AI-Solutions Sales Dashboard", className="text-xl font-bold text-center text-blue-800 mb-2"),
    # Global Filters
    html.Div([
        html.Label("Select Date Range:", className="text-sm font-semibold text-gray-700 mr-2"),
        dcc.DatePickerRange(
            id='date-picker',
            min_date_allowed=df['date'].min(),
            max_date_allowed=df['date'].max(),
            start_date=df['date'].min(),
            end_date=df['date'].max(),
            display_format='YYYY-MM-DD',
            className="border rounded p-1 text-sm"
        ),
        html.Label("Select Region:", className="text-sm font-semibold text-gray-700 ml-2 mr-2"),
        dcc.Dropdown(
            id='region-filter',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': r, 'value': r} for r in df['region'].unique()],
            value='All',
            className="w-40 border rounded p-1 text-sm"
        ),
        html.Label("Select Salesperson:", className="text-sm font-semibold text-gray-700 ml-2 mr-2"),
        dcc.Dropdown(
            id='salesperson-filter',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': s, 'value': s} for s in df['salesperson'].unique()],
            value='All',
            className="w-40 border rounded p-1 text-sm"
        ),
        html.Label("Select Marketing Channel:", className="text-sm font-semibold text-gray-700 ml-2 mr-2"),
        dcc.Dropdown(
            id='channel-filter',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': c, 'value': c} for c in df['marketing_channel'].unique()],
            value='All',
            className="w-40 border rounded p-1 text-sm"
        ),
    ], className="flex items-center justify-center gap-2 mb-2 flex-wrap bg-gray-100 p-2 rounded-lg shadow"),

    # Tabs
    dcc.Tabs(id='tabs', className="custom-tabs", children=[
        # Overview Tab
        dcc.Tab(label="Overview", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div([
                html.Div([
                    html.H3("Total Sales vs Target", className="text-sm font-semibold text-gray-700"),
                    dcc.Graph(id='kpi-sales-gauge', className="h-32")
                ], className="kpi-card"),
                html.Div([
                    html.H3("Conversion Rate", className="text-sm font-semibold text-gray-700"),
                    dcc.Graph(id='kpi-conversion-gauge', className="h-32")
                ], className="kpi-card"),
                html.Div([
                    html.H3("Sales Growth", className="text-sm font-semibold text-gray-700"),
                    dcc.Graph(id='kpi-growth-gauge', className="h-32")
                ], className="kpi-card"),
                html.Div([
                    html.H3("Team Performance", className="text-sm font-semibold text-gray-700"),
                    html.P(id='team-status', className="text-base font-bold")
                ], className="kpi-card"),
            ], className="grid grid-cols-1 md:grid-cols-4 gap-2 mb-2"),
                html.Div([
                    html.H3("Total Sales Revenue", className="text-sm font-semibold text-gray-700"),
                    html.P(id='total-sales', className="text-base font-bold text-blue-600")
            ], className="kpi-card"),
            html.Div([
            dcc.Graph(id='sales-trend', className="graph-card", style={'transform': 'scale(0.8)', 'transformOrigin': 'center'}),
            dcc.Graph(id='region-pie', className="graph-card", style={'transform': 'scale(0.8)', 'transformOrigin': 'center'})
        ], className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-2"),
    ]),

        # Products Tab
        dcc.Tab(label="Products", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div([
                html.H3("Select Product", className="text-sm font-semibold text-gray-700"),
                dcc.Dropdown(
                    id='product-dropdown',
                    options=[{'label': product, 'value': product} for product in products],
                    value=products[0],
                    className="w-1/3 mx-auto border rounded p-1 text-sm"
                )
            ], className="text-center mb-2"),
            html.Div([
                html.Div([
                    html.H3("Top-Selling Product", className="text-sm font-semibold text-gray-700"),
                    html.P(id='top-product', className="text-base font-bold text-green-600")
                ], className="product-kpi-card"),
                html.Div([
                    html.H3("Low-Performing Product", className="text-sm font-semibold text-gray-700"),
                    html.P(id='low-product', className="text-base font-bold text-red-600")
                ], className="product-kpi-card"),
                html.Div([
                    html.H3("Average Profit Margin", className="text-sm font-semibold text-gray-700"),
                    html.P(id='profit-margin', className="text-base font-bold text-yellow-600")
                ], className="product-kpi-card"),
            ], className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-2"),
            html.Div([
                dcc.Graph(id='product-sales-chart', className="product-graph-card")
            ], className="grid grid-cols-1 gap-2 mb-2"),
        ]),

        # Regions Tab
        dcc.Tab(label="Regions", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.H2("Sales Distribution by Region", className="text-base font-bold text-blue-800 mb-2"),
            html.Div([
                dcc.Graph(id='choropleth-map', className="graph-card"),
                dcc.Graph(id='region-bar', className="graph-card"),
                dcc.Graph(id='age-dist', className="graph-card")
            ], className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-2"),
        ]),

        # User Engagement Tab
        dcc.Tab(label="User Engagement", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div([
                html.Label("Segment By:", className="text-sm font-semibold text-gray-700 mr-2"),
                dcc.Dropdown(
                    id='engagement-segment',
                    options=[
                        {'label': 'All', 'value': 'All'},
                        {'label': 'Age Group', 'value': 'age_group'},
                        {'label': 'Region', 'value': 'region'},
                        {'label': 'Salesperson', 'value': 'salesperson'}
                    ],
                    value='All',
                    className="w-40 border rounded p-1 text-sm"
                )
            ], className="mb-2"),
            html.Div([
                html.Div([
                    html.H3("Daily Active Users", className="text-sm font-semibold text-gray-700"),
                    html.P(id='dau', className="text-base font-bold text-green-600")
                ], className="kpi-card"),
                html.Div([
                    html.H3("Avg Session Duration", className="text-sm font-semibold text-gray-700"),
                    html.P(id='session-duration', className="text-base font-bold text-blue-600")
                ], className="kpi-card"),
                html.Div([
                    html.H3("Retention Rate", className="text-sm font-semibold text-gray-700"),
                    html.P(id='retention', className="text-base font-bold text-red-600")
                ], className="kpi-card"),
            ], className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-2"),
            html.Div([
                dcc.Graph(id='engagement-trend', className="graph-card"),
                dcc.Graph(id='engagement-funnel', className="graph-card"),
                dcc.Graph(id='cohort-analysis', className="graph-card")
            ], className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-2"),
        ]),

        # Promotions Tab
        dcc.Tab(label="Promotions", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div([
                dcc.Graph(id='promo-performance', className="graph-card"),
                dcc.Graph(id='promo-correlation', className="graph-card")
            ], className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-2"),
            html.Div([
                html.Div([
                    html.H3("Total Redemptions", className="text-sm font-semibold text-gray-700"),
                    html.P(id='promo-redemptions', className="text-base font-bold text-green-600")
                ], className="kpi-card"),
                html.Div([
                    html.H3("Average ROI", className="text-sm font-semibold text-gray-700"),
                    html.P(id='promo-roi', className="text-base font-bold text-blue-600")
                ], className="kpi-card"),
            ], className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-2"),
            html.H2("Manage Promotions", className="text-base font-bold text-blue-800 mb-2"),
            html.Div([
                html.Label("Promotion Name:", className="text-sm font-semibold text-gray-700 mr-2"),
                dcc.Input(id='input-promo', type='text', placeholder='Enter promo name', className="w-32 border rounded p-1 text-sm"),
                html.Label("Start Date:", className="text-sm font-semibold text-gray-700 ml-2 mr-2"),
                dcc.DatePickerSingle(id='promo-start', display_format='YYYY-MM-DD', className="border rounded p-1 text-sm"),
                html.Label("End Date:", className="text-sm font-semibold text-gray-700 ml-2 mr-2"),
                dcc.DatePickerSingle(id='promo-end', display_format='YYYY-MM-DD', className="border rounded p-1 text-sm"),
                html.Label("Target:", className="text-sm font-semibold text-gray-700 ml-2 mr-2"),
                dcc.Dropdown(
                    id='input-target',
                    options=[{'label': t, 'value': t} for t in ['All', 'New Users', 'Enterprise']],
                    placeholder='Select target',
                    className="w-32 border rounded p-1 text-sm"
                ),
                html.Label("Channel:", className="text-sm font-semibold text-gray-700 ml-2 mr-2"),
                dcc.Dropdown(
                    id='input-channel',
                    options=[{'label': c, 'value': c} for c in marketing_channels],
                    placeholder='Select channel',
                    className="w-32 border rounded p-1 text-sm"
                ),
                html.Button('Add Promotion', id='add-promo-button', n_clicks=0, className="ml-2 bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700 text-sm"),
                html.Div(id='promo-form-output', className="mt-2 text-green-600 text-sm")
            ], className="flex items-center justify-center gap-2 flex-wrap mb-2"),
        ]),

        # Logs Tab
        dcc.Tab(label="Logs", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.H2("System Logs", className="text-base font-bold text-blue-800", style={'margin': '20px'}),
            dash_table.DataTable(
                id='log-table',
                columns=[
                    {"name": "Timestamp", "id": "date"},
                    {"name": "Country", "id": "country"},
                    {"name": "Salesperson", "id": "salesperson"},
                    {"name": "Channel", "id": "marketing_channel"},
                    {"name": "Details", "id": "details"}
                ],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                page_size=5,
                sort_action='native',
                filter_action='native'
            ),
        ]),

        # Salesperson Tab
        dcc.Tab(label="Salesperson", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.H2("Individual and Team Performance", className="text-base font-bold text-blue-800 mb-2"),
            html.Div([
                html.Div([
                    html.H3("Top Performer", className="text-sm font-semibold text-gray-700"),
                    html.P(id='top-salesperson', className="text-base font-bold text-green-600")
                ], className="kpi-card"),
                html.Div([
                    html.H3("Underperformer", className="text-sm font-semibold text-gray-700"),
                    html.P(id='low-salesperson', className="text-base font-bold text-red-600")
                ], className="kpi-card"),
            ], className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-2"),
            html.Div([
                dcc.Graph(id='salesperson-bar', className="graph-card"),
                dcc.Graph(id='salesperson-trend', className="graph-card")
            ], className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-2"),
        ]),
    ])
], className="dashboard-container")

# Callbacks
@app.callback(
    [
        Output('kpi-sales-gauge', 'figure'),
        Output('kpi-conversion-gauge', 'figure'),
        Output('kpi-growth-gauge', 'figure'),
        Output('team-status', 'children'),
        Output('total-sales', 'children'),
        Output('sales-trend', 'figure'),
        Output('region-pie', 'figure')
    ],
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('region-filter', 'value'),
        Input('salesperson-filter', 'value'),
        Input('channel-filter', 'value')
    ]
)
def update_overview(start_date, end_date, region, salesperson, channel):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == region]
    if salesperson != 'All':
        filtered_df = filtered_df[filtered_df['salesperson'] == salesperson]
    if channel != 'All':
        filtered_df = filtered_df[filtered_df['marketing_channel'] == channel]

    sales = filtered_df['sales'].sum()
    target = filtered_df['sales_target'].sum()
    users = len(filtered_df)
    conv_rate = (filtered_df['converted'].sum() / users * 100) if users > 0 else 0
    filtered_df['year'] = filtered_df['date'].dt.year
    sales_by_year = filtered_df.groupby('year')['sales'].sum().reset_index()
    for year in sales_by_year['year']:
        year_data = filtered_df[filtered_df['date'].dt.year == year]
        days_in_year = 365 if year != 2025 else (pd.to_datetime(f'{year}-03-31') - pd.to_datetime(f'{year}-01-01')).days + 1
        fraction_of_year = len(year_data['date'].dt.date.unique()) / days_in_year
        if fraction_of_year > 0:
            sales_by_year.loc[sales_by_year['year'] == year, 'sales'] /= fraction_of_year
    growth = ((sales_by_year['sales'].pct_change() * 100).iloc[-1] if len(sales_by_year) > 1 else 0)
    growth = max(5, min(100, growth))

    # Gauge for Sales
    sales_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sales,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Sales ($)", 'font': {'size': 10}},
        gauge={
            'axis': {'range': [0, max(target * 1.2, sales * 1.2)]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, target * 0.8], 'color': "red"},
                {'range': [target * 0.8, target], 'color': "yellow"},
                {'range': [target, target * 1.2], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': target
            }
        }
    ))
    sales_gauge.update_layout(margin=dict(l=10, r=10, t=20, b=10), font=dict(size=8))

    # Gauge for Conversion Rate
    conv_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=conv_rate,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Conversion Rate (%)", 'font': {'size': 10}},
        gauge={
            'axis': {'range': [0, 10]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 3], 'color': "red"},
                {'range': [3, 5], 'color': "yellow"},
                {'range': [5, 10], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': 5 
            }
        }
    ))
    conv_gauge.update_layout(margin=dict(l=10, r=10, t=20, b=10), font=dict(size=8))

    # Gauge for Growth
    growth_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=growth,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Sales Growth (%)", 'font': {'size': 10}},
        gauge={
            'axis': {'range': [0, 20]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 5], 'color': "red"},
                {'range': [5, 10], 'color': "yellow"},
                {'range': [10, 20], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': 10  
            }
        }
    ))
    growth_gauge.update_layout(margin=dict(l=10, r=10, t=20, b=10), font=dict(size=8))

    # Team Status
    sales_performance = sales / target * 100 if target > 0 else 0
    team_status = (
        "Green: On Track" if sales_performance >= 100 else
        "Yellow: At Risk" if sales_performance >= 60 else
        "Underperforming"
    )
    team_color = (
        "text-green-600" if sales_performance >= 100 else
        "text-yellow-600" if sales_performance >= 80 else
        "text-red-600"
    )

    total_sales_display = f"${sales:,.2f}"

    sales_trend_data = filtered_df.groupby('date')['sales'].sum().reset_index()
    sales_fig = px.line(sales_trend_data, x='date', y='sales', title="Sales Trend Over Time")
    sales_fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(size=8),
        title_font_size=10
    )

    region_data = filtered_df.groupby('region')['sales'].sum().reset_index()
    pie_fig = px.pie(region_data, names='region', values='sales', title="Sales by Region")
    pie_fig.update_traces(textinfo='percent+label', textfont_size=8)
    pie_fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(size=8),
        title_font_size=10
    )


    return (
        sales_gauge,
        conv_gauge,
        growth_gauge,
        html.P(team_status, className=f"text-base font-bold {team_color}"),
        total_sales_display,
        sales_fig,
        pie_fig
    )

@app.callback(
    [
        Output('top-product', 'children'),
        Output('low-product', 'children'),
        Output('profit-margin', 'children'),
        Output('product-sales-chart', 'figure')
    ],
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('region-filter', 'value'),
        Input('salesperson-filter', 'value'),
        Input('channel-filter', 'value'),
        Input('product-dropdown', 'value')
    ]
)
def update_products(start_date, end_date, region, salesperson, channel, selected_product):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == region]
    if salesperson != 'All':
        filtered_df = filtered_df[filtered_df['salesperson'] == salesperson]
    if channel != 'All':
        filtered_df = filtered_df[filtered_df['marketing_channel'] == channel]

    sales_by_product = filtered_df.groupby('product').agg({'sales': 'sum', 'sales_target': 'sum'}).reset_index()
    sales_by_product['performance'] = sales_by_product['sales'] / sales_by_product['sales_target'] * 100
    top_product = sales_by_product.loc[sales_by_product['sales'].idxmax(), 'product'] if not sales_by_product.empty else "N/A"
    low_product = sales_by_product.loc[sales_by_product['sales'].idxmin(), 'product'] if not sales_by_product.empty else "N/A"
    avg_profit_margin = filtered_df['profit_margin'].mean().round(2) if not filtered_df.empty else 0

    sales_fig = px.bar(
        sales_by_product,
        x='product',
        y='sales',
        title="Sales by Product",
        color='product', 
        color_discrete_sequence=px.colors.qualitative.Plotly  
    )
    sales_fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(size=8),
        title_font_size=10,
        xaxis_title="Product",
        yaxis_title="sales",
        xaxis_tickangle=45,  
        showlegend=False  
    )

    return (
        top_product,
        low_product,
        f"{avg_profit_margin:.2f}%",
        sales_fig
    )

@app.callback(
    [
        Output('choropleth-map', 'figure'),
        Output('region-bar', 'figure'),
        Output('age-dist', 'figure')
    ],
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('region-filter', 'value'),
        Input('salesperson-filter', 'value'),
        Input('channel-filter', 'value')
    ]
)
def update_regions(start_date, end_date, region, salesperson, channel):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == region]
    if salesperson != 'All':
        filtered_df = filtered_df[filtered_df['salesperson'] == salesperson]
    if channel != 'All':
        filtered_df = filtered_df[filtered_df['marketing_channel'] == channel]

    choropleth_fig = px.choropleth(
        filtered_df.groupby('country')['sales'].sum().reset_index(),
        locations='country', locationmode='country names', color='sales',
        title='Sales by Country', color_continuous_scale='Viridis'
    )
    choropleth_fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(size=8),
        title_font_size=10
    )

    region_kpis = filtered_df.groupby('region').agg({'sales': 'sum'}).reset_index()
    region_bar_fig = px.bar(region_kpis, x='region', y='sales', title="Sales Comparison by Region")
    region_bar_fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(size=8),
        title_font_size=10
    )

    age_dist_fig = px.histogram(filtered_df, x='age_group', y='sales', color='region', title="Sales by Age Group and Region", barmode='group')
    age_dist_fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), font=dict(size=8), title_font_size=10)

    return (
        choropleth_fig,
        region_bar_fig,
        age_dist_fig
    )

@app.callback(
    [
        Output('dau', 'children'),
        Output('session-duration', 'children'),
        Output('retention', 'children'),
        Output('engagement-trend', 'figure'),
        Output('engagement-funnel', 'figure'),
        Output('cohort-analysis', 'figure')
    ],
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('region-filter', 'value'),
        Input('salesperson-filter', 'value'),
        Input('channel-filter', 'value'),
        Input('engagement-segment', 'value')
    ]
)
def update_engagement(start_date, end_date, region, salesperson, channel, segment):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == region]
    if salesperson != 'All':
        filtered_df = filtered_df[filtered_df['salesperson'] == salesperson]
    if channel != 'All':
        filtered_df = filtered_df[filtered_df['marketing_channel'] == channel]

    if segment != 'All':
        filtered_df = filtered_df.groupby([segment, 'date']).sum().reset_index()

    dau = filtered_df.groupby('date')['user_engagement'].count().mean()
    session_duration = filtered_df['session_duration'].mean()
    retention = (filtered_df['user_engagement'] > 5).mean() * 100  # Adjusted threshold

    trend_fig = px.line(
        filtered_df.groupby('date')['user_engagement'].sum().reset_index(),
        x='date',
        y='user_engagement',
        title="User Engagement Over Time"
    )
    trend_fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), font=dict(size=8), title_font_size=10)

    funnel_fig = px.funnel(
        filtered_df.groupby('job_title')['user_engagement'].sum().nlargest(5).reset_index(),
        x='user_engagement',
        y='job_title',
        title="Top 5 Job Titles by Engagement"
    )
    funnel_fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), font=dict(size=8), title_font_size=10)

    cohort_fig = px.density_heatmap(
        filtered_df.groupby(['month', 'region'])['user_engagement'].sum().reset_index(),
        x='month',
        y='region',
        z='user_engagement',
        title="Cohort Analysis by Region"
    )
    cohort_fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), font=dict(size=8), title_font_size=10)

    return (
        f"{int(dau)}",
        f"{session_duration:.2f} sec",
        f"{retention:.2f}%",
        trend_fig,
        funnel_fig,
        cohort_fig
    )

@app.callback(
    [
        Output('promo-redemptions', 'children'),
        Output('promo-roi', 'children'),
        Output('promo-performance', 'figure'),
        Output('promo-correlation', 'figure'),
        Output('promo-form-output', 'children')
    ],
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('region-filter', 'value'),
        Input('salesperson-filter', 'value'),
        Input('channel-filter', 'value'),
        Input('add-promo-button', 'n_clicks')
    ],
    [
        State('input-promo', 'value'),
        State('promo-start', 'date'),
        State('promo-end', 'date'),
        State('input-target', 'value'),
        State('input-channel', 'value')
    ]
)
def update_promotions(start_date, end_date, region, salesperson, channel, add_clicks, input_promo, promo_start, promo_end, input_target, input_channel):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == region]
    if salesperson != 'All':
        filtered_df = filtered_df[filtered_df['salesperson'] == salesperson]
    if channel != 'All':
        filtered_df = filtered_df[filtered_df['marketing_channel'] == channel]

    global promotion_data
    redemptions = filtered_df.groupby('promo_event')['quantity'].sum().sum()
    roi = filtered_df[filtered_df['promo_event'] != 'None']['sales'].mean() / filtered_df['sales'].mean() * 100 if filtered_df['sales'].mean() > 0 else 0

    performance_fig = px.line(
        filtered_df.groupby(['date', 'promo_event'])['sales'].sum().reset_index(),
        x='date',
        y='sales',
        color='promo_event',
        title="Sales by Promotion"
    )
    performance_fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), font=dict(size=8), title_font_size=10)

    # Box plot for correlation analysis between sales and promotional events
    correlation_fig = px.box(
        filtered_df[filtered_df['sales'] > 0],
        x='promo_event',
        y='sales',
        color='promo_event',
        title="Sales Distribution by Promotional Event",
        points="outliers"
    )
    correlation_fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(size=8),
        title_font_size=10,
        showlegend=False,
        xaxis_title="Promotional Event",
        yaxis_title="Sales ($)"
    )
    form_message = ""
    if add_clicks > 0 and input_promo and promo_start and promo_end and input_target and input_channel:
        if input_promo not in [p['promo_event'] for p in promotion_data]:
            promotion_data.append({
                'promo_event': input_promo,
                'start_date': promo_start,
                'end_date': promo_end,
                'target': input_target,
                'redemption_rate': random.uniform(0.1, 0.5),
                'channel': input_channel
            })
            form_message = f"Added promotion: {input_promo} for {input_channel}"
        else:
            form_message = "Promotion already exists!"

    return (
        f"{int(redemptions)}",
        f"{roi:.2f}%",
        performance_fig,
        correlation_fig,
        form_message
    )

@app.callback(
    [
        Output('log-table', 'data'),
    ],
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('region-filter', 'value'),
        Input('salesperson-filter', 'value'),
        Input('channel-filter', 'value')
    ]
)
def update_logs(start_date, end_date, region, salesperson, channel):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == region]
    if salesperson != 'All':
        filtered_df = filtered_df[filtered_df['salesperson'] == salesperson]
    if channel != 'All':
        filtered_df = filtered_df[filtered_df['marketing_channel'] == channel]

    log_data = filtered_df[['date', 'country', 'salesperson', 'marketing_channel', 'details']].sort_values(by='date', ascending=False)
    table_data = log_data.to_dict('records')

    return (
        table_data,
    )

@app.callback(
    [
        Output('top-salesperson', 'children'),
        Output('low-salesperson', 'children'),
        Output('salesperson-bar', 'figure'),
        Output('salesperson-trend', 'figure')
    ],
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('region-filter', 'value'),
        Input('salesperson-filter', 'value'),
        Input('channel-filter', 'value')
    ]
)
def update_salesperson(start_date, end_date, region, salesperson, channel):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == region]
    if salesperson != 'All':
        filtered_df = filtered_df[filtered_df['salesperson'] == salesperson]
    if channel != 'All':
        filtered_df = filtered_df[filtered_df['marketing_channel'] == channel]

    sales_by_person = filtered_df.groupby('salesperson').agg({'sales': 'sum', 'sales_target': 'sum'}).reset_index()
    sales_by_person['performance'] = sales_by_person['sales'] / sales_by_person['sales_target'] * 100
    top_salesperson = sales_by_person.loc[sales_by_person['sales'].idxmax(), 'salesperson'] if not sales_by_person.empty else "N/A"
    low_salesperson = sales_by_person.loc[sales_by_person['sales'].idxmin(), 'salesperson'] if not sales_by_person.empty else "N/A"

    # Bar Chart for Team Performance
    bar_fig = px.bar(
        sales_by_person,
        x='salesperson',
        y='sales',
        title="Sales by Salesperson vs Target",
        color_discrete_sequence=['blue']
    )
    bar_fig.add_scatter(x=sales_by_person['salesperson'], y=sales_by_person['sales_target'], mode='markers', name='Target', marker=dict(color='red', size=10, symbol='x'))
    bar_fig.update_traces(marker_color=['green' if p >= 100 else 'yellow' if p >= 80 else 'red' for p in sales_by_person['performance']])
    bar_fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(size=8),
        title_font_size=10,
        xaxis_title="Salesperson",
        yaxis_title="Sales ($)",
        xaxis_tickangle=45
    )

    # Trend by Salesperson
    trend_data = filtered_df.groupby(['date', 'salesperson'])['sales'].sum().reset_index()
    trend_fig = px.line(
        trend_data,
        x='date',
        y='sales',
        color='salesperson',
        title="Sales Trends by Salesperson"
    )
    trend_fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), font=dict(size=8), title_font_size=10)

    return (
        top_salesperson,
        low_salesperson,
        bar_fig,
        trend_fig
    )

if __name__ == "__main__":
    app.run(debug=True)
