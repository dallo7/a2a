import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table, ALL, no_update
import dash_bootstrap_components as dbc
import datetime
import uuid
import sqlite3
import pandas as pd
import plotly.express as px
import base64
import io
import pytz

# --- Database Setup ---
DB_FILE = 'banking_final.db5'


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS accounts (id TEXT PRIMARY KEY, name TEXT NOT NULL, bank TEXT NOT NULL, accountNumber TEXT NOT NULL UNIQUE, balance REAL NOT NULL, type TEXT NOT NULL)''')
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS transactions (id TEXT PRIMARY KEY, from_acct TEXT, to_acct TEXT, amount REAL NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, timestamp TEXT NOT NULL, method TEXT)''')
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS master_employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, bank TEXT NOT NULL, account TEXT NOT NULL, amount REAL NOT NULL, department TEXT NOT NULL)''')

        cursor.execute("SELECT COUNT(*) FROM accounts")
        if cursor.fetchone()[0] == 0:
            accounts_data = [('acc001', 'John Doe', 'KCB Bank', '1234567890', 45000, 'personal'),
                             ('acc002', 'Sarah Wilson', 'Equity Bank', '2345678901', 78500, 'personal'),
                             ('acc003', 'Capital Pay Corp', 'Stanbic Bank', '3456789012', 1500000, 'business'),
                             ('acc004', 'Green Valley Corp', 'Co-op Bank', '4567890123', 180000, 'business'),
                             ('acc005', 'Mohamed Hassan', 'Nile Commercial Bank', '5678901234', 92000, 'personal'),
                             ('acc006', 'Amina Yusuf', 'Ecobank', '6789012345', 62000, 'personal'),
                             ('acc007', 'David Chen', 'I&M Bank', '7890123456', 88000, 'personal'),
                             ('acc008', 'Fatima Al-Jamil', 'Absa Bank', '8901234567', 110000, 'personal'),
                             ('acc009', 'Ken Okoro', 'NCBA Bank', '9012345678', 71500, 'personal'),
                             ('acc010', 'Maria Rodriguez', 'Diamond Trust Bank', '0123456789', 95000, 'personal')]
            cursor.executemany(
                "INSERT INTO accounts (id, name, bank, accountNumber, balance, type) VALUES (?, ?, ?, ?, ?, ?)",
                accounts_data)

        cursor.execute("SELECT COUNT(*) FROM transactions")
        if cursor.fetchone()[0] == 0:
            now = datetime.datetime.now(pytz.timezone('Africa/Nairobi'))
            initial_transactions = [('txn001', 'acc003', 'acc001', 50000, 'payroll', 'completed',
                                     (now - datetime.timedelta(days=3)).isoformat(), 'Bulk'), (
                                    'txn002', 'acc004', 'acc002', 12000, 'transfer', 'completed',
                                    (now - datetime.timedelta(days=2)).isoformat(), 'RTGS'), (
                                    'txn003', 'acc003', 'acc005', 62000, 'payroll', 'completed',
                                    (now - datetime.timedelta(days=4)).isoformat(), 'Bulk'), (
                                    'txn004', 'acc002', 'acc008', 7500, 'transfer', 'completed',
                                    (now - datetime.timedelta(days=10)).isoformat(), 'IFT'), (
                                    'txn005', 'acc003', 'acc009', 71000, 'payroll', 'completed',
                                    (now - datetime.timedelta(days=32)).isoformat(), 'Bulk'), (
                                    'txn006', 'acc001', 'acc004', 25000, 'transfer', 'completed',
                                    (now - datetime.timedelta(days=35)).isoformat(), 'IFT'), (
                                    'txn007', 'acc003', 'acc002', 45000, 'payroll', 'completed',
                                    (now - datetime.timedelta(days=65)).isoformat(), 'Bulk'), (
                                    'txn008', 'acc004', 'acc007', 18000, 'transfer', 'completed',
                                    (now - datetime.timedelta(days=70)).isoformat(), 'IFT')]
            cursor.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", initial_transactions)

        cursor.execute("SELECT COUNT(*) FROM master_employees")
        if cursor.fetchone()[0] == 0:
            master_employee_data = [('John Doe', 'KCB Bank', '1234567890', 50000, 'Sales'),
                                    ('Sarah Wilson', 'Equity Bank', '2345678901', 45000, 'Marketing'),
                                    ('Mohamed Hassan', 'Nile Commercial Bank', '5678901234', 60000, 'Engineering'),
                                    ('Amina Yusuf', 'Ecobank', '6789012345', 52000, 'Engineering'),
                                    ('David Chen', 'I&M Bank', '7890123456', 75000, 'Sales'),
                                    ('Fatima Al-Jamil', 'Absa Bank', '8901234567', 91000, 'Engineering'),
                                    ('Ken Okoro', 'NCBA Bank', '9012345678', 68000, 'HR'),
                                    ('Maria Rodriguez', 'Diamond Trust Bank', '0123456789', 82000, 'Marketing'),
                                    ('James Omondi', 'KCB Bank', '1122334455', 48000, 'Sales'),
                                    ('Grace Wanjiku', 'Equity Bank', '2233445566', 53000, 'HR'),
                                    ('Peter Musyoka', 'Co-op Bank', '3344556677', 61000, 'Engineering')]
            cursor.executemany(
                "INSERT INTO master_employees (name, bank, account, amount, department) VALUES (?, ?, ?, ?, ?)",
                master_employee_data)
        conn.commit()


# --- Initialize DB ---
init_db()


# --- Helper Functions (Unchanged) ---
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_banks():
    with get_db_connection() as conn:
        banks = [row[0] for row in conn.execute("SELECT DISTINCT bank FROM accounts ORDER BY bank").fetchall()]
        emp_banks = [row[0] for row in conn.execute(
            "SELECT DISTINCT bank FROM master_employees WHERE bank IS NOT NULL AND bank != '' ORDER BY bank").fetchall()]
        return sorted(list(set(banks + emp_banks)))


def get_account_details(account_id):
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()


def get_account_name(account_id):
    if not account_id: return "Corporate Payroll"
    details = get_account_details(account_id)
    return details['name'] if details else 'Unknown Account'


def format_currency(amount):
    if amount is None: amount = 0
    return f"KES {float(amount):,.2f}"


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return html.Div(['Please upload a CSV or Excel file.'])
        df.columns = df.columns.str.lower().str.strip()
        return df
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])


# --- Initialize App ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
app.config.suppress_callback_exceptions = True

server = app.server


# --- UI Component Creation Functions ---
def create_processing_animation(status='processing', message=None):
    if status == 'processing': return html.Div(
        [dbc.Spinner(size="lg", color="primary"), html.H4("Securely Processing...", className="mt-3 text-primary")],
        className="text-center p-4")
    if status == 'success': return html.Div([html.I(className="fas fa-check-circle fa-4x text-success"),
                                             html.H4("Transaction Successful!", className="mt-3 text-success")],
                                            className="text-center p-4")
    if status == 'failed': return html.Div([html.I(className="fas fa-times-circle fa-4x text-danger"),
                                            html.H4("Transaction Failed", className="mt-3 text-danger"),
                                            html.P(message, className="text-muted mt-2")], className="text-center p-4")


def create_mobile_keypad(pin_value=''):
    keypad_style = {'width': '60px', 'height': '60px', 'margin': '5px', 'fontSize': '24px', 'borderRadius': '50%',
                    'border': '2px solid #007bff', 'backgroundColor': '#f8f9fa'}
    pin_display_text = '●' * len(pin_value) + '○' * (4 - len(pin_value))
    is_confirm_disabled = len(pin_value) != 4
    rows = [
        [dbc.Button(str(i), id={'type': 'keypad-btn', 'index': str(i)}, style=keypad_style, color="outline-primary") for
         i in range(j, j + 3)] for j in range(1, 10, 3)]
    rows.append([
        dbc.Button(html.I(className="fas fa-backspace"), id={'type': 'keypad-btn', 'index': 'del'}, style=keypad_style,
                   color="outline-danger"),
        dbc.Button("0", id={'type': 'keypad-btn', 'index': '0'}, style=keypad_style, color="outline-primary"),
        dbc.Button(html.I(className="fas fa-check"), id={'type': 'keypad-btn', 'index': 'confirm'}, style=keypad_style,
                   color="success" if not is_confirm_disabled else "secondary", disabled=is_confirm_disabled)
    ])
    return html.Div([
        html.H4("🔐 Enter Your Authorization PIN", className="text-center mb-4"),
        html.Div(pin_display_text, style={'fontSize': '32px', 'letterSpacing': '10px'},
                 className="text-center mb-4 font-monospace text-primary"),
        html.Div([dbc.Row([dbc.Col(btn) for btn in row], className="justify-content-center mb-2") for row in rows],
                 style={'maxWidth': '280px', 'margin': '0 auto'})
    ])


def create_account_card(account_id):
    account_data = get_account_details(account_id)
    if not account_data: return html.Div()
    card_type = "from" if "from-account-dropdown" in str(callback_context.triggered_id) else "to"
    color, icon, title = ("danger", "arrow-left", "From Account") if card_type == "from" else (
    "success", "arrow-right", "To Account")
    return dbc.Card(dbc.CardBody([
        dbc.Badge([html.I(className=f"fas fa-{icon} me-2"), title], color=color, className="mb-3"),
        dbc.Row([dbc.Col([html.Strong("Account Holder:"), html.Div(account_data['name'], className="fw-bold")]),
                 dbc.Col([html.Strong("Bank:"), html.Div(account_data['bank'], className="fw-bold")])],
                className="mb-2"),
        dbc.Row([dbc.Col(
            [html.Strong("Account Number:"), html.Div(account_data['accountNumber'], className="font-monospace")]),
                 dbc.Col([html.Strong("Balance:"),
                          html.H4(format_currency(account_data['balance']), className=f"text-{color} fw-bold mb-0")])])
    ]), className=f"border-{color} border-2 bg-light")


def create_transfer_form():
    with get_db_connection() as conn:
        accounts = conn.execute("SELECT * FROM accounts").fetchall()
    accounts_options = [{'label': f"{acc['name']} - {acc['bank']}", 'value': acc['id']} for acc in accounts]
    return html.Div([
        html.H2("💸 Account-to-Account Transfer", className="text-center text-primary fw-bold mb-4"),
        dbc.Row([
            dbc.Col([html.H5([html.I(className="fas fa-arrow-left text-danger me-2"), "From Account"]),
                     dcc.Dropdown(id="from-account-dropdown", options=accounts_options),
                     html.Div(id="from-account-details", className="mt-3")], width=6),
            dbc.Col([html.H5([html.I(className="fas fa-arrow-right text-success me-2"), "To Account"]),
                     dcc.Dropdown(id="to-account-dropdown", options=accounts_options),
                     html.Div(id="to-account-details", className="mt-3")], width=6)
        ], className="mb-4"),
        dbc.Card(dbc.CardBody([dbc.Row([dbc.Col([html.Label("💰 Transfer Amount (KES)"), dbc.InputGroup(
            [dbc.InputGroupText("KES"), dbc.Input(id="transfer-amount", type="number", min=1)])])])]),
                 className="bg-light mb-4"),
        html.Div(dbc.Button([html.I(className="fas fa-rocket me-2"), "Execute Transfer"], id="execute-transfer-btn",
                            color="primary", size="lg", disabled=True, className="w-100"))
    ])


def create_payroll_section():
    with get_db_connection() as conn:
        employee_options = [{'label': row['name'], 'value': row['id']} for row in
                            conn.execute("SELECT id, name FROM master_employees ORDER BY name ASC").fetchall()]
    return html.Div([
        dcc.Store(id='payroll-mode-store', data='select'),
        dcc.Store(id='bank-selection-store'),
        html.H2("💼 Bulk Payroll Management", className="text-center text-primary fw-bold mb-4"),
        dbc.Card([
            dbc.CardHeader(html.H5("1. Load Employee Data")),
            dbc.CardBody([
                html.Div([
                    dbc.Button("Select from List", id="btn-mode-select", color="primary"),
                    dbc.Button("Upload File", id="btn-mode-upload", color="secondary"),
                    dbc.Button("Manual Entry", id="btn-mode-manual", color="secondary"),
                ], className="d-flex flex-wrap gap-2 mb-3"),
                html.Div(dcc.Dropdown(id='employee-selection-dropdown', options=employee_options, multi=True),
                         id='payroll-input-select'),
                html.Div([
                    dcc.Upload(id='upload-payroll-data',
                               children=html.Div(['Drag & Drop or ', html.A('Select Excel/CSV File')]),
                               style={'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px',
                                      'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center'}),
                    html.Small("File must contain 'name', 'bank', 'account', and 'amount' columns.",
                               className="text-muted")
                ], id='payroll-input-upload', style={'display': 'none'}),
                html.Div(dbc.Button([html.I(className="fas fa-plus me-2"), "Add New Row"], id='add-payroll-row-btn',
                                    color='primary', outline=True, className="w-100"), id='payroll-input-manual',
                         style={'display': 'none'}),
            ])
        ]),
        dbc.Card([
            dbc.CardHeader(html.H5("2. Review and Process Payroll Batch")),
            dbc.CardBody([
                dbc.Button("Choose Bank for Selected Row", id="open-bank-modal-btn", color="info", className="mb-3",
                           disabled=True),
                dash_table.DataTable(id='payroll-table',
                                     columns=[{"name": "ID", "id": "id"},
                                              {"name": "Employee", "id": "name", "editable": True},
                                              {"name": "Bank", "id": "bank", "editable": False},
                                              {"name": "Account Number", "id": "account", "editable": True},
                                              {"name": "Net Pay (KES)", "id": "amount", "editable": True,
                                               "type": "numeric"}],
                                     data=[], row_deletable=True, style_cell={'textAlign': 'left', 'padding': '10px'},
                                     style_header={'backgroundColor': '#e9ecef', 'fontWeight': 'bold'},
                                     style_cell_conditional=[{'if': {'column_id': 'id'}, 'display': 'none'}],
                                     ),
                html.Div(id="payroll-summary", className="text-end fw-bold mt-3 border-top pt-3 fs-5"),
            ])
        ], className="mt-4"),
        html.Div(dbc.Button([html.I(className="fas fa-rocket me-2"), "Process Bulk Payroll"], id="process-payroll-btn",
                            color="success", size="lg", className="mt-4 w-100", disabled=True), className="mt-4")
    ])


def create_header():
    with get_db_connection() as conn: total_volume = \
    conn.execute("SELECT SUM(amount) FROM transactions WHERE status='completed'").fetchone()[0] or 0
    return dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(dbc.Row([
        dbc.Col(
            [html.H1("Boma Money Transfer"), html.P("Where Everyone Belongs", className="text-muted")],
            width=8),
        dbc.Col(html.Div([html.Small("Total Network Volume"), html.H2(format_currency(total_volume))],
                         className="text-end"), width=4)
    ])), className="mb-4")))


def create_navigation():
    return dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(dbc.ButtonGroup([
        dbc.Button([html.I(className="fas fa-exchange-alt me-2"), "Account Transfer"], id="btn-transfer",
                   className="me-2"),
        dbc.Button([html.I(className="fas fa-users me-2"), "Bulk Transfers/Payroll"], id="btn-payroll", className="me-2"),
        dbc.Button([html.I(className="fas fa-credit-card me-2"), "Transactions"], id="btn-transactions",
                   className="me-2"),
        dbc.Button([html.I(className="fas fa-building me-2"), "Network Dashboard"], id="btn-dashboard",
                   className="me-2"),
        dbc.Button([html.I(className="fas fa-chart-pie me-2"), "Analytics"], id="btn-analytics")
    ]))), className="mb-4"))


# --- MODIFIED --- Analytics view adds a new chart placeholder
def create_analytics_view():
    return html.Div([
        dbc.Row(id="kpi-cards", className="mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='payroll-by-dept-chart')])), width=6),
            dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='transfer-dist-chart')])), width=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='monthly-trends-chart')])), width=7),
            # --- NEW CHART ---
            dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='top-transfer-banks-chart')])), width=5),
        ], className="mb-4")
    ])


# --- MODIFIED --- Transactions view now uses tabs
def create_transactions_view():
    with get_db_connection() as conn:
        transactions = conn.execute("SELECT * FROM transactions ORDER BY timestamp DESC").fetchall()

    def generate_card(txn):
        status_color = "success" if txn['status'] == 'completed' else "warning"
        icon, desc = ("fa-users text-primary", f"Bulk Payroll from {get_account_name(txn['from_acct'])}") if txn[
                                                                                                                 'type'] == 'payroll' else (
        "fa-exchange-alt text-info", f"{get_account_name(txn['from_acct'])} → {get_account_name(txn['to_acct'])}")
        return dbc.Card(dbc.CardBody(dbc.Row([
            dbc.Col(html.Div([html.I(className=f"fas {icon} me-3 fs-4"), html.Div(
                [html.H6([desc, dbc.Badge(txn['method'], color="secondary", pill=True, className="ms-2")]),
                 html.Small(datetime.datetime.fromisoformat(txn['timestamp']).strftime("%Y-%m-%d %H:%M:%S"))])],
                             className="d-flex align-items-center"), width=8),
            dbc.Col(html.Div(
                [html.H5(format_currency(txn['amount'])), dbc.Badge(txn['status'].title(), color=status_color)],
                className="text-end"), width=4)
        ])), className="mb-3")

    all_cards = [generate_card(txn) for txn in transactions]
    payroll_cards = [generate_card(txn) for txn in transactions if txn['type'] == 'payroll']
    transfer_cards = [generate_card(txn) for txn in transactions if txn['type'] == 'transfer']

    return html.Div([
        html.H2("📊 Transaction History", className="text-primary fw-bold mb-4"),
        dbc.Tabs([
            dbc.Tab(all_cards, label="All Transactions"),
            dbc.Tab(transfer_cards, label="💸 Account Transfers"),
            dbc.Tab(payroll_cards, label="💼 Bulk Payroll"),
        ])
    ])


# --- MODIFIED --- Dashboard now shows more specific stats and dynamic bank data
def create_dashboard():
    banks = get_all_banks()
    with get_db_connection() as conn:
        num_accounts = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        # More specific queries for today's transactions
        transfers_today = conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE date(timestamp) = date('now') AND type = 'transfer'").fetchone()[0]
        payrolls_today = conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE date(timestamp) = date('now') AND type = 'payroll'").fetchone()[0]
        # Query for bank volume in the last 7 days
        bank_volumes = conn.execute("""
            SELECT a.bank, SUM(t.amount) as volume
            FROM transactions t
            JOIN accounts a ON t.to_acct = a.id
            WHERE date(t.timestamp) >= date('now', '-7 days') AND t.type = 'transfer'
            GROUP BY a.bank
        """).fetchall()
        bank_volume_map = {row['bank']: row['volume'] for row in bank_volumes}

    bank_cards = []
    for bank in banks:
        volume = bank_volume_map.get(bank, 0)
        card = dbc.Col(dbc.Card([
            dbc.CardHeader(html.Div([html.I(className="fas fa-university me-2"), html.Span(bank)],
                                    className="d-flex align-items-center")),
            dbc.CardBody([
                html.P("Active", className="text-success"),
                html.H4(format_currency(volume), className="text-info"),
                html.Small("7-Day Inbound Volume", className="text-muted")
            ])
        ]), width=3, className="mb-3")
        bank_cards.append(card)

    return dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader(html.H4("Connected Banking Network")), dbc.CardBody(dbc.Row(bank_cards))]),
                width=9),
        dbc.Col(dbc.Card([dbc.CardHeader(html.H5("Quick Stats")), dbc.CardBody([
            dbc.Row([dbc.Col("Active Accounts"),
                     dbc.Col(html.Strong(num_accounts, className="text-primary"), width="auto")], className="mb-3"),
            dbc.Row([dbc.Col("Today's Transfers"),
                     dbc.Col(html.Strong(transfers_today, className="text-success"), width="auto")], className="mb-3"),
            dbc.Row([dbc.Col("Today's Payrolls"),
                     dbc.Col(html.Strong(payrolls_today, className="text-info"), width="auto")])
        ])]), width=3)
    ])


def create_bank_selection_modal():
    banks = get_all_banks()
    list_group = dbc.ListGroup(
        [dbc.ListGroupItem(bank, action=True, id={'type': 'bank-select-item', 'index': bank}) for bank in banks],
        flush=True)
    return dbc.Modal([dbc.ModalHeader("Select a Bank"), dbc.ModalBody(list_group)], id="bank-selection-modal",
                     is_open=False)


# --- App Layout ---
app.layout = dbc.Container([
    dcc.Store(id='current-view-store', data='payroll'),
    dcc.Store(id='current-pin-store', data=''),
    dcc.Store(id='pending-transaction-store', data={}),
    dcc.Store(id='transaction-refresh-signal', data=None),
    dcc.Interval(id='interval-component', interval=3000, n_intervals=0, disabled=True),

    dbc.Modal([dbc.ModalHeader(dbc.ModalTitle(id="payment-modal-title")), dbc.ModalBody(id="payment-confirmation-body"),
               dbc.ModalFooter(
                   [dbc.Button("Cancel", id="cancel-payment-btn"), dbc.Button("Continue", id="continue-to-pin-btn")])],
              id="payment-modal", is_open=False),
    dbc.Modal([dbc.ModalHeader("Secure PIN Entry"), dbc.ModalBody(id="pin-entry-body"),
               dbc.ModalFooter(dbc.Button("Cancel", id="pin-cancel-btn"))], id="pin-modal", is_open=False,
              backdrop="static"),
    dbc.Modal(
        [dbc.ModalBody(id="processing-body"), dbc.ModalFooter(dbc.Button("Close", id="close-processing-modal-btn"))],
        id="processing-modal", is_open=False, centered=True),
    create_bank_selection_modal(),

    html.Div(id='header-container'),
    create_navigation(),

    html.Div([
        html.Div(create_payroll_section(), id='page-payroll'),
        html.Div(create_transfer_form(), id='page-transfer', style={'display': 'none'}),
        html.Div(create_transactions_view(), id='page-transactions', style={'display': 'none'}),
        html.Div(create_dashboard(), id='page-dashboard', style={'display': 'none'}),
        html.Div(create_analytics_view(), id='page-analytics', style={'display': 'none'}),
    ])
], className="py-4", style={'maxWidth': '70%', 'backgroundColor': '#f8f9fa'})


# --- Callbacks ---
@app.callback(
    [Output('current-view-store', 'data')] + [Output(f'btn-{view}', 'color') for view in
                                              ['payroll', 'transfer', 'transactions', 'dashboard', 'analytics']],
    [Input(f'btn-{view}', 'n_clicks') for view in ['payroll', 'transfer', 'transactions', 'dashboard', 'analytics']]
)
def update_active_button(p, t, r, d, a):
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'btn-payroll'
    view_name = button_id.replace('btn-', '')
    colors = {v: 'outline-primary' for v in ['payroll', 'transfer', 'transactions', 'dashboard', 'analytics']}
    colors[view_name] = 'primary'
    return view_name, colors['payroll'], colors['transfer'], colors['transactions'], colors['dashboard'], colors[
        'analytics']


@app.callback(
    [Output(f'page-{view}', 'style') for view in ['payroll', 'transfer', 'transactions', 'dashboard', 'analytics']],
    Input('current-view-store', 'data')
)
def display_page(view_name):
    styles = {v: {'display': 'none'} for v in ['payroll', 'transfer', 'transactions', 'dashboard', 'analytics']}
    if view_name in styles:
        styles[view_name] = {'display': 'block'}
    return styles['payroll'], styles['transfer'], styles['transactions'], styles['dashboard'], styles['analytics']


@app.callback(Output('header-container', 'children'), Input('transaction-refresh-signal', 'data'))
def update_header_live(refresh_signal): return create_header()


@app.callback(
    [Output('payroll-mode-store', 'data'), Output('btn-mode-select', 'color'), Output('btn-mode-upload', 'color'),
     Output('btn-mode-manual', 'color'),
     Output('payroll-input-select', 'style'), Output('payroll-input-upload', 'style'),
     Output('payroll-input-manual', 'style')],
    [Input('btn-mode-select', 'n_clicks'), Input('btn-mode-upload', 'n_clicks'), Input('btn-mode-manual', 'n_clicks')]
)
def switch_payroll_mode(select_clicks, upload_clicks, manual_clicks):
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'btn-mode-select'
    if button_id == 'btn-mode-upload':
        return 'upload', 'secondary', 'primary', 'secondary', {'display': 'none'}, {'display': 'block'}, {
            'display': 'none'}
    elif button_id == 'btn-mode-manual':
        return 'manual', 'secondary', 'secondary', 'primary', {'display': 'none'}, {'display': 'none'}, {
            'display': 'block'}
    return 'select', 'primary', 'secondary', 'secondary', {'display': 'block'}, {'display': 'none'}, {'display': 'none'}


# --- MODIFIED to be responsive to new transactions ---
@app.callback(
    [Output('kpi-cards', 'children'),
     Output('payroll-by-dept-chart', 'figure'),
     Output('transfer-dist-chart', 'figure'),
     Output('monthly-trends-chart', 'figure'),
     Output('top-transfer-banks-chart', 'figure')],
    [Input('current-view-store', 'data'),
     # --- ADDED an Input to listen for the refresh signal ---
     Input('transaction-refresh-signal', 'data')]
)
def update_analytics(view, refresh_signal):
    # --- MODIFIED the function signature to accept the new input ---
    if view != 'analytics':
        return no_update, no_update, no_update, no_update, no_update

    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM transactions WHERE status='completed'", conn)
        emp_df = pd.read_sql_query("SELECT department, amount FROM master_employees", conn)
        banks_df = pd.read_sql_query("SELECT id, bank FROM accounts", conn)

    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('Africa/Nairobi')
    today = pd.Timestamp.now(tz='Africa/Nairobi').normalize()
    start_of_week, start_of_month = today - pd.to_timedelta(today.weekday()), today.replace(day=1)

    payroll_df = df[df['type'] == 'payroll']
    transfer_df = df[df['type'] == 'transfer']

    p_month_vol, p_month_count = payroll_df[payroll_df['timestamp'] >= start_of_month]['amount'].sum(), len(
        payroll_df[payroll_df['timestamp'] >= start_of_month])
    p_week_vol, p_week_count = payroll_df[payroll_df['timestamp'] >= start_of_week]['amount'].sum(), len(
        payroll_df[payroll_df['timestamp'] >= start_of_week])
    t_month_vol, t_month_count = transfer_df[transfer_df['timestamp'] >= start_of_month]['amount'].sum(), len(
        transfer_df[transfer_df['timestamp'] >= start_of_month])
    t_week_vol, t_week_count = transfer_df[transfer_df['timestamp'] >= start_of_week]['amount'].sum(), len(
        transfer_df[transfer_df['timestamp'] >= start_of_week])

    kpi_cards = dbc.Row([
        dbc.Col(html.H4("This Month's Activity"), width=12),
        dbc.Col(dbc.Card([dbc.CardBody(
            [html.H6("Bulk Payroll"), html.H3(format_currency(p_month_vol), className="text-primary"),
             html.P(f"{p_month_count} Batches")])]), width=6, className="mb-3"),
        dbc.Col(dbc.Card([dbc.CardBody(
            [html.H6("Account Transfers"), html.H3(format_currency(t_month_vol), className="text-success"),
             html.P(f"{t_month_count} Transfers")])]), width=6, className="mb-3"),
        dbc.Col(html.H4("This Week's Activity"), width=12),
        dbc.Col(dbc.Card([dbc.CardBody(
            [html.H6("Bulk Payroll"), html.H3(format_currency(p_week_vol), className="text-primary"),
             html.P(f"{p_week_count} Batches")])]), width=6, className="mb-3"),
        dbc.Col(dbc.Card([dbc.CardBody(
            [html.H6("Account Transfers"), html.H3(format_currency(t_week_vol), className="text-success"),
             html.P(f"{t_week_count} Transfers")])]), width=6, className="mb-3"),
    ])

    dept_payroll = emp_df.groupby('department')['amount'].sum().reset_index()
    fig_dept = px.pie(dept_payroll, names='department', values='amount', title='Projected Payroll by Department',
                      hole=0.4)
    fig_dist = px.histogram(transfer_df, x='amount', nbins=20, title='Transfer Amount Distribution')

    payroll_monthly, transfer_monthly = payroll_df.set_index('timestamp').resample('M')['amount'].sum(), \
    transfer_df.set_index('timestamp').resample('M')['amount'].sum()
    trends_df = pd.DataFrame({'Payroll': payroll_monthly, 'Transfers': transfer_monthly}).reset_index()
    trends_df['timestamp'] = trends_df['timestamp'].dt.strftime('%Y-%b')
    fig_trends = px.line(trends_df, x='timestamp', y=['Payroll', 'Transfers'], title='Monthly Volume Trends',
                         markers=True)

    transfer_banks = pd.merge(transfer_df, banks_df, left_on='to_acct', right_on='id', how='left')
    top_banks = transfer_banks.groupby('bank')['amount'].sum().nlargest(5).reset_index()
    fig_top_banks = px.bar(top_banks, x='bank', y='amount', title='Top 5 Transfer Destinations (by Bank)',
                           labels={'bank': 'Bank', 'amount': 'Total Volume'})

    return kpi_cards, fig_dept, fig_dist, fig_trends, fig_top_banks


@app.callback(Output('open-bank-modal-btn', 'disabled'), Input('payroll-table', 'active_cell'))
def toggle_open_bank_modal_button(active_cell):
    return not (active_cell and active_cell['column_id'] == 'bank')


@app.callback([Output('bank-selection-modal', 'is_open'), Output('bank-selection-store', 'data')],
              Input('open-bank-modal-btn', 'n_clicks'), State('payroll-table', 'active_cell'),
              prevent_initial_call=True)
def open_bank_modal_and_store_row(n, cell):
    if n: return True, {'row': cell['row']}
    return False, no_update


@app.callback([Output('payroll-table', 'data', allow_duplicate=True),
               Output('bank-selection-modal', 'is_open', allow_duplicate=True)],
              Input({'type': 'bank-select-item', 'index': ALL}, 'n_clicks'),
              [State('bank-selection-store', 'data'), State('payroll-table', 'data')], prevent_initial_call=True)
def select_bank_and_update_table(clicks, store, table):
    if not any(clicks): return no_update
    bank_name = callback_context.triggered_id['index']
    table[store['row']]['bank'] = bank_name
    return table, False


@app.callback(Output('from-account-details', 'children'), Input('from-account-dropdown', 'value'))
def update_from_account_details(account_id):
    if account_id: return create_account_card(account_id)
    return html.Div()


@app.callback(Output('to-account-details', 'children'), Input('to-account-dropdown', 'value'))
def update_to_account_details(account_id):
    if account_id: return create_account_card(account_id)
    return html.Div()


@app.callback(Output('execute-transfer-btn', 'disabled'),
              [Input('from-account-dropdown', 'value'), Input('to-account-dropdown', 'value'),
               Input('transfer-amount', 'value')])
def toggle_execute_button(f, t, a):
    return not all([f, t, a and float(a) > 0, f != t])


@app.callback(Output('payroll-table', 'data'),
              [Input('employee-selection-dropdown', 'value'), Input('upload-payroll-data', 'contents'),
               Input('add-payroll-row-btn', 'n_clicks')],
              [State('payroll-mode-store', 'data'), State('upload-payroll-data', 'filename'),
               State('payroll-table', 'data')], prevent_initial_call=True)
def update_payroll_table_data(ids, contents, clicks, mode, filename, data):
    trig_id = callback_context.triggered_id
    if mode == 'select' and trig_id == 'employee-selection-dropdown':
        if not ids: return []
        placeholders = ','.join(['?'] * len(ids))
        with get_db_connection() as conn:
            df = pd.read_sql_query(
                f"SELECT id, name, bank, account, amount FROM master_employees WHERE id IN ({placeholders})", conn,
                params=ids)
        return df.to_dict('records')
    elif mode == 'upload' and contents:
        df = parse_contents(contents, filename)
        cols = ['name', 'bank', 'account', 'amount']
        if isinstance(df, pd.DataFrame) and all(c in df.columns for c in cols): return df[cols].to_dict('records')
        return []
    elif mode == 'manual' and trig_id == 'add-payroll-row-btn':
        new_row = {'id': None, 'name': '', 'bank': '(Click to select)', 'account': '', 'amount': None}
        return (data or []) + [new_row]
    return no_update


@app.callback([Output('payroll-summary', 'children'), Output('process-payroll-btn', 'disabled')],
              Input('payroll-table', 'data'))
def update_payroll_summary(data):
    if not data: return "Total Payroll: KES 0.00 | Employees: 0", True
    total = sum(float(row.get('amount') or 0) for row in data)
    return f"Total: {format_currency(total)} | Employees: {len(data)}", total <= 0


@app.callback([Output('payment-modal', 'is_open'), Output('payment-modal-title', 'children'),
               Output('payment-confirmation-body', 'children'), Output('pending-transaction-store', 'data')],
              [Input('execute-transfer-btn', 'n_clicks'), Input('process-payroll-btn', 'n_clicks')],
              [State('from-account-dropdown', 'value'), State('to-account-dropdown', 'value'),
               State('transfer-amount', 'value'), State('payroll-table', 'data')], prevent_initial_call=True)
def handle_confirmation(t_clicks, p_clicks, f_acct, t_acct, amt, p_data):
    trig_id = callback_context.triggered_id
    if trig_id == 'execute-transfer-btn':
        data = {'type': 'transfer', 'from': f_acct, 'to': t_acct, 'amount': float(amt)}
        body = html.Div([dbc.Row([dbc.Col("From:"), dbc.Col(get_account_name(f_acct))]),
                         dbc.Row([dbc.Col("To:"), dbc.Col(get_account_name(t_acct))]), html.Hr(),
                         html.H2(format_currency(float(amt)))])
        return True, "Confirm Transfer", body, data
    elif trig_id == 'process-payroll-btn':
        total = sum(float(row.get('amount') or 0) for row in p_data)
        data = {'type': 'payroll', 'employees': p_data, 'amount': total}
        body = html.Div([dbc.Alert(f"Process payment for {len(p_data)} employees?"), html.Hr(),
                         dbc.Row([dbc.Col("Total:"), dbc.Col(html.H3(format_currency(total)))])])
        return True, "Confirm Payroll", body, data
    return no_update


@app.callback(
    [Output('processing-modal', 'is_open'), Output('processing-body', 'children'),
     Output('payment-modal', 'is_open', allow_duplicate=True),
     Output('current-pin-store', 'data', allow_duplicate=True), Output('transaction-refresh-signal', 'data'),
     Output('interval-component', 'disabled', allow_duplicate=True)],
    Input('current-pin-store', 'data'), State('pending-transaction-store', 'data'), prevent_initial_call=True)
def process_payment(pin, data):
    if not pin or len(pin) != 4: return no_update
    if pin != '1234': return True, create_processing_animation('failed', "Invalid PIN."), False, '', no_update, False
    is_success, msg = False, ""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if data['type'] == 'transfer':
                bal = cursor.execute("SELECT balance FROM accounts WHERE id = ?", (data['from'],)).fetchone()[0]
                if bal < data['amount']: raise ValueError("Insufficient funds.")
                cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (data['amount'], data['from']))
                cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (data['amount'], data['to']))
                cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                f'txn{uuid.uuid4().hex[:6]}', data['from'], data['to'], data['amount'], 'transfer', 'completed',
                datetime.datetime.now(pytz.timezone('Africa/Nairobi')).isoformat(), 'IFT'))
            elif data['type'] == 'payroll':
                corp_bal = cursor.execute("SELECT balance FROM accounts WHERE id = 'acc003'").fetchone()[0]
                if corp_bal < data['amount']: raise ValueError("Insufficient corporate funds.")
                cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = 'acc003'", (data['amount'],))
                for emp in data['employees']:
                    rec_id = cursor.execute("SELECT id FROM accounts WHERE accountNumber = ? AND bank = ?",
                                            (emp['account'], emp['bank'])).fetchone()
                    if rec_id: cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?",
                                              (emp.get('amount', 0), rec_id[0]))
                cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                f'txn{uuid.uuid4().hex[:6]}', 'acc003', None, data['amount'], 'payroll', 'completed',
                datetime.datetime.now(pytz.timezone('Africa/Nairobi')).isoformat(), 'Bulk'))
            conn.commit()
            is_success = True
    except (sqlite3.Error, ValueError, TypeError, IndexError) as e:
        msg = str(e)
    body, refresh, interval = (
    create_processing_animation('success'), datetime.datetime.now().isoformat(), False) if is_success else (
    create_processing_animation('failed', msg), no_update, False)
    return True, body, False, '', refresh, interval


@app.callback(Output('payment-modal', 'is_open', allow_duplicate=True), Input('cancel-payment-btn', 'n_clicks'),
              prevent_initial_call=True)
def cancel_confirmation(n): return False if n else no_update


@app.callback(
    [Output('pin-modal', 'is_open'), Output('pin-entry-body', 'children'), Output('current-pin-store', 'data')],
    [Input('continue-to-pin-btn', 'n_clicks'), Input('pin-cancel-btn', 'n_clicks'),
     Input({'type': 'keypad-btn', 'index': ALL}, 'n_clicks')],
    [State('current-pin-store', 'data')], prevent_initial_call=True)
def handle_pin_modal(cont, canc, keys, pin):
    trig_id = callback_context.triggered_id
    if not trig_id: return no_update
    if trig_id == 'continue-to-pin-btn': return True, create_mobile_keypad(), ''
    if trig_id == 'pin-cancel-btn': return False, no_update, ''
    if isinstance(trig_id, dict):
        index, new_pin = trig_id['index'], pin or ""
        if index == 'del':
            new_pin = new_pin[:-1]
        elif index == 'confirm':
            return False, no_update, new_pin
        elif len(new_pin) < 4:
            new_pin += index
        return True, create_mobile_keypad(new_pin), new_pin
    return no_update


@app.callback(Output('processing-modal', 'is_open', allow_duplicate=True), Input('interval-component', 'n_intervals'),
              prevent_initial_call=True)
def auto_close_processing_modal(n): return False


@app.callback([Output('processing-modal', 'is_open', allow_duplicate=True),
               Output('interval-component', 'disabled', allow_duplicate=True)],
              Input('close-processing-modal-btn', 'n_clicks'), prevent_initial_call=True)
def manual_close_processing_modal(n): return False, True


if __name__ == '__main__':
    app.run(debug=True, port=6659)

