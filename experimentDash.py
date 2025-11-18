# ============================================================
# Interactive Options Strategy Dashboard with Dash
# ============================================================

import numpy as np
from dash import Dash, dcc, html, Input, Output, State, ALL, callback_context
import plotly.graph_objs as go

# ============================================================
# 1. Option Classes
# ============================================================

class OptionContract:
    def __init__(self, option_type, position, strike, premium, quantity=1, rate=0.0, maturity=1.0):
        self.option_type = option_type
        self.position = position
        self.strike = strike
        self.premium = premium
        self.quantity = quantity
        self.rate = rate
        self.maturity = maturity

    def payoff(self, S):
        if self.option_type == 'call':
            intrinsic = np.maximum(S - self.strike, 0)
        elif self.option_type == 'put':
            intrinsic = np.maximum(self.strike - S, 0)
        else:  # underlying
            intrinsic = S - self.strike

        intrinsic = intrinsic - self.premium

        if self.position == 'short':
            intrinsic *= -1

        intrinsic *= self.quantity
        return intrinsic

class OptionStrategy:
    def __init__(self, contracts):
        self.contracts = contracts

    def total_payoff(self, S):
        total = np.zeros_like(S, dtype=float)
        for c in self.contracts:
            total += c.payoff(S)
        return total

# ============================================================
# 2. Plotly Graph
# ============================================================

def plot_strategy_plotly(S, payoff, parity=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=S, y=payoff, mode='lines', name='Strategy Payoff'))
    if parity is not None:
        fig.add_trace(go.Scatter(x=S, y=parity, mode='lines', name='Parity', line=dict(dash='dash')))
    fig.update_layout(
        title="Options Strategy Payoff / Parity",
        xaxis_title="Underlying Price (S)",
        yaxis_title="Profit / Loss",
        template="plotly_white"
    )
    return fig

# ============================================================
# 3. Dash App Layout
# ============================================================

app = Dash(__name__)
app.title = "Options Strategy Dashboard"

app.layout = html.Div([
    html.H1("Interactive Options Strategy Dashboard"),

    html.Div([
        html.Div([
            html.Label('Min X'),
            dcc.Input(id='S_min', type='number', value=50, style={'width':'100px'})
            ], style={'display':'inline-block', 'marginRight':'20px'}),
        html.Div([
            html.Label('Max X'),
            dcc.Input(id='S_max', type='number', value=150, style={'width':'100px'})
        ], style={'display':'inline-block', 'marginRight':'20px'}),
        html.Div([
            html.Label('Points'),
            dcc.Input(id='S_points', type='number', value=500, style={'width':'100px'})
        ], style={'display':'inline-block'})
    ], style={'marginBottom':'20px'}),

    html.H3("Contracts"),
    html.Div(id='contracts-container', children=[]),
    html.Button('Add Contract', id='add-contract', n_clicks=0, style={'marginTop':'10px'}),

    html.Hr(),

    dcc.Graph(id='payoff-graph')
], style={'width':'90%', 'margin':'auto'})

# ============================================================
# 4. Callbacks
# ============================================================

# Combined callback to add/remove contracts
@app.callback(
    Output('contracts-container', 'children'),
    Input('add-contract', 'n_clicks'),
    Input({'type':'remove-contract','index':ALL}, 'n_clicks'),
    State('contracts-container', 'children')
)
def update_contracts(add_clicks, remove_clicks, children):
    if children is None:
        children = []

    ctx = callback_context
    if not ctx.triggered:
        return children

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Add contract
    if triggered_id == 'add-contract':
        new_index = len(children)
        new_row = html.Div([
            dcc.Dropdown(['call','put','underlying'], 'call', id={'type':'option_type','index':new_index}, style={'width':'100px','display':'inline-block','marginRight':'5px'}),
            dcc.Dropdown(['long','short'], 'long', id={'type':'position','index':new_index}, style={'width':'100px','display':'inline-block','marginRight':'5px'}),
            dcc.Input(id={'type':'strike','index':new_index}, type='number', value=100, placeholder='Strike', style={'width':'80px','marginRight':'5px'}),
            dcc.Input(id={'type':'premium','index':new_index}, type='number', value=5, placeholder='Premium', style={'width':'80px','marginRight':'5px'}),
            dcc.Input(id={'type':'quantity','index':new_index}, type='number', value=1, placeholder='Quantity', style={'width':'60px','marginRight':'5px'}),
            html.Button('Remove', id={'type':'remove-contract','index':new_index}, n_clicks=0)
        ], style={'marginBottom':'5px'}, id={'type':'contract-row','index':new_index})
        children.append(new_row)

    # Remove contract
    else:
        remove_index = eval(triggered_id)['index']
        children = [c for c in children if c['props']['id']['index'] != remove_index]

    return children

# Update payoff graph
@app.callback(
    Output('payoff-graph', 'figure'),
    Input({'type':'option_type','index':ALL}, 'value'),
    Input({'type':'position','index':ALL}, 'value'),
    Input({'type':'strike','index':ALL}, 'value'),
    Input({'type':'premium','index':ALL}, 'value'),
    Input({'type':'quantity','index':ALL}, 'value'),
    Input('S_min', 'value'),
    Input('S_max', 'value'),
    Input('S_points', 'value'),
)
def update_graph(option_types, positions, strikes, premiums, quantities, S_min, S_max, S_points):
    S = np.linspace(S_min, S_max, S_points)
    contracts = []
    for t, p, k, pr, q in zip(option_types, positions, strikes, premiums, quantities):
        if t is not None and p is not None and k is not None and pr is not None and q is not None:
            contracts.append(OptionContract(t, p, k, pr, q))
    strategy = OptionStrategy(contracts)
    payoff = strategy.total_payoff(S)
    fig = plot_strategy_plotly(S, payoff)
    return fig

# ============================================================
# 5. Run App
# ============================================================

if __name__ == "__main__":
    app.run_server(debug=True)