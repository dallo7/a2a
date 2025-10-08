
# import dash
# from dash import dcc, html, Input, Output, State, callback_context, dash_table, ALL, no_update
# import dash_bootstrap_components as dbc
# import datetime
# import uuid
# import sqlite3
# import pandas as pd
# import plotly.express as px
# import base64
# import io
# import pytz

# # --- Database Setup ---
# DB_FILE = 'banking_final.db5'


# def init_db():
#     with sqlite3.connect(DB_FILE) as conn:
#         cursor = conn.cursor()
#         # Core Tables
#         cursor.execute(
#             '''CREATE TABLE IF NOT EXISTS accounts (id TEXT PRIMARY KEY, name TEXT NOT NULL, bank TEXT NOT NULL, accountNumber TEXT NOT NULL UNIQUE, balance REAL NOT NULL, type TEXT NOT NULL)''')
#         cursor.execute(
#             '''CREATE TABLE IF NOT EXISTS transactions (id TEXT PRIMARY KEY, from_acct TEXT, to_acct TEXT, amount REAL NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, timestamp TEXT NOT NULL, method TEXT)''')
#         cursor.execute(
#             '''CREATE TABLE IF NOT EXISTS master_employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, bank TEXT NOT NULL, account TEXT NOT NULL, amount REAL NOT NULL, department TEXT NOT NULL)''')
#         # Tables for saving user and recipient details
#         cursor.execute(
#             '''CREATE TABLE IF NOT EXISTS saved_senders (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, msisdn TEXT, id_number TEXT, email TEXT, bank_name TEXT, bank_account_number TEXT)''')
#         cursor.execute(
#             '''CREATE TABLE IF NOT EXISTS saved_recipients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, msisdn TEXT, id_number TEXT, email TEXT, bank_name TEXT, bank_account_number TEXT)''')

#         cursor.execute("SELECT COUNT(*) FROM accounts")
#         if cursor.fetchone()[0] == 0:
#             accounts_data = [('acc001', 'John Doe', 'KCB Bank', '1234567890', 45000, 'personal'),
#                              ('acc002', 'Sarah Wilson', 'Equity Bank', '2345678901', 78500, 'personal'),
#                              ('acc003', 'Capital Pay Corp', 'Stanbic Bank', '3456789012', 1500000, 'business'),
#                              ('acc004', 'Green Valley Corp', 'Co-op Bank', '4567890123', 180000, 'business'),
#                              ('acc005', 'Mohamed Hassan', 'Nile Commercial Bank', '5678901234', 92000, 'personal'),
#                              ('acc006', 'Amina Yusuf', 'Ecobank', '6789012345', 62000, 'personal'),
#                              ('acc007', 'David Chen', 'I&M Bank', '7890123456', 88000, 'personal'),
#                              ('acc008', 'Fatima Al-Jamil', 'Absa Bank', '8901234567', 110000, 'personal'),
#                              ('acc009', 'Ken Okoro', 'NCBA Bank', '9012345678', 71500, 'personal'),
#                              ('acc010', 'Maria Rodriguez', 'Diamond Trust Bank', '0123456789', 95000, 'personal')]
#             cursor.executemany(
#                 "INSERT INTO accounts (id, name, bank, accountNumber, balance, type) VALUES (?, ?, ?, ?, ?, ?)",
#                 accounts_data)

#         cursor.execute("SELECT COUNT(*) FROM master_employees")
#         if cursor.fetchone()[0] == 0:
#             master_employee_data = [('John Doe', 'KCB Bank', '1234567890', 50000, 'Sales'),
#                                     ('Sarah Wilson', 'Equity Bank', '2345678901', 45000, 'Marketing'),
#                                     ('Mohamed Hassan', 'Nile Commercial Bank', '5678901234', 60000, 'Engineering')]
#             cursor.executemany(
#                 "INSERT INTO master_employees (name, bank, account, amount, department) VALUES (?, ?, ?, ?, ?)",
#                 master_employee_data)

#         cursor.execute("SELECT COUNT(*) FROM saved_senders")
#         if cursor.fetchone()[0] == 0:
#             senders_data = [
#                 ('Alice Mwangi', '254722123456', '12345678', 'alice.m@capitalpay.corp', 'Stanbic Bank', '3456789012'),
#                 ('Bob Otieno', '254711987654', '87654321', 'bob.o@capitalpay.corp', 'Stanbic Bank', '3456789012')
#             ]
#             cursor.executemany(
#                 "INSERT INTO saved_senders (name, msisdn, id_number, email, bank_name, bank_account_number) VALUES (?, ?, ?, ?, ?, ?)",
#                 senders_data)

#         cursor.execute("SELECT COUNT(*) FROM saved_recipients")
#         if cursor.fetchone()[0] == 0:
#             recipients_data = [
#                 ('Charles Maina', '254700111222', '23456789', 'c.maina@email.com', 'Equity Bank', '2345678901'),
#                 ('Brenda Wanjiru', '254701222333', '34567890', 'bwanjiru@email.net', 'KCB Bank', '1234567890'),
#                 ('David Koech', '254702333444', '45678901', 'dkoech@email.org', 'Co-op Bank', '4567890123')
#             ]
#             cursor.executemany(
#                 "INSERT INTO saved_recipients (name, msisdn, id_number, email, bank_name, bank_account_number) VALUES (?, ?, ?, ?, ?, ?)",
#                 recipients_data)

#         conn.commit()


# # --- Initialize DB ---
# init_db()


# # --- Helper Functions ---
# def get_db_connection():
#     conn = sqlite3.connect(DB_FILE)
#     conn.row_factory = sqlite3.Row
#     return conn


# def get_all_banks():
#     with get_db_connection() as conn:
#         banks = [row[0] for row in conn.execute("SELECT DISTINCT bank FROM accounts ORDER BY bank").fetchall()]
#     return banks


# def get_account_name(account_id):
#     if not account_id: return "Corporate Payroll"
#     if account_id == 'EXTERNAL_BULK': return "Multiple Recipients"
#     with get_db_connection() as conn:
#         details = conn.execute("SELECT name FROM accounts WHERE id = ?", (account_id,)).fetchone()
#     return details['name'] if details else 'Unknown Account'


# def format_currency(amount):
#     if amount is None: amount = 0
#     return f"KES {float(amount):,.2f}"


# def parse_contents(contents, filename):
#     content_type, content_string = contents.split(',')
#     decoded = base64.b64decode(content_string)
#     try:
#         if 'csv' in filename:
#             df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
#         elif 'xls' in filename:
#             df = pd.read_excel(io.BytesIO(decoded))
#         else:
#             return html.Div(['Please upload a CSV or Excel file.'])
#         df.columns = df.columns.str.lower().str.strip()
#         return df
#     except Exception as e:
#         print(e)
#         return html.Div(['There was an error processing this file.'])


# # --- Initialize App ---
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
# app.config.suppress_callback_exceptions = True
# SECURE_PASSPHRASE = "BomaPay2025!"
# server = app.server


# # --- UI Component Creation Functions ---
# def create_processing_animation(step=0, status='processing', message=None):
#     if status == 'failed':
#         return html.Div([
#             html.I(className="fas fa-times-circle fa-4x text-danger"),
#             html.H4("Transaction Failed", className="mt-3 text-danger"),
#             html.P(message, className="text-muted mt-2")
#         ], className="text-center p-4")

#     animation_steps = [
#         {"icon": "fa-network-wired", "text": "Contacting Banking Network...", "progress": 20},
#         {"icon": "fa-shield-alt", "text": "Encrypting Transaction Details...", "progress": 40},
#         {"icon": "fa-random", "text": "Authorizing Payment...", "progress": 60},
#         {"icon": "fa-money-bill-wave", "text": "Securely Transferring Funds...", "progress": 80},
#     ]

#     if step < len(animation_steps):
#         current_step = animation_steps[step]
#         return html.Div([
#             html.Div(html.I(className=f"fas {current_step['icon']} fa-beat-fade fa-3x text-primary"),
#                      style={'marginBottom': '20px'}),
#             html.H4(current_step['text'], className="text-primary"),
#             dbc.Progress(value=current_step['progress'], striped=True, animated=True, className="mt-3")
#         ], className="text-center p-4")
#     else:
#         return html.Div([
#             html.I(className="fas fa-check-circle fa-4x text-success"),
#             html.H4("Transaction Successful!", className="mt-3 text-success"),
#             dbc.Progress(value=100, color="success", className="mt-3")
#         ], className="text-center p-4")


# def create_mobile_keypad(pin_value=''):
#     keypad_style = {'width': '60px', 'height': '60px', 'margin': '5px', 'fontSize': '24px', 'borderRadius': '50%',
#                     'border': '2px solid #007bff', 'backgroundColor': '#f8f9fa'}
#     pin_display_text = '●' * len(pin_value) + '○' * (4 - len(pin_value))
#     is_confirm_disabled = len(pin_value) != 4
#     rows = [
#         [dbc.Button(str(i), id={'type': 'keypad-btn', 'index': str(i)}, style=keypad_style, color="outline-primary") for
#          i in range(j, j + 3)] for j in range(1, 10, 3)]
#     rows.append([
#         dbc.Button(html.I(className="fas fa-backspace"), id={'type': 'keypad-btn', 'index': 'del'}, style=keypad_style,
#                    color="outline-danger"),
#         dbc.Button("0", id={'type': 'keypad-btn', 'index': '0'}, style=keypad_style, color="outline-primary"),
#         dbc.Button(html.I(className="fas fa-check"), id={'type': 'keypad-btn', 'index': 'confirm'}, style=keypad_style,
#                    color="success" if not is_confirm_disabled else "secondary", disabled=is_confirm_disabled)
#     ])
#     return html.Div([
#         html.H4("🔐 Enter Your Authorization PIN", className="text-center mb-4"),
#         html.Div(pin_display_text, style={'fontSize': '32px', 'letterSpacing': '10px'},
#                  className="text-center mb-4 font-monospace text-primary"),
#         html.Div([dbc.Row([dbc.Col(btn) for btn in row], className="justify-content-center mb-2") for row in rows],
#                  style={'maxWidth': '280px', 'margin': '0 auto'})
#     ])


# def create_transfer_form():
#     with get_db_connection() as conn:
#         senders = conn.execute("SELECT id, name FROM saved_senders ORDER BY name").fetchall()
#         recipients = conn.execute("SELECT id, name FROM saved_recipients ORDER BY name").fetchall()
#     sender_options = [{'label': s['name'], 'value': s['id']} for s in senders]
#     recipient_options = [{'label': r['name'], 'value': r['id']} for r in recipients]

#     return html.Div([
#         html.H2("💸 Account-to-Account Transfer", className="text-center text-primary fw-bold mb-4"),
#         dbc.Row([
#             dbc.Col(dbc.Card(dbc.CardBody([
#                 html.H5("Source Account Details"),
#                 dcc.Dropdown(id='load-sender-dropdown', options=sender_options, placeholder="Load Saved Sender",
#                              className="mb-3"),
#                 dbc.Row([
#                     dbc.Col(dbc.Input(id='senderBankName-input', placeholder="Sender's Bank Name")),
#                     dbc.Col(dbc.Input(id='senderAccountNum-input', placeholder="Sender's Account Number")),
#                 ], className="mb-3"),
#                 dbc.Row([
#                     dbc.Col(dbc.Input(id='senderName-input', placeholder="Sender's Full Name")),
#                     dbc.Col(dbc.Input(id='senderMSISDN-input', placeholder="Sender's Phone")),
#                 ], className="mb-3"),
#                 dbc.Row([
#                     dbc.Col(dbc.Input(id='senderIDNumber-input', placeholder="Sender's ID Number")),
#                     dbc.Col(dbc.Input(id='senderEmail-input', placeholder="Sender's Email (optional)")),
#                 ], className="mb-3"),
#                 dbc.Checkbox(id='save-sender-checkbox', label="Save my details for next time"),
#             ]), style={'backgroundColor': '#E3F2FD'}), width=6),

#             dbc.Col(dbc.Card(dbc.CardBody([
#                 html.H5("Destination Account Details"),
#                 dcc.Dropdown(id='load-recipient-dropdown', options=recipient_options,
#                              placeholder="Load Saved Recipient", className="mb-3"),
#                 dbc.Row([
#                     dbc.Col(dbc.Input(id='clientBankName-input', placeholder="Recipient's Bank Name")),
#                     dbc.Col(dbc.Input(id='clientAccountNum-input', placeholder="Recipient's Account Number")),
#                 ], className="mb-3"),
#                 dbc.Row([
#                     dbc.Col(dbc.Input(id='clientName-input', placeholder="Recipient's Full Name (clientName)")),
#                     dbc.Col(dbc.Input(id='clientMSISDN-input', placeholder="Recipient's Phone (clientMSISDN)")),
#                 ], className="mb-3"),
#                 dbc.Row([
#                     dbc.Col(dbc.Input(id='clientIDNumber-input',
#                                       placeholder="Recipient's ID Number (clientIDNumber)")),
#                     dbc.Col(
#                         dbc.Input(id='clientEmail-input', placeholder="Recipient's Email (clientEmail, optional)")),
#                 ], className="mb-3"),
#                 dbc.Checkbox(id='save-recipient-checkbox', label="Save this recipient for next time"),
#             ]), style={'backgroundColor': '#E8F5E9'}), width=6),
#         ], className="mb-4"),

#         dbc.Card(dbc.CardBody([
#             html.H5("Transaction Details"),
#             dbc.Row([
#                 dbc.Col(dbc.Input(id="amountExpected-input", type="number", min=1,
#                                   placeholder="Amount (amountExpected)")),
#                 dbc.Col(dbc.Input(id="billDesc-input", placeholder="Narration (billDesc)")),
#             ])
#         ]), className="mb-4"),

#         html.Div([
#             dbc.Button([html.I(className="fas fa-rocket me-2"), "Execute Transfer"], id="execute-transfer-btn",
#                        color="primary", size="lg", disabled=True, className="w-100"),
#             dbc.Popover(
#                 [
#                     dbc.PopoverHeader("Confirm Action"),
#                     dbc.PopoverBody([
#                         html.P("Please validate all details before proceeding."),
#                         dbc.Button("Confirm & Continue", id="confirm-transfer-popover-btn", color="success", size="sm")
#                     ]),
#                 ],
#                 id="transfer-popover",
#                 target="execute-transfer-btn",
#                 trigger="click",
#                 placement="top",
#             )
#         ])
#     ])


# def create_payroll_section():
#     with get_db_connection() as conn:
#         employee_options = [{'label': row['name'], 'value': row['id']} for row in
#                             conn.execute("SELECT id, name FROM master_employees ORDER BY name ASC").fetchall()]
#     return html.Div([
#         dcc.Store(id='payroll-mode-store', data='select'),
#         dcc.Store(id='bank-selection-store'),
#         html.H2("💼 Bulk Payroll Management", className="text-center text-primary fw-bold mb-4"),
#         dbc.Card([
#             dbc.CardHeader(html.H5("1. Load Employee Data")),
#             dbc.CardBody([
#                 html.Div([
#                     dbc.Button("Select from List", id="btn-mode-select", color="primary"),
#                     dbc.Button("Upload File", id="btn-mode-upload", color="secondary"),
#                     dbc.Button("Manual Entry", id="btn-mode-manual", color="secondary"),
#                 ], className="d-flex flex-wrap gap-2 mb-3"),
#                 html.Div(dcc.Dropdown(id='employee-selection-dropdown', options=employee_options, multi=True),
#                          id='payroll-input-select'),
#                 html.Div([
#                     dcc.Upload(id='upload-payroll-data',
#                                children=html.Div(['Drag & Drop or ', html.A('Select Excel/CSV File')]),
#                                style={'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px',
#                                       'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center'}),
#                     html.Small(
#                         "File must contain 'clientName', 'clientMSISDN', 'clientIDNumber', 'amountExpected', and 'billDesc' columns.",
#                         className="text-muted")
#                 ], id='payroll-input-upload', style={'display': 'none'}),
#                 html.Div(dbc.Button([html.I(className="fas fa-plus me-2"), "Add New Row"], id='add-payroll-row-btn',
#                                     color='primary', outline=True, className="w-100"), id='payroll-input-manual',
#                          style={'display': 'none'}),
#             ])
#         ]),
#         dbc.Card([
#             dbc.CardHeader(html.H5("2. Review and Process Payroll Batch")),
#             dbc.CardBody([
#                 dash_table.DataTable(id='payroll-table',
#                                      columns=[
#                                          {"name": "Name (clientName)", "id": "clientName"},
#                                          {"name": "Phone (clientMSISDN)", "id": "clientMSISDN"},
#                                          {"name": "ID No (clientIDNumber)", "id": "clientIDNumber"},
#                                          {"name": "Amount (amountExpected)", "id": "amountExpected", "type": "numeric",
#                                           "format": {'specifier': ',.2f'}},
#                                          {"name": "Narration (billDesc)", "id": "billDesc"}
#                                      ],
#                                      data=[], row_deletable=True, style_cell={'textAlign': 'left', 'padding': '10px'},
#                                      style_header={'backgroundColor': '#e9ecef', 'fontWeight': 'bold'},
#                                      ),
#                 html.Div(id="payroll-summary", className="text-end fw-bold mt-3 border-top pt-3 fs-5"),
#             ])
#         ], className="mt-4"),
#         html.Div([
#             dbc.Button([html.I(className="fas fa-rocket me-2"), "Process Bulk Payroll"], id="process-payroll-btn",
#                        color="success", size="lg", className="w-100", disabled=True),
#             dbc.Popover(
#                 [
#                     dbc.PopoverHeader("Confirm Action"),
#                     dbc.PopoverBody([
#                         html.P(
#                             "You are about to process payroll for multiple employees. Please ensure the list is correct."),
#                         dbc.Button("Confirm & Continue", id="confirm-payroll-popover-btn", color="success", size="sm")
#                     ]),
#                 ],
#                 id="payroll-popover",
#                 target="process-payroll-btn",
#                 trigger="click",
#                 placement="top",
#             ),
#         ], className="mt-4")
#     ])


# def create_header():
#     with get_db_connection() as conn:
#         total_volume_query = "SELECT SUM(amount) FROM transactions WHERE status='completed'"
#         total_volume = conn.execute(total_volume_query).fetchone()[0] or 0
#     return dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(dbc.Row([
#         dbc.Col(
#             [html.H1("Boma Money Transfer"), html.P("Where Everyone Belongs", className="text-muted")],
#             width=8),
#         dbc.Col(html.Div([html.Small("Total Network Volume"), html.H2(format_currency(total_volume))],
#                          className="text-end"), width=4)
#     ])), className="mb-4")))


# def create_navigation():
#     return dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(dbc.ButtonGroup([
#         dbc.Button([html.I(className="fas fa-exchange-alt me-2"), "Account Transfer"], id="btn-transfer",
#                    className="me-2"),
#         dbc.Button([html.I(className="fas fa-users me-2"), "Bulk Transfers/Payroll"], id="btn-payroll",
#                    className="me-2"),
#         dbc.Button([html.I(className="fas fa-credit-card me-2"), "Transactions"], id="btn-transactions",
#                    className="me-2"),
#         dbc.Button([html.I(className="fas fa-building me-2"), "Network Dashboard"], id="btn-dashboard",
#                    className="me-2"),
#         dbc.Button([html.I(className="fas fa-chart-pie me-2"), "Analytics"], id="btn-analytics")
#     ]))), className="mb-4"))


# def create_analytics_view():
#     return html.Div([
#         dbc.Row(id="kpi-cards", className="mb-4"),
#         dbc.Row([
#             dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='payroll-by-dept-chart')])), width=6),
#             dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='transfer-dist-chart')])), width=6),
#         ], className="mb-4"),
#         dbc.Row([
#             dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='monthly-trends-chart')])), width=7),
#             dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='top-transfer-banks-chart')])), width=5),
#         ], className="mb-4")
#     ])


# def create_transactions_view():
#     return html.Div([
#         html.H2("📊 Transaction History", className="text-primary fw-bold mb-4"),
#         dbc.Tabs([
#             dbc.Tab(html.Div(id='all-transactions-content',
#                              children=[dbc.Spinner(color="primary")]), label="All Transactions"),
#             dbc.Tab(html.Div(id='transfer-transactions-content',
#                              children=[dbc.Spinner(color="primary")]), label="💸 Account Transfers"),
#             dbc.Tab(html.Div(id='payroll-transactions-content',
#                              children=[dbc.Spinner(color="primary")]), label="💼 Bulk Payroll"),
#         ])
#     ])


# def create_dashboard():
#     banks = get_all_banks()
#     today_str = datetime.datetime.now(pytz.timezone('Africa/Nairobi')).strftime('%Y-%m-%d')
#     seven_days_ago_str = (datetime.datetime.now(pytz.timezone('Africa/Nairobi')) - datetime.timedelta(days=7)).strftime(
#         '%Y-%m-%d')

#     with get_db_connection() as conn:
#         num_accounts = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
#         transfers_today = conn.execute(
#             "SELECT COUNT(*) FROM transactions WHERE DATE(timestamp) = ? AND type = 'transfer'",
#             (today_str,)).fetchone()[0]
#         payrolls_today = conn.execute(
#             "SELECT COUNT(*) FROM transactions WHERE DATE(timestamp) = ? AND type = 'payroll'",
#             (today_str,)).fetchone()[0]
#         bank_volumes = conn.execute("""
#             SELECT a.bank, SUM(t.amount) as volume
#             FROM transactions t
#             JOIN accounts a ON t.to_acct = a.id
#             WHERE DATE(t.timestamp) >= ?
#             GROUP BY a.bank
#         """, (seven_days_ago_str,)).fetchall()
#         bank_volume_map = {row['bank']: row['volume'] for row in bank_volumes}

#     bank_cards = []
#     for bank in banks:
#         volume = bank_volume_map.get(bank, 0)
#         card = dbc.Col(dbc.Card([
#             dbc.CardHeader(html.Div([html.I(className="fas fa-university me-2"), html.Span(bank)],
#                                     className="d-flex align-items-center")),
#             dbc.CardBody([
#                 html.P("Active", className="text-success"),
#                 html.H4(format_currency(volume), className="text-info"),
#                 html.Small("7-Day Inbound Volume", className="text-muted")
#             ])
#         ]), md=4, lg=3, className="mb-3")
#         bank_cards.append(card)

#     return dbc.Row([
#         dbc.Col(dbc.Card([dbc.CardHeader(html.H4("Connected Banking Network")), dbc.CardBody(dbc.Row(bank_cards))]),
#                 width=9),
#         dbc.Col(dbc.Card([dbc.CardHeader(html.H5("Quick Stats")), dbc.CardBody([
#             dbc.Row([dbc.Col("Active Accounts"),
#                      dbc.Col(html.Strong(num_accounts, className="text-primary"), width="auto")], className="mb-3"),
#             dbc.Row([dbc.Col("Today's Transfers"),
#                      dbc.Col(html.Strong(transfers_today, className="text-success"), width="auto")],
#                     className="mb-3"),
#             dbc.Row([dbc.Col("Today's Payrolls"),
#                      dbc.Col(html.Strong(payrolls_today, className="text-info"), width="auto")])
#         ])]), width=3)
#     ])


# # --- App Layout ---
# app.layout = dbc.Container([
#     dcc.Store(id='current-view-store', data='transfer'),
#     dcc.Store(id='current-pin-store', data=''),
#     dcc.Store(id='pending-transaction-store', data={}),
#     dcc.Store(id='transaction-refresh-signal', data=None),
#     dcc.Store(id='animation-step-store', data=0),
#     dcc.Interval(id='animation-interval', interval=2000, n_intervals=0, disabled=True),
#     dcc.Interval(id='interval-component', interval=3000, n_intervals=0, disabled=True),

#     dbc.Modal([
#         dbc.ModalHeader(html.H4("🔒 Secure Passphrase Verification")),
#         dbc.ModalBody([
#             html.P("Please review the transaction details below and enter your security passphrase to proceed."),
#             html.Div(id="passphrase-summary-body"),
#             html.Hr(),
#             dbc.Input(id="security-passphrase-input", type="password", placeholder="Enter your secret passphrase"),
#             html.Div(id="passphrase-alert-container", className="mt-2")
#         ]),
#         dbc.ModalFooter([
#             dbc.Button("Cancel", id="passphrase-cancel-btn", color="secondary"),
#             dbc.Button("Submit Passphrase", id="submit-passphrase-btn", color="primary")
#         ])
#     ], id="passphrase-modal", is_open=False, backdrop="static"),

#     dbc.Modal([dbc.ModalHeader("Secure PIN Entry"), dbc.ModalBody(id="pin-entry-body"),
#                dbc.ModalFooter(dbc.Button("Cancel", id="pin-cancel-btn"))], id="pin-modal", is_open=False,
#               backdrop="static"),
#     dbc.Modal(
#         [dbc.ModalBody(id="processing-body"), dbc.ModalFooter(dbc.Button("Close", id="close-processing-modal-btn"))],
#         id="processing-modal", is_open=False, centered=True),

#     html.Div(id='header-container'),
#     create_navigation(),

#     html.Div([
#         html.Div(create_payroll_section(), id='page-payroll', style={'display': 'none'}),
#         html.Div(create_transfer_form(), id='page-transfer'),
#         html.Div(create_transactions_view(), id='page-transactions', style={'display': 'none'}),
#         html.Div(id='page-dashboard', style={'display': 'none'}),
#         html.Div(create_analytics_view(), id='page-analytics', style={'display': 'none'}),
#     ])
# ], className="py-4", style={'maxWidth': '85%', 'backgroundColor': '#f8f9fa'})


# # --- Callbacks ---
# @app.callback(
#     [Output('current-view-store', 'data')] + [Output(f'btn-{view}', 'color') for view in
#                                               ['payroll', 'transfer', 'transactions', 'dashboard', 'analytics']],
#     [Input(f'btn-{view}', 'n_clicks') for view in ['payroll', 'transfer', 'transactions', 'dashboard', 'analytics']]
# )
# def update_active_button(p, t, r, d, a):
#     ctx = callback_context
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'btn-transfer'
#     view_name = button_id.replace('btn-', '')
#     colors = {v: 'outline-primary' for v in ['payroll', 'transfer', 'transactions', 'dashboard', 'analytics']}
#     colors[view_name] = 'primary'
#     return view_name, colors['payroll'], colors['transfer'], colors['transactions'], colors['dashboard'], colors[
#         'analytics']


# @app.callback(
#     [Output(f'page-{view}', 'style') for view in ['payroll', 'transfer', 'transactions', 'dashboard', 'analytics']],
#     Input('current-view-store', 'data')
# )
# def display_page(view_name):
#     styles = {v: {'display': 'none'} for v in ['payroll', 'transfer', 'transactions', 'dashboard', 'analytics']}
#     if view_name in styles:
#         styles[view_name] = {'display': 'block'}
#     return styles['payroll'], styles['transfer'], styles['transactions'], styles['dashboard'], styles['analytics']


# @app.callback(Output('header-container', 'children'),
#               [Input('transaction-refresh-signal', 'data'), Input('current-view-store', 'data')])
# def update_header_live(refresh_signal, view):
#     return create_header()


# @app.callback(
#     Output('all-transactions-content', 'children'),
#     Output('transfer-transactions-content', 'children'),
#     Output('payroll-transactions-content', 'children'),
#     Input('transaction-refresh-signal', 'data'),
#     Input('current-view-store', 'data')
# )
# def update_transaction_tables(refresh_signal, view_name):
#     if view_name != 'transactions':
#         return no_update, no_update, no_update

#     with get_db_connection() as conn:
#         df = pd.read_sql_query("SELECT * FROM transactions ORDER BY timestamp DESC", conn)

#     if df.empty:
#         no_data_msg = html.Div("No transactions found.", className="text-center text-muted p-4")
#         return no_data_msg, no_data_msg, no_data_msg

#     df['from_acct'] = df['from_acct'].apply(get_account_name)
#     df['to_acct'] = df['to_acct'].apply(get_account_name)
#     df['amount'] = df['amount'].apply(format_currency)
#     df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

#     df.rename(columns={
#         'id': 'Reference', 'from_acct': 'From', 'to_acct': 'To', 'amount': 'Amount',
#         'type': 'Type', 'status': 'Status', 'timestamp': 'Timestamp'
#     }, inplace=True)

#     table_style = {
#         'style_cell': {'textAlign': 'left', 'padding': '10px', 'fontFamily': 'sans-serif'},
#         'style_header': {'backgroundColor': '#e9ecef', 'fontWeight': 'bold'},
#         'style_data_conditional': [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
#         'page_size': 10,
#     }

#     all_table = dash_table.DataTable(data=df.to_dict('records'),
#                                      columns=[{'name': i, 'id': i} for i in df.columns if i != 'method'], **table_style)
#     transfer_table = dash_table.DataTable(data=df[df['Type'] == 'transfer'].to_dict('records'),
#                                           columns=[{'name': i, 'id': i} for i in df.columns if i != 'method'],
#                                           **table_style)
#     payroll_table = dash_table.DataTable(data=df[df['Type'] == 'payroll'].to_dict('records'),
#                                          columns=[{'name': i, 'id': i} for i in df.columns if i != 'method'],
#                                          **table_style)

#     return all_table, transfer_table, payroll_table


# @app.callback(
#     Output('page-dashboard', 'children'),
#     Input('transaction-refresh-signal', 'data'),
#     Input('current-view-store', 'data')
# )
# def update_dashboard(refresh_signal, view_name):
#     if view_name == 'dashboard':
#         return create_dashboard()
#     return no_update


# @app.callback(
#     Output('kpi-cards', 'children'),
#     Output('payroll-by-dept-chart', 'figure'),
#     Output('transfer-dist-chart', 'figure'),
#     Output('monthly-trends-chart', 'figure'),
#     Output('top-transfer-banks-chart', 'figure'),
#     Input('current-view-store', 'data'),
#     prevent_initial_call=True
# )
# def update_analytics_page(view_name):
#     if view_name != 'analytics':
#         return no_update, no_update, no_update, no_update, no_update

#     with get_db_connection() as conn:
#         total_volume = conn.execute("SELECT SUM(amount) FROM transactions WHERE status='completed'").fetchone()[0] or 0
#         total_transactions = conn.execute("SELECT COUNT(*) FROM transactions WHERE status='completed'").fetchone()[
#                                  0] or 0
#         avg_transfer = \
#         conn.execute("SELECT AVG(amount) FROM transactions WHERE status='completed' AND type='transfer'").fetchone()[
#             0] or 0
#         df_payroll = pd.read_sql_query(
#             "SELECT department, SUM(amount) as total_payroll FROM master_employees GROUP BY department", conn)
#         df_trans = pd.read_sql_query("SELECT amount FROM transactions WHERE status='completed'", conn)
#         df_trends = pd.read_sql_query(
#             "SELECT STRFTIME('%Y-%m', timestamp) as month, SUM(amount) as volume FROM transactions WHERE status='completed' GROUP BY month ORDER BY month ASC",
#             conn)
#         df_banks = pd.read_sql_query("""
#             SELECT a.bank, SUM(t.amount) as volume
#             FROM transactions t JOIN accounts a ON t.to_acct = a.id
#             WHERE t.status='completed'
#             GROUP BY a.bank ORDER BY volume DESC LIMIT 5
#         """, conn)

#     kpi_cards = [
#         dbc.Col(dbc.Card(
#             dbc.CardBody([html.H4(format_currency(total_volume)), html.P("Total Volume", className="text-muted")])),
#                 width=4),
#         dbc.Col(dbc.Card(
#             dbc.CardBody([html.H4(f"{total_transactions:,}"), html.P("Total Transactions", className="text-muted")])),
#                 width=4),
#         dbc.Col(dbc.Card(dbc.CardBody(
#             [html.H4(format_currency(avg_transfer)), html.P("Avg. Transfer Amount", className="text-muted")])),
#                 width=4),
#     ]

#     fig_payroll = px.bar(df_payroll, x='department', y='total_payroll', title="Payroll Costs by Department",
#                          labels={'department': 'Department', 'total_payroll': 'Total Payroll Amount'})
#     fig_payroll.update_layout(title_x=0.5)

#     bins = [0, 10000, 50000, 100000, float('inf')]
#     labels = ['< 10k', '10k - 50k', '50k - 100k', '> 100k']
#     df_trans['range'] = pd.cut(df_trans['amount'], bins=bins, labels=labels, right=False)
#     dist_data = df_trans['range'].value_counts().reset_index()
#     dist_data.columns = ['range', 'count']
#     fig_dist = px.pie(dist_data, names='range', values='count', title="Distribution of Transaction Sizes", hole=.3)
#     fig_dist.update_layout(title_x=0.5)

#     fig_trends = px.line(df_trends, x='month', y='volume', title="Monthly Transaction Volume", markers=True,
#                          labels={'month': 'Month', 'volume': 'Transaction Volume'})
#     fig_trends.update_layout(title_x=0.5)

#     fig_banks = px.bar(df_banks, x='bank', y='volume', title="Top 5 Banks by Inbound Volume",
#                        labels={'bank': 'Bank', 'volume': 'Inbound Volume'})
#     fig_banks.update_layout(title_x=0.5)

#     return kpi_cards, fig_payroll, fig_dist, fig_trends, fig_banks


# # --- NEW --- Callback to populate the payroll table when employees are selected
# @app.callback(
#     Output('payroll-table', 'data'),
#     Input('employee-selection-dropdown', 'value')
# )
# def update_payroll_table(employee_ids):
#     if not employee_ids:
#         return []

#     # Create a string of question marks for the SQL query
#     placeholders = ','.join(['?'] * len(employee_ids))
#     query = f"""
#         SELECT 
#             name AS clientName, 
#             account AS clientMSISDN, 
#             'N/A' AS clientIDNumber, 
#             amount AS amountExpected, 
#             'Monthly Salary' AS billDesc 
#         FROM master_employees 
#         WHERE id IN ({placeholders})
#     """
#     with get_db_connection() as conn:
#         df = pd.read_sql_query(query, conn, params=employee_ids)

#     return df.to_dict('records')


# # --- NEW --- Callback to enable/disable the process payroll button
# @app.callback(
#     Output('process-payroll-btn', 'disabled'),
#     Input('payroll-table', 'data')
# )
# def toggle_process_payroll_button(data):
#     return not data


# @app.callback(
#     [Output('senderName-input', 'value'), Output('senderMSISDN-input', 'value'),
#      Output('senderIDNumber-input', 'value'), Output('senderEmail-input', 'value'),
#      Output('senderBankName-input', 'value'), Output('senderAccountNum-input', 'value')],
#     Input('load-sender-dropdown', 'value'),
#     prevent_initial_call=True
# )
# def load_saved_sender(sender_id):
#     if not sender_id:
#         return "", "", "", "", "", ""
#     with get_db_connection() as conn:
#         sender = conn.execute("SELECT * FROM saved_senders WHERE id = ?", (sender_id,)).fetchone()
#     if sender:
#         return sender['name'], sender['msisdn'], sender['id_number'], sender['email'], sender['bank_name'], sender[
#             'bank_account_number']
#     return [no_update] * 6


# @app.callback(
#     [Output('clientName-input', 'value'), Output('clientMSISDN-input', 'value'),
#      Output('clientIDNumber-input', 'value'), Output('clientEmail-input', 'value'),
#      Output('clientBankName-input', 'value'), Output('clientAccountNum-input', 'value')],
#     Input('load-recipient-dropdown', 'value'),
#     prevent_initial_call=True
# )
# def load_saved_recipient(recipient_id):
#     if not recipient_id:
#         return "", "", "", "", "", ""
#     with get_db_connection() as conn:
#         recipient = conn.execute("SELECT * FROM saved_recipients WHERE id = ?", (recipient_id,)).fetchone()
#     if recipient:
#         return recipient['name'], recipient['msisdn'], recipient['id_number'], recipient['email'], recipient[
#             'bank_name'], recipient['bank_account_number']
#     return [no_update] * 6


# @app.callback(
#     Output('execute-transfer-btn', 'disabled'),
#     [Input('senderName-input', 'value'), Input('senderAccountNum-input', 'value'),
#      Input('clientName-input', 'value'), Input('clientAccountNum-input', 'value'),
#      Input('amountExpected-input', 'value')]
# )
# def toggle_execute_button(s_name, s_acct, r_name, r_acct, amount):
#     return not all([s_name, s_acct, r_name, r_acct, amount])


# # --- MODIFIED --- This callback now handles the payroll confirmation workflow
# @app.callback(
#     [Output('passphrase-modal', 'is_open'), Output('passphrase-summary-body', 'children'),
#      Output('pending-transaction-store', 'data'),
#      Output('transfer-popover', 'is_open'), Output('payroll-popover', 'is_open'),
#      Output('load-sender-dropdown', 'options'), Output('load-recipient-dropdown', 'options')],
#     [Input('confirm-transfer-popover-btn', 'n_clicks'), Input('confirm-payroll-popover-btn', 'n_clicks')],
#     [State('senderName-input', 'value'), State('senderMSISDN-input', 'value'),
#      State('senderIDNumber-input', 'value'), State('senderEmail-input', 'value'),
#      State('senderBankName-input', 'value'), State('senderAccountNum-input', 'value'),
#      State('save-sender-checkbox', 'value'),
#      State('clientName-input', 'value'), State('clientMSISDN-input', 'value'),
#      State('clientIDNumber-input', 'value'), State('clientEmail-input', 'value'),
#      State('clientBankName-input', 'value'), State('clientAccountNum-input', 'value'),
#      State('save-recipient-checkbox', 'value'),
#      State('amountExpected-input', 'value'), State('billDesc-input', 'value'),
#      State('payroll-table', 'data')],
#     prevent_initial_call=True
# )
# def handle_confirmation(t_clicks, p_clicks, s_name, s_msisdn, s_id, s_email, s_bank, s_acct, save_sender,
#                         r_name, r_msisdn, r_id, r_email, r_bank, r_acct, save_recipient, amount, desc, p_data):
#     trig_id = callback_context.triggered_id
#     sender_options, recipient_options = no_update, no_update

#     with get_db_connection() as conn:
#         if save_sender and s_name:
#             conn.execute(
#                 "INSERT OR REPLACE INTO saved_senders (name, msisdn, id_number, email, bank_name, bank_account_number) VALUES (?, ?, ?, ?, ?, ?)",
#                 (s_name, s_msisdn, s_id, s_email, s_bank, s_acct))
#             conn.commit()
#             senders = conn.execute("SELECT id, name FROM saved_senders ORDER BY name").fetchall()
#             sender_options = [{'label': s['name'], 'value': s['id']} for s in senders]

#         if save_recipient and r_name:
#             conn.execute(
#                 "INSERT OR REPLACE INTO saved_recipients (name, msisdn, id_number, email, bank_name, bank_account_number) VALUES (?, ?, ?, ?, ?, ?)",
#                 (r_name, r_msisdn, r_id, r_email, r_bank, r_acct))
#             conn.commit()
#             recipients = conn.execute("SELECT id, name FROM saved_recipients ORDER BY name").fetchall()
#             recipient_options = [{'label': r['name'], 'value': r['id']} for r in recipients]

#     if trig_id == 'confirm-transfer-popover-btn':
#         ref = f'INV-{uuid.uuid4().hex[:8].upper()}'
#         data = {'type': 'transfer', 'payload': {
#             'senderName': s_name, 'senderAccount': s_acct, 'senderBank': s_bank,
#             'clientName': r_name, 'clientAccount': r_acct, 'clientBank': r_bank, 'clientMSISDN': r_msisdn,
#             'amountExpected': float(amount), 'billRefNumber': ref, 'billDesc': desc
#         }}
#         summary_list = dbc.ListGroup([
#             dbc.ListGroupItem(f"Debiting From: {s_name} ({s_bank})", className="text-danger fw-bold"),
#             dbc.ListGroupItem(f"Account Number: {s_acct}"),
#             html.Hr(),
#             dbc.ListGroupItem(f"Recipient: {r_name} ({r_acct})"),
#             dbc.ListGroupItem(f"Recipient Bank: {r_bank}"),
#             dbc.ListGroupItem(f"Bill Reference: {ref}"),
#             dbc.ListGroupItem(f"Amount: {format_currency(amount)}", color="primary", className="fw-bold"),
#         ], flush=True, className="mb-3")
#         return True, summary_list, data, False, False, sender_options, recipient_options

#     elif trig_id == 'confirm-payroll-popover-btn':
#         if not p_data:
#             return no_update, no_update, no_update, False, False, sender_options, recipient_options

#         total_amount = sum(float(row.get('amountExpected', 0)) for row in p_data)
#         num_employees = len(p_data)
#         ref = f'PAYROLL-{uuid.uuid4().hex[:6].upper()}'
#         data = {'type': 'payroll', 'amount': total_amount, 'ref': ref}

#         summary_list = dbc.ListGroup([
#             dbc.ListGroupItem(f"Processing payroll for {num_employees} employees.", className="text-info fw-bold"),
#             dbc.ListGroupItem(f"Batch Reference: {ref}"),
#             dbc.ListGroupItem(f"Total Amount: {format_currency(total_amount)}", color="primary", className="fw-bold"),
#         ], flush=True, className="mb-3")

#         return True, summary_list, data, False, False, sender_options, recipient_options

#     return no_update, no_update, no_update, False, False, sender_options, recipient_options


# @app.callback(
#     [Output('pin-modal', 'is_open'),
#      Output('passphrase-modal', 'is_open', allow_duplicate=True),
#      Output('passphrase-alert-container', 'children'),
#      Output('current-pin-store', 'data', allow_duplicate=True),
#      Output('pin-entry-body', 'children', allow_duplicate=True)],
#     [Input('submit-passphrase-btn', 'n_clicks'), Input('passphrase-cancel-btn', 'n_clicks')],
#     [State('security-passphrase-input', 'value')],
#     prevent_initial_call=True
# )
# def handle_passphrase_submission(submit_clicks, cancel_clicks, passphrase):
#     trig_id = callback_context.triggered_id
#     if trig_id == 'passphrase-cancel-btn':
#         return False, False, None, no_update, no_update

#     if passphrase == SECURE_PASSPHRASE:
#         return True, False, None, '', create_mobile_keypad('')
#     else:
#         alert = dbc.Alert("Invalid Passphrase. Please try again.", color="danger", dismissable=True, duration=4000)
#         return False, True, alert, no_update, no_update


# @app.callback(
#     [Output('processing-modal', 'is_open'), Output('processing-body', 'children'),
#      Output('pin-modal', 'is_open', allow_duplicate=True),
#      Output('current-pin-store', 'data', allow_duplicate=True), Output('transaction-refresh-signal', 'data'),
#      Output('interval-component', 'disabled', allow_duplicate=True),
#      Output('animation-interval', 'disabled', allow_duplicate=True),
#      Output('animation-step-store', 'data', allow_duplicate=True)],
#     Input('current-pin-store', 'data'),
#     State('pending-transaction-store', 'data'),
#     prevent_initial_call=True
# )
# def process_payment(pin, data):
#     if not pin or len(pin) != 4:
#         return [no_update] * 8

#     if pin != '1234':
#         body = create_processing_animation(status='failed', message="Invalid PIN.")
#         return True, body, False, '', no_update, True, True, 0

#     is_success, msg = False, ""
#     try:
#         with get_db_connection() as conn:
#             cursor = conn.cursor()
#             if data['type'] == 'transfer':
#                 payload = data['payload']
#                 amount = payload['amountExpected']
#                 sender_acct = cursor.execute("SELECT id, balance FROM accounts WHERE accountNumber = ?",
#                                              (payload['senderAccount'],)).fetchone()
#                 if not sender_acct:
#                     raise ValueError(f"Sender account {payload['senderAccount']} not found in the network.")

#                 if sender_acct['balance'] < amount:
#                     raise ValueError("Insufficient funds in the sender's account.")

#                 receiver_acct = cursor.execute("SELECT id FROM accounts WHERE accountNumber = ?",
#                                                (payload['clientAccount'],)).fetchone()
#                 if not receiver_acct:
#                     raise ValueError(f"Recipient account {payload['clientAccount']} not found in the network.")

#                 cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, sender_acct['id']))
#                 cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, receiver_acct['id']))
#                 cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
#                     payload['billRefNumber'], sender_acct['id'], receiver_acct['id'], amount, 'transfer', 'completed',
#                     datetime.datetime.now(pytz.timezone('Africa/Nairobi')).isoformat(), 'A2A-INTERNAL'))

#             elif data['type'] == 'payroll':
#                 amount = data['amount']
#                 ref = data['ref']
#                 from_acct = 'acc003'  # Corporate Account ID
#                 bal = cursor.execute("SELECT balance FROM accounts WHERE id = ?", (from_acct,)).fetchone()[0]
#                 if bal < amount: raise ValueError("Insufficient corporate funds for payroll.")
#                 cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_acct))
#                 cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
#                     ref, from_acct, 'EXTERNAL_BULK', amount, 'payroll',
#                     'completed',
#                     datetime.datetime.now(pytz.timezone('Africa/Nairobi')).isoformat(), 'API-Bulk'))

#             conn.commit()
#             is_success = True
#     except (sqlite3.Error, ValueError, TypeError, IndexError) as e:
#         msg = str(e)

#     if is_success:
#         initial_body = create_processing_animation(step=0)
#         return True, initial_body, False, '', datetime.datetime.now().isoformat(), True, False, 0
#     else:
#         fail_body = create_processing_animation(status='failed', message=msg)
#         return True, fail_body, False, '', no_update, True, True, 0


# @app.callback(
#     Output('processing-body', 'children', allow_duplicate=True),
#     Output('animation-step-store', 'data', allow_duplicate=True),
#     Output('animation-interval', 'disabled', allow_duplicate=True),
#     Output('interval-component', 'disabled', allow_duplicate=True),
#     Output('transaction-refresh-signal', 'data', allow_duplicate=True),
#     Input('animation-interval', 'n_intervals'),
#     State('animation-step-store', 'data'),
#     prevent_initial_call=True
# )
# def update_animation_step(n, current_step):
#     if n == 0:
#         return [no_update] * 5

#     next_step = current_step + 1
#     number_of_animation_steps = 4

#     if next_step <= number_of_animation_steps:
#         new_body = create_processing_animation(step=next_step)
#         is_animation_disabled = next_step == number_of_animation_steps
#         close_interval_disabled = not is_animation_disabled
#         refresh_signal = datetime.datetime.now().isoformat() if is_animation_disabled else no_update
#         return new_body, next_step, is_animation_disabled, close_interval_disabled, refresh_signal

#     return [no_update] * 5


# @app.callback(
#     [Output('pin-modal', 'is_open', allow_duplicate=True), Output('current-pin-store', 'data', allow_duplicate=True),
#      Output('pin-entry-body', 'children', allow_duplicate=True)],
#     [Input('pin-cancel-btn', 'n_clicks'), Input({'type': 'keypad-btn', 'index': ALL}, 'n_clicks')],
#     [State('current-pin-store', 'data')], prevent_initial_call=True
# )
# def handle_pin_modal(canc, keys, pin):
#     ctx = callback_context
#     trig_id = ctx.triggered_id

#     if trig_id == 'pin-cancel-btn':
#         return False, '', no_update

#     if not isinstance(trig_id, dict):
#         return no_update, no_update, no_update

#     index = trig_id['index']
#     new_pin = pin or ""

#     if index == 'del':
#         new_pin = new_pin[:-1]
#     elif index == 'confirm':
#         return False, new_pin, no_update
#     elif len(new_pin) < 4:
#         new_pin += index

#     return True, new_pin, create_mobile_keypad(new_pin)


# @app.callback(Output('processing-modal', 'is_open', allow_duplicate=True), Input('interval-component', 'n_intervals'),
#               prevent_initial_call=True)
# def auto_close_processing_modal(n): return False


# @app.callback([Output('processing-modal', 'is_open', allow_duplicate=True),
#                Output('interval-component', 'disabled', allow_duplicate=True)],
#               Input('close-processing-modal-btn', 'n_clicks'), prevent_initial_call=True)
# def manual_close_processing_modal(n): return False, True


# if __name__ == '__main__':
#     app.run(debug=True, port=6639)




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
        # Core Tables
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS accounts (id TEXT PRIMARY KEY, name TEXT NOT NULL, bank TEXT NOT NULL, accountNumber TEXT NOT NULL UNIQUE, balance REAL NOT NULL, type TEXT NOT NULL)''')
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS transactions (id TEXT PRIMARY KEY, from_acct TEXT, to_acct TEXT, amount REAL NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, timestamp TEXT NOT NULL, method TEXT)''')
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS master_employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, bank TEXT NOT NULL, account TEXT NOT NULL, amount REAL NOT NULL, department TEXT NOT NULL)''')
        # Tables for saving user and recipient details
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS saved_senders (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, msisdn TEXT, id_number TEXT, email TEXT, bank_name TEXT, bank_account_number TEXT)''')
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS saved_recipients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, msisdn TEXT, id_number TEXT, email TEXT, bank_name TEXT, bank_account_number TEXT)''')

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

        cursor.execute("SELECT COUNT(*) FROM master_employees")
        if cursor.fetchone()[0] == 0:
            master_employee_data = [('John Doe', 'KCB Bank', '1234567890', 50000, 'Sales'),
                                    ('Sarah Wilson', 'Equity Bank', '2345678901', 45000, 'Marketing'),
                                    ('Mohamed Hassan', 'Nile Commercial Bank', '5678901234', 60000, 'Engineering')]
            cursor.executemany(
                "INSERT INTO master_employees (name, bank, account, amount, department) VALUES (?, ?, ?, ?, ?)",
                master_employee_data)

        # Add some transactions for better analytics visualization if table is empty
        cursor.execute("SELECT COUNT(*) FROM transactions")
        if cursor.fetchone()[0] == 0:
            # Get current time
            now = datetime.datetime.now(pytz.timezone('Africa/Nairobi'))
            transactions_data = [
                (f'INV-{uuid.uuid4().hex[:8].upper()}', 'acc003', 'acc001', 5000, 'transfer', 'completed',
                 (now - datetime.timedelta(days=40)).isoformat(), 'A2A'),
                (f'INV-{uuid.uuid4().hex[:8].upper()}', 'acc003', 'acc002', 7500, 'transfer', 'completed',
                 (now - datetime.timedelta(days=35)).isoformat(), 'A2A'),
                (f'PAYROLL-{uuid.uuid4().hex[:6].upper()}', 'acc003', 'EXTERNAL_BULK', 115000, 'payroll', 'completed',
                 (now - datetime.timedelta(days=30)).isoformat(), 'API-Bulk'),
                (f'INV-{uuid.uuid4().hex[:8].upper()}', 'acc004', 'acc005', 12000, 'transfer', 'completed',
                 (now - datetime.timedelta(days=25)).isoformat(), 'A2A'),
                (f'INV-{uuid.uuid4().hex[:8].upper()}', 'acc003', 'acc006', 8200, 'transfer', 'completed',
                 (now - datetime.timedelta(days=15)).isoformat(), 'A2A'),
                (f'PAYROLL-{uuid.uuid4().hex[:6].upper()}', 'acc003', 'EXTERNAL_BULK', 125000, 'payroll', 'completed',
                 (now - datetime.timedelta(days=1)).isoformat(), 'API-Bulk'),
                (f'INV-{uuid.uuid4().hex[:8].upper()}', 'acc003', 'acc009', 25000, 'transfer', 'completed',
                 (now - datetime.timedelta(hours=5)).isoformat(), 'A2A'),
            ]
            cursor.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", transactions_data)

        cursor.execute("SELECT COUNT(*) FROM saved_senders")
        if cursor.fetchone()[0] == 0:
            senders_data = [
                ('Alice Mwangi', '254722123456', '12345678', 'alice.m@capitalpay.corp', 'Stanbic Bank', '3456789012'),
                ('Bob Otieno', '254711987654', '87654321', 'bob.o@capitalpay.corp', 'Stanbic Bank', '3456789012')
            ]
            cursor.executemany(
                "INSERT INTO saved_senders (name, msisdn, id_number, email, bank_name, bank_account_number) VALUES (?, ?, ?, ?, ?, ?)",
                senders_data)

        cursor.execute("SELECT COUNT(*) FROM saved_recipients")
        if cursor.fetchone()[0] == 0:
            recipients_data = [
                ('Charles Maina', '254700111222', '23456789', 'c.maina@email.com', 'Equity Bank', '2345678901'),
                ('Brenda Wanjiru', '254701222333', '34567890', 'bwanjiru@email.net', 'KCB Bank', '1234567890'),
                ('David Koech', '254702333444', '45678901', 'dkoech@email.org', 'Co-op Bank', '4567890123')
            ]
            cursor.executemany(
                "INSERT INTO saved_recipients (name, msisdn, id_number, email, bank_name, bank_account_number) VALUES (?, ?, ?, ?, ?, ?)",
                recipients_data)

        conn.commit()


# --- Initialize DB ---
init_db()


# --- Helper Functions ---
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_banks():
    with get_db_connection() as conn:
        banks = [row[0] for row in conn.execute("SELECT DISTINCT bank FROM accounts ORDER BY bank").fetchall()]
    return banks


def get_account_name(account_id):
    if not account_id: return "Corporate Payroll"
    if account_id == 'EXTERNAL_BULK': return "Multiple Recipients"
    with get_db_connection() as conn:
        details = conn.execute("SELECT name FROM accounts WHERE id = ?", (account_id,)).fetchone()
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
SECURE_PASSPHRASE = "Test123"
server = app.server


# --- UI Component Creation Functions ---
def create_processing_animation(step=0, status='processing', message=None):
    if status == 'failed':
        return html.Div([
            html.I(className="fas fa-times-circle fa-4x text-danger mb-3"),
            html.H4("Transaction Failed", className="text-danger"),
            html.P(message, className="text-muted mt-2")
        ], className="text-center p-4")

    animation_steps = [
        {"icon": "fa-network-wired", "text": " Capital Pay Aggregator Engine Contacting Banking Network...", "progress": 20},
        {"icon": "fa-shield-alt", "text": "Encrypting Transaction Details...", "progress": 40},
        {"icon": "fa-random", "text": "Authorizing Payment...", "progress": 60},
        {"icon": "fa-money-bill-wave", "text": "Securely Transferring Funds...", "progress": 80},
    ]

    if step < len(animation_steps):
        current_step = animation_steps[step]
        return html.Div([
            html.Div(html.I(className=f"fas {current_step['icon']} fa-beat-fade fa-3x text-primary"),
                     style={'marginBottom': '20px'}),
            html.H4(current_step['text'], className="text-primary"),
            dbc.Progress(value=current_step['progress'], striped=True, animated=True, className="mt-3")
        ], className="text-center p-4")
    else:
        return html.Div([
            html.I(className="fas fa-check-circle fa-4x text-success mb-3"),
            html.H4("Transaction Successful!", className="text-success"),
            dbc.Progress(value=100, color="success", className="mt-3")
        ], className="text-center p-4")


def create_mobile_keypad(pin_value=''):
    keypad_style = {'width': '60px', 'height': '60px', 'margin': '5px', 'fontSize': '24px', 'borderRadius': '50%'}
    pin_display_text = '●' * len(pin_value) + '○' * (4 - len(pin_value))
    is_confirm_disabled = len(pin_value) != 4
    rows = [
        [dbc.Button(str(i), id={'type': 'keypad-btn', 'index': str(i)}, style=keypad_style, color="light") for i in
         range(j, j + 3)] for j in range(1, 10, 3)]
    rows.append([
        dbc.Button(html.I(className="fas fa-backspace"), id={'type': 'keypad-btn', 'index': 'del'}, style=keypad_style,
                   color="light", className="text-danger"),
        dbc.Button("0", id={'type': 'keypad-btn', 'index': '0'}, style=keypad_style, color="light"),
        dbc.Button(html.I(className="fas fa-check"), id={'type': 'keypad-btn', 'index': 'confirm'}, style=keypad_style,
                   color="success" if not is_confirm_disabled else "secondary", disabled=is_confirm_disabled)
    ])
    return html.Div([
        html.H4("🔐 Authorize with PIN", className="text-center mb-4"),
        html.Div(pin_display_text,
                 style={'fontSize': '32px', 'letterSpacing': '10px', 'fontFamily': 'monospace'},
                 className="text-center mb-4 text-primary"),
        html.Div([dbc.Row([dbc.Col(btn) for btn in row], className="justify-content-center") for row in rows],
                 style={'maxWidth': '280px', 'margin': '0 auto'})
    ])


def create_transfer_form():
    with get_db_connection() as conn:
        senders = conn.execute("SELECT id, name FROM saved_senders ORDER BY name").fetchall()
        recipients = conn.execute("SELECT id, name FROM saved_recipients ORDER BY name").fetchall()
    sender_options = [{'label': s['name'], 'value': s['id']} for s in senders]
    recipient_options = [{'label': r['name'], 'value': r['id']} for r in recipients]

    return html.Div([
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.Div([
                    html.I(className="fas fa-arrow-circle-up me-2 text-danger"),
                    "Source Account Details"
                ], className="form-section-card-header")),
                dbc.CardBody([
                    dbc.Label("Load Saved Sender"),
                    dcc.Dropdown(id='load-sender-dropdown', options=sender_options,
                                 placeholder="Select a saved sender...", className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("Bank Name"),
                                 dbc.Input(id='senderBankName-input', placeholder="e.g., KCB Bank")], width=6),
                        dbc.Col([dbc.Label("Account Number"),
                                 dbc.Input(id='senderAccountNum-input', placeholder="e.g., 1234567890")], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col(
                            [dbc.Label("Full Name"), dbc.Input(id='senderName-input', placeholder="e.g., John Doe")],
                            width=6),
                        dbc.Col([dbc.Label("Phone Number"),
                                 dbc.Input(id='senderMSISDN-input', placeholder="e.g., 2547...")]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("ID Number"),
                                 dbc.Input(id='senderIDNumber-input', placeholder="e.g., 12345678")]),
                        dbc.Col([dbc.Label("Email (Optional)"),
                                 dbc.Input(id='senderEmail-input', placeholder="e.g., john.doe@email.com")]),
                    ], className="mb-3"),
                    dbc.Checkbox(id='save-sender-checkbox', label="Save sender details for next time",
                                 className="mt-2"),
                ])
            ]), lg=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.Div([
                    html.I(className="fas fa-arrow-circle-down me-2 text-success"),
                    "Destination Account Details"
                ], className="form-section-card-header")),
                dbc.CardBody([
                    dbc.Label("Load Saved Recipient"),
                    dcc.Dropdown(id='load-recipient-dropdown', options=recipient_options,
                                 placeholder="Select a saved recipient...", className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("Bank Name"),
                                 dbc.Input(id='clientBankName-input', placeholder="e.g., Equity Bank")], width=6),
                        dbc.Col([dbc.Label("Account Number"),
                                 dbc.Input(id='clientAccountNum-input', placeholder="e.g., 2345678901")], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("Full Name (clientName)"),
                                 dbc.Input(id='clientName-input', placeholder="e.g., Sarah Wilson")], width=6),
                        dbc.Col([dbc.Label("Phone Number (clientMSISDN)"),
                                 dbc.Input(id='clientMSISDN-input', placeholder="e.g., 2547...")]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("ID Number (clientIDNumber)"),
                                 dbc.Input(id='clientIDNumber-input', placeholder="e.g., 87654321")]),
                        dbc.Col([dbc.Label("Email (clientEmail, Optional)"),
                                 dbc.Input(id='clientEmail-input', placeholder="e.g., s.wilson@email.com")]),
                    ], className="mb-3"),
                    dbc.Checkbox(id='save-recipient-checkbox', label="Save this recipient for future use",
                                 className="mt-2"),
                ])
            ]), lg=6)
        ]),
        dbc.Card([
            dbc.CardHeader(html.Div([
                html.I(className="fas fa-file-invoice-dollar me-2 text-primary"),
                "Transaction Details"
            ], className="form-section-card-header")),
            dbc.CardBody(dbc.Row([
                dbc.Col([dbc.Label("Amount (KES)"),
                         dbc.Input(id="amountExpected-input", type="number", min=1, placeholder="e.g., 5000")],
                        width=6),
                dbc.Col([dbc.Label("Narration / Bill Description"),
                         dbc.Input(id="billDesc-input", placeholder="e.g., Payment for Invoice #123")], width=6)
            ]))
        ]),
        html.Div([
            dbc.Button([html.I(className="fas fa-paper-plane me-2"), "Initiate Transfer"], id="execute-transfer-btn",
                       color="primary", size="lg", disabled=True, className="w-100"),
            dbc.Popover(
                [
                    dbc.PopoverHeader("Confirm Transfer"),
                    dbc.PopoverBody([
                        html.P("Please verify all details are correct before proceeding."),
                        dbc.Button("Confirm & Continue", id="confirm-transfer-popover-btn", color="success", size="sm")
                    ]),
                ],
                id="transfer-popover",
                target="execute-transfer-btn",
                trigger="click",
                placement="top",
            )
        ], className="mt-4")
    ])


def create_payroll_section():
    with get_db_connection() as conn:
        employee_options = [{'label': row['name'], 'value': row['id']} for row in
                            conn.execute("SELECT id, name FROM master_employees ORDER BY name ASC").fetchall()]
    return html.Div([
        dcc.Store(id='payroll-mode-store', data='select'),
        dcc.Store(id='bank-selection-store'),
        dbc.Card([
            dbc.CardHeader(html.H5("Step 1: Load Employee Data")),
            dbc.CardBody([
                dbc.RadioItems(
                    id="payroll-mode-radios",
                    className="btn-group w-100 mb-4",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {'label': 'Select from List', 'value': 'select'},
                        {'label': 'Upload File', 'value': 'upload'},
                        {'label': 'Manual Entry', 'value': 'manual'},
                    ],
                    value='select',
                ),
                html.Div(dcc.Dropdown(id='employee-selection-dropdown', options=employee_options, multi=True,
                                      placeholder="Select employees from the master list..."),
                         id='payroll-input-select'),
                html.Div([
                    dcc.Upload(id='upload-payroll-data',
                               children=html.Div(['Drag & Drop or ', html.A('Select Excel/CSV File')]),
                               className="upload-box"),
                    html.Small(
                        "File must contain 'clientName', 'clientMSISDN', 'clientIDNumber', 'amountExpected', and 'billDesc' columns.",
                        className="text-muted d-block mt-2")
                ], id='payroll-input-upload', style={'display': 'none'}),
                html.Div(dbc.Button([html.I(className="fas fa-plus me-2"), "Add New Row"], id='add-payroll-row-btn',
                                    color='primary', outline=True, className="w-100"), id='payroll-input-manual',
                         style={'display': 'none'}),
            ])
        ]),
        dbc.Card([
            dbc.CardHeader(html.H5("Step 2: Review and Process Payroll Batch")),
            dbc.CardBody([
                dash_table.DataTable(
                    id='payroll-table',
                    columns=[
                        {"name": "Name (clientName)", "id": "clientName"},
                        {"name": "Phone (clientMSISDN)", "id": "clientMSISDN"},
                        {"name": "ID No (clientIDNumber)", "id": "clientIDNumber"},
                        {"name": "Amount (amountExpected)", "id": "amountExpected", "type": "numeric",
                         "format": {'specifier': ',.2f'}},
                        {"name": "Narration (billDesc)", "id": "billDesc"}
                    ],
                    data=[],
                    row_deletable=True,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'sans-serif',
                                'border': '1px solid #eee'},
                    style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold',
                                  'borderBottom': '2px solid #dee2e6'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}]
                ),
                html.Div(id="payroll-summary", className="text-end fw-bold mt-3 border-top pt-3 fs-5"),
            ])
        ]),
        html.Div([
            dbc.Button([html.I(className="fas fa-rocket me-2"), "Process Bulk Payroll"], id="process-payroll-btn",
                       color="success", size="lg", className="w-100", disabled=True),
            dbc.Popover(
                [
                    dbc.PopoverHeader("Confirm Payroll Run"),
                    dbc.PopoverBody([
                        html.P("You are about to process payroll for multiple employees. This action is irreversible."),
                        dbc.Button("Confirm & Continue", id="confirm-payroll-popover-btn", color="success", size="sm")
                    ]),
                ],
                id="payroll-popover",
                target="process-payroll-btn",
                trigger="click",
                placement="top",
            ),
        ], className="mt-4")
    ])


def create_header():
    with get_db_connection() as conn:
        total_volume_query = "SELECT SUM(amount) FROM transactions WHERE status='completed'"
        total_volume = conn.execute(total_volume_query).fetchone()[0] or 0
    return dbc.Card(dbc.CardBody(dbc.Row([
        dbc.Col([
            html.Div([
                html.I(className="fas fa-landmark text-primary me-3", style={'fontSize': '2.5rem'}),
                html.Div([
                    html.H1("Boma Money Transfers  - BMT", className="app-title"),
                    html.P("Secure Corporate Payments", className="app-subtitle")
                ])
            ], className="d-flex align-items-center")
        ], width='auto'),
        dbc.Col(html.Div([
            html.Small("Total Network Volume", className="text-muted"),
            html.H3(format_currency(total_volume), className="fw-bold text-success")
        ], className="kpi-card"), className="d-flex align-items-center justify-content-end")
    ])), className="app-header")


def create_navigation():
    nav_items = {
        'transfer': {'icon': 'fa-exchange-alt', 'label': 'A2A Transfer'},
        'payroll': {'icon': 'fa-users', 'label': 'Bulk Payroll'},
        'transactions': {'icon': 'fa-history', 'label': 'Transactions'},
        'dashboard': {'icon': 'fa-tachometer-alt', 'label': 'Network'},
        'analytics': {'icon': 'fa-chart-pie', 'label': 'Analytics'}
    }
    return dbc.Nav(
        [dbc.NavLink([html.I(className=f"fas {v['icon']} me-2"), v['label']],
                     href=f"/{k}",
                     id=f"nav-{k}",
                     active="exact")
         for k, v in nav_items.items()],
        pills=True,
        className="bg-white p-2 rounded"
    )


# ==============================================================================
# UPDATED SECTION: The `create_analytics_view` function is updated with new graphs.
# ==============================================================================
def create_analytics_view():
    return html.Div([
        dbc.Row(id="kpi-cards", className="mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='monthly-trends-chart', config={'displayModeBar': False}))),
                    lg=7),
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='top-transfer-banks-chart', config={'displayModeBar': False}))),
                    lg=5),
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='transfer-dist-chart', config={'displayModeBar': False}))),
                    lg=6),
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='payroll-by-dept-chart', config={'displayModeBar': False}))),
                    lg=6),
        ]),
        # NEW: Row for the new Pie and Scatter charts
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='transaction-type-pie', config={'displayModeBar': False}))),
                    lg=5),
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='amount-vs-time-scatter', config={'displayModeBar': False}))),
                    lg=7),
        ])
    ])


# ==============================================================================
# END OF UPDATED SECTION
# ==============================================================================

def create_transactions_view():
    return dbc.Card([
        dbc.CardHeader(html.H5("📊 Transaction History")),
        dbc.CardBody(
            dbc.Tabs([
                dbc.Tab(
                    html.Div(id='all-transactions-content', className="p-2", children=[dbc.Spinner(color="primary")]),
                    label="All Transactions"),
                dbc.Tab(html.Div(id='transfer-transactions-content', className="p-2",
                                 children=[dbc.Spinner(color="primary")]), label="💸 Account Transfers"),
                dbc.Tab(html.Div(id='payroll-transactions-content', className="p-2",
                                 children=[dbc.Spinner(color="primary")]), label="💼 Bulk Payroll"),
            ])
        )
    ])


def create_dashboard():
    banks = get_all_banks()
    today_str = datetime.datetime.now(pytz.timezone('Africa/Nairobi')).strftime('%Y-%m-%d')
    seven_days_ago_str = (datetime.datetime.now(pytz.timezone('Africa/Nairobi')) - datetime.timedelta(days=7)).strftime(
        '%Y-%m-%d')

    with get_db_connection() as conn:
        num_accounts = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        transfers_today = \
        conn.execute("SELECT COUNT(*) FROM transactions WHERE DATE(timestamp) = ? AND type = 'transfer'",
                     (today_str,)).fetchone()[0]
        payrolls_today = \
        conn.execute("SELECT COUNT(*) FROM transactions WHERE DATE(timestamp) = ? AND type = 'payroll'",
                     (today_str,)).fetchone()[0]
        bank_volumes = conn.execute("""
            SELECT a.bank, SUM(t.amount) as volume
            FROM transactions t JOIN accounts a ON t.to_acct = a.id
            WHERE DATE(t.timestamp) >= ?
            GROUP BY a.bank
        """, (seven_days_ago_str,)).fetchall()
        bank_volume_map = {row['bank']: row['volume'] for row in bank_volumes}

    bank_cards = []
    for bank in banks:
        volume = bank_volume_map.get(bank, 0)
        card = dbc.Col(dbc.Card([
            dbc.CardHeader(html.Div([html.I(className="fas fa-university me-2"), html.Span(bank)],
                                    className="d-flex align-items-center")),
            dbc.CardBody([
                html.P("Status: Active", className="text-success small mb-2"),
                html.H5(format_currency(volume), className="text-primary"),
                html.Small("7-Day Inbound Volume", className="text-muted")
            ])
        ], outline=True, color="secondary"), md=4, lg=3, className="mb-3")
        bank_cards.append(card)

    return dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader(html.H4("Connected Banking Network")), dbc.CardBody(dbc.Row(bank_cards))]),
                lg=9),
        dbc.Col(dbc.Card([dbc.CardHeader(html.H5("Quick Stats")), dbc.CardBody([
            dbc.ListGroup([
                dbc.ListGroupItem(
                    [
                        "Active Accounts",
                        dbc.Badge(num_accounts, color="primary", pill=True, className="ms-1")
                    ],
                    className="d-flex justify-content-between align-items-center"
                ),
                dbc.ListGroupItem(
                    [
                        "Today's Transfers",
                        dbc.Badge(transfers_today, color="success", pill=True, className="ms-1")
                    ],
                    className="d-flex justify-content-between align-items-center"
                ),
                dbc.ListGroupItem(
                    [
                        "Today's Payrolls",
                        dbc.Badge(payrolls_today, color="info", pill=True, className="ms-1")
                    ],
                    className="d-flex justify-content-between align-items-center"
                )
            ], flush=True)
        ])]), lg=3)
    ])


# --- App Layout ---
app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id='current-view-store', data='transfer'),
    dcc.Store(id='current-pin-store', data=''),
    dcc.Store(id='pending-transaction-store', data={}),
    dcc.Store(id='transaction-refresh-signal', data=None),
    dcc.Store(id='animation-step-store', data=0),
    dcc.Interval(id='animation-interval', interval=1500, n_intervals=0, disabled=True),
    dcc.Interval(id='interval-component', interval=3000, n_intervals=0, disabled=True),

    dbc.Modal([
        dbc.ModalHeader(html.H4("🔒 Secure Passphrase Verification")),
        dbc.ModalBody([
            html.P("Please review the transaction summary and enter your passphrase to proceed."),
            html.Div(id="passphrase-summary-body"),
            html.Hr(),
            dbc.Input(id="security-passphrase-input", type="password", placeholder="Enter your secret passphrase"),
            html.Div(id="passphrase-alert-container", className="mt-2")
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="passphrase-cancel-btn", color="secondary"),
            dbc.Button("Submit Passphrase", id="submit-passphrase-btn", color="primary")
        ])
    ], id="passphrase-modal", is_open=False, backdrop="static"),

    dbc.Modal([dbc.ModalHeader("Secure PIN Entry"), dbc.ModalBody(id="pin-entry-body"),
               dbc.ModalFooter(dbc.Button("Cancel", id="pin-cancel-btn", color="secondary"))], id="pin-modal",
              is_open=False, backdrop="static"),
    dbc.Modal(
        [dbc.ModalBody(id="processing-body"),
         dbc.ModalFooter(dbc.Button("Close", id="close-processing-modal-btn", color="primary"))],
        id="processing-modal", is_open=False, centered=True, backdrop="static"),

    html.Div(id='header-container', className="mb-4"),
    html.Div(create_navigation(), className="mb-4"),

    html.Div(id='page-content')

], className="app-container py-4", fluid=True)


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    view = (pathname or "/").strip("/").split("/")[-1]
    if view == 'payroll':
        return create_payroll_section()
    elif view == 'transactions':
        return create_transactions_view()
    elif view == 'dashboard':
        return create_dashboard()
    elif view == 'analytics':
        return create_analytics_view()
    else:  # Default to transfer view
        return create_transfer_form()


@app.callback(
    [Output(f'nav-{view}', 'active') for view in ['transfer', 'payroll', 'transactions', 'dashboard', 'analytics']],
    Input('url', 'pathname')
)
def update_active_navlink(pathname):
    view = (pathname or "/").strip("/").split("/")[-1]
    if not view: view = 'transfer'
    return [view == v for v in ['transfer', 'payroll', 'transactions', 'dashboard', 'analytics']]


@app.callback(Output('header-container', 'children'),
              Input('transaction-refresh-signal', 'data'))
def update_header_live(refresh_signal):
    return create_header()


# Callback for switching payroll input methods
@app.callback(
    Output('payroll-input-select', 'style'),
    Output('payroll-input-upload', 'style'),
    Output('payroll-input-manual', 'style'),
    Input('payroll-mode-radios', 'value')
)
def switch_payroll_mode(mode):
    select_style = upload_style = manual_style = {'display': 'none'}
    if mode == 'select':
        select_style = {'display': 'block'}
    elif mode == 'upload':
        upload_style = {'display': 'block'}
    elif mode == 'manual':
        manual_style = {'display': 'block'}
    return select_style, upload_style, manual_style


@app.callback(
    Output('all-transactions-content', 'children'),
    Output('transfer-transactions-content', 'children'),
    Output('payroll-transactions-content', 'children'),
    Input('transaction-refresh-signal', 'data'),
    Input('url', 'pathname')
)
def update_transaction_tables(refresh_signal, pathname):
    if 'transactions' not in pathname:
        return no_update, no_update, no_update

    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY timestamp DESC", conn)

    if df.empty:
        no_data_msg = html.Div("No transactions found.", className="text-center text-muted p-4")
        return no_data_msg, no_data_msg, no_data_msg

    df['from_acct'] = df['from_acct'].apply(get_account_name)
    df['to_acct'] = df['to_acct'].apply(get_account_name)
    df['amount'] = df['amount'].apply(format_currency)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

    df.rename(columns={
        'id': 'Reference', 'from_acct': 'From', 'to_acct': 'To', 'amount': 'Amount',
        'type': 'Type', 'status': 'Status', 'timestamp': 'Timestamp'
    }, inplace=True)

    table_style = {
        'style_cell': {'textAlign': 'left', 'padding': '10px', 'fontFamily': 'sans-serif', 'border': '1px solid #eee'},
        'style_header': {'backgroundColor': '#f8f9fa', 'fontWeight': 'bold', 'borderBottom': '2px solid #dee2e6'},
        'style_data_conditional': [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
        'page_size': 10,
        'style_table': {'overflowX': 'auto'}
    }

    all_table = dash_table.DataTable(data=df.to_dict('records'),
                                     columns=[{'name': i, 'id': i} for i in df.columns if i != 'method'], **table_style)
    transfer_table = dash_table.DataTable(data=df[df['Type'] == 'transfer'].to_dict('records'),
                                          columns=[{'name': i, 'id': i} for i in df.columns if i != 'method'],
                                          **table_style)
    payroll_table = dash_table.DataTable(data=df[df['Type'] == 'payroll'].to_dict('records'),
                                         columns=[{'name': i, 'id': i} for i in df.columns if i != 'method'],
                                         **table_style)

    return all_table, transfer_table, payroll_table


# ==============================================================================
# UPDATED SECTION: The analytics callback is fixed and enhanced.
# ==============================================================================
@app.callback(
    Output('kpi-cards', 'children'),
    Output('payroll-by-dept-chart', 'figure'),
    Output('transfer-dist-chart', 'figure'),
    Output('monthly-trends-chart', 'figure'),
    Output('top-transfer-banks-chart', 'figure'),
    Output('transaction-type-pie', 'figure'),  # NEW output
    Output('amount-vs-time-scatter', 'figure'),  # NEW output
    Input('url', 'pathname'),
    # FIX: Removed prevent_initial_call=True to allow loading on page entry
)
def update_analytics_page(pathname):
    if 'analytics' not in pathname:
        # Update number of no_updates to match number of outputs
        return [no_update] * 7

    with get_db_connection() as conn:
        # KPIs and existing charts data
        total_volume = conn.execute("SELECT SUM(amount) FROM transactions WHERE status='completed'").fetchone()[0] or 0
        total_transactions = conn.execute("SELECT COUNT(*) FROM transactions WHERE status='completed'").fetchone()[
                                 0] or 0
        avg_transfer = \
        conn.execute("SELECT AVG(amount) FROM transactions WHERE status='completed' AND type='transfer'").fetchone()[
            0] or 0
        df_payroll = pd.read_sql_query(
            "SELECT department, SUM(amount) as total_payroll FROM master_employees GROUP BY department", conn)
        df_trends = pd.read_sql_query(
            "SELECT STRFTIME('%Y-%m', timestamp) as month, SUM(amount) as volume FROM transactions WHERE status='completed' GROUP BY month ORDER BY month ASC",
            conn)
        df_banks = pd.read_sql_query("""
            SELECT a.bank, SUM(t.amount) as volume
            FROM transactions t JOIN accounts a ON t.to_acct = a.id
            WHERE t.status='completed'
            GROUP BY a.bank ORDER BY volume DESC LIMIT 5
        """, conn)
        # NEW: Data for new charts
        df_trans_full = pd.read_sql_query("SELECT amount, timestamp, type FROM transactions WHERE status='completed'",
                                          conn)

    # --- KPI Cards ---
    kpi_cards = [
        dbc.Col(dbc.Card(
            dbc.CardBody([html.H4(format_currency(total_volume)), html.P("Total Volume", className="text-muted")])),
                md=4),
        dbc.Col(dbc.Card(
            dbc.CardBody([html.H4(f"{total_transactions:,}"), html.P("Total Transactions", className="text-muted")])),
                md=4),
        dbc.Col(dbc.Card(dbc.CardBody(
            [html.H4(format_currency(avg_transfer)), html.P("Avg. Transfer Amount", className="text-muted")])), md=4),
    ]

    # --- Charting ---
    plot_template = 'plotly_white'

    # Payroll by Dept (Bar)
    fig_payroll = px.bar(df_payroll, x='department', y='total_payroll', title="Payroll Costs by Department",
                         labels={'department': 'Department', 'total_payroll': 'Total Payroll Amount'},
                         template=plot_template)
    fig_payroll.update_layout(title_x=0.5, margin=dict(l=20, r=20, t=40, b=20))

    # Transaction Size Distribution (Pie)
    bins = [0, 10000, 50000, 100000, float('inf')]
    labels = ['< 10k', '10k - 50k', '50k - 100k', '> 100k']
    df_trans_full['range'] = pd.cut(df_trans_full['amount'], bins=bins, labels=labels, right=False)
    dist_data = df_trans_full['range'].value_counts().reset_index()
    fig_dist = px.pie(dist_data, names='range', values='count', title="Distribution of Transaction Sizes", hole=.3,
                      template=plot_template)
    fig_dist.update_layout(title_x=0.5, margin=dict(l=20, r=20, t=40, b=20))

    # Monthly Trends (Line)
    fig_trends = px.line(df_trends, x='month', y='volume', title="Monthly Transaction Volume", markers=True,
                         labels={'month': 'Month', 'volume': 'Transaction Volume'}, template=plot_template)
    fig_trends.update_layout(title_x=0.5, margin=dict(l=20, r=20, t=40, b=20))

    # Top Banks (Bar)
    fig_banks = px.bar(df_banks, x='bank', y='volume', title="Top 5 Banks by Inbound Volume",
                       labels={'bank': 'Bank', 'volume': 'Inbound Volume'}, template=plot_template)
    fig_banks.update_layout(title_x=0.5, margin=dict(l=20, r=20, t=40, b=20))

    # --- NEW: Transaction Type (Pie Chart) ---
    type_counts = df_trans_full['type'].str.capitalize().value_counts().reset_index()
    fig_type_pie = px.pie(type_counts, names='type', values='count', title='Transaction Count by Type', hole=0.3,
                          template=plot_template)
    fig_type_pie.update_layout(title_x=0.5, margin=dict(l=20, r=20, t=40, b=20))

    # --- NEW: Amount vs. Time (Scatter Plot) ---
    df_trans_full['timestamp'] = pd.to_datetime(df_trans_full['timestamp'])
    fig_scatter = px.scatter(
        df_trans_full,
        x='timestamp',
        y='amount',
        color=df_trans_full['type'].str.capitalize(),
        title='Transaction Amount vs. Time',
        labels={'timestamp': 'Date', 'amount': 'Amount (KES)', 'color': 'Type'},
        hover_data={'amount': ':.2f'},
        template=plot_template
    )
    fig_scatter.update_layout(title_x=0.5, margin=dict(l=20, r=20, t=40, b=20))

    return kpi_cards, fig_payroll, fig_dist, fig_trends, fig_banks, fig_type_pie, fig_scatter


# ==============================================================================
# END OF UPDATED SECTION
# ==============================================================================


@app.callback(
    Output('payroll-table', 'data'),
    Input('employee-selection-dropdown', 'value')
)
def update_payroll_table(employee_ids):
    if not employee_ids:
        return []
    placeholders = ','.join(['?'] * len(employee_ids))
    query = f"SELECT name AS clientName, account AS clientMSISDN, 'N/A' AS clientIDNumber, amount AS amountExpected, 'Monthly Salary' AS billDesc FROM master_employees WHERE id IN ({placeholders})"
    with get_db_connection() as conn:
        df = pd.read_sql_query(query, conn, params=employee_ids)
    return df.to_dict('records')


@app.callback(
    Output('process-payroll-btn', 'disabled'),
    Input('payroll-table', 'data')
)
def toggle_process_payroll_button(data):
    return not data


@app.callback(
    [Output('senderName-input', 'value'), Output('senderMSISDN-input', 'value'),
     Output('senderIDNumber-input', 'value'), Output('senderEmail-input', 'value'),
     Output('senderBankName-input', 'value'), Output('senderAccountNum-input', 'value')],
    Input('load-sender-dropdown', 'value'),
    prevent_initial_call=True
)
def load_saved_sender(sender_id):
    if not sender_id:
        return [""] * 6
    with get_db_connection() as conn:
        sender = conn.execute("SELECT * FROM saved_senders WHERE id = ?", (sender_id,)).fetchone()
    if sender:
        return sender['name'], sender['msisdn'], sender['id_number'], sender['email'], sender['bank_name'], sender[
            'bank_account_number']
    return [no_update] * 6


@app.callback(
    [Output('clientName-input', 'value'), Output('clientMSISDN-input', 'value'),
     Output('clientIDNumber-input', 'value'), Output('clientEmail-input', 'value'),
     Output('clientBankName-input', 'value'), Output('clientAccountNum-input', 'value')],
    Input('load-recipient-dropdown', 'value'),
    prevent_initial_call=True
)
def load_saved_recipient(recipient_id):
    if not recipient_id:
        return [""] * 6
    with get_db_connection() as conn:
        recipient = conn.execute("SELECT * FROM saved_recipients WHERE id = ?", (recipient_id,)).fetchone()
    if recipient:
        return recipient['name'], recipient['msisdn'], recipient['id_number'], recipient['email'], recipient[
            'bank_name'], recipient['bank_account_number']
    return [no_update] * 6


@app.callback(
    Output('execute-transfer-btn', 'disabled'),
    [Input('senderName-input', 'value'), Input('senderAccountNum-input', 'value'),
     Input('clientName-input', 'value'), Input('clientAccountNum-input', 'value'),
     Input('amountExpected-input', 'value')]
)
def toggle_execute_button(s_name, s_acct, r_name, r_acct, amount):
    return not all([s_name, s_acct, r_name, r_acct, amount])


@app.callback(
    [Output('passphrase-modal', 'is_open'),
     Output('passphrase-summary-body', 'children'),
     Output('pending-transaction-store', 'data'),
     Output('transfer-popover', 'is_open'),
     Output('load-sender-dropdown', 'options'),
     Output('load-recipient-dropdown', 'options')],
    Input('confirm-transfer-popover-btn', 'n_clicks'),
    [State('senderName-input', 'value'), State('senderMSISDN-input', 'value'),
     State('senderIDNumber-input', 'value'), State('senderEmail-input', 'value'),
     State('senderBankName-input', 'value'), State('senderAccountNum-input', 'value'),
     State('save-sender-checkbox', 'value'),
     State('clientName-input', 'value'), State('clientMSISDN-input', 'value'),
     State('clientIDNumber-input', 'value'), State('clientEmail-input', 'value'),
     State('clientBankName-input', 'value'), State('clientAccountNum-input', 'value'),
     State('save-recipient-checkbox', 'value'),
     State('amountExpected-input', 'value'), State('billDesc-input', 'value')],
    prevent_initial_call=True
)
def handle_transfer_confirmation(
        t_clicks, s_name, s_msisdn, s_id, s_email, s_bank, s_acct, save_sender,
        r_name, r_msisdn, r_id, r_email, r_bank, r_acct, save_recipient, amount, desc):
    if amount is None:
        return False, no_update, no_update, False, no_update, no_update

    sender_options, recipient_options = no_update, no_update

    with get_db_connection() as conn:
        if save_sender and s_name:
            conn.execute(
                "INSERT OR REPLACE INTO saved_senders (name, msisdn, id_number, email, bank_name, bank_account_number) VALUES (?, ?, ?, ?, ?, ?)",
                (s_name, s_msisdn, s_id, s_email, s_bank, s_acct))
            conn.commit()
            senders = conn.execute("SELECT id, name FROM saved_senders ORDER BY name").fetchall()
            sender_options = [{'label': s['name'], 'value': s['id']} for s in senders]

        if save_recipient and r_name:
            conn.execute(
                "INSERT OR REPLACE INTO saved_recipients (name, msisdn, id_number, email, bank_name, bank_account_number) VALUES (?, ?, ?, ?, ?, ?)",
                (r_name, r_msisdn, r_id, r_email, r_bank, r_acct))
            conn.commit()
            recipients = conn.execute("SELECT id, name FROM saved_recipients ORDER BY name").fetchall()
            recipient_options = [{'label': r['name'], 'value': r['id']} for r in recipients]

    ref = f'INV-{uuid.uuid4().hex[:8].upper()}'
    data = {'type': 'transfer', 'payload': {
        'senderName': s_name, 'senderAccount': s_acct, 'senderBank': s_bank,
        'clientName': r_name, 'clientAccount': r_acct, 'clientBank': r_bank, 'clientMSISDN': r_msisdn,
        'amountExpected': float(amount), 'billRefNumber': ref, 'billDesc': desc
    }}
    summary_list = dbc.ListGroup([
        dbc.ListGroupItem(f"From: {s_name} ({s_bank})", className="text-danger fw-bold"),
        dbc.ListGroupItem(f"To: {r_name} ({r_bank})"),
        dbc.ListGroupItem(f"Reference: {ref}"),
        dbc.ListGroupItem(f"Amount: {format_currency(amount)}", color="primary", className="fw-bold fs-5"),
    ], flush=True)

    return True, summary_list, data, False, sender_options, recipient_options


@app.callback(
    [Output('passphrase-modal', 'is_open', allow_duplicate=True),
     Output('passphrase-summary-body', 'children', allow_duplicate=True),
     Output('pending-transaction-store', 'data', allow_duplicate=True),
     Output('payroll-popover', 'is_open')],
    Input('confirm-payroll-popover-btn', 'n_clicks'),
    State('payroll-table', 'data'),
    prevent_initial_call=True
)
def handle_payroll_confirmation(p_clicks, p_data):
    if not p_data:
        return no_update, no_update, no_update, False

    total_amount = sum(float(row.get('amountExpected', 0)) for row in p_data)
    num_employees = len(p_data)
    ref = f'PAYROLL-{uuid.uuid4().hex[:6].upper()}'
    data = {'type': 'payroll', 'amount': total_amount, 'ref': ref}
    summary_list = dbc.ListGroup([
        dbc.ListGroupItem(f"Employees: {num_employees}", className="text-info fw-bold"),
        dbc.ListGroupItem(f"Reference: {ref}"),
        dbc.ListGroupItem(f"Total Amount: {format_currency(total_amount)}", color="primary", className="fw-bold fs-5"),
    ], flush=True)
    return True, summary_list, data, False


@app.callback(
    [Output('pin-modal', 'is_open'),
     Output('passphrase-modal', 'is_open', allow_duplicate=True),
     Output('passphrase-alert-container', 'children'),
     Output('current-pin-store', 'data', allow_duplicate=True),
     Output('pin-entry-body', 'children', allow_duplicate=True)],
    [Input('submit-passphrase-btn', 'n_clicks'), Input('passphrase-cancel-btn', 'n_clicks')],
    [State('security-passphrase-input', 'value')],
    prevent_initial_call=True
)
def handle_passphrase_submission(submit_clicks, cancel_clicks, passphrase):
    trig_id = callback_context.triggered_id
    if trig_id == 'passphrase-cancel-btn':
        return False, False, None, no_update, no_update
    if passphrase == SECURE_PASSPHRASE:
        return True, False, None, '', create_mobile_keypad('')
    else:
        alert = dbc.Alert("Invalid Passphrase. Please try again.", color="danger", dismissable=True, duration=4000)
        return False, True, alert, no_update, no_update


@app.callback(
    [Output('processing-modal', 'is_open'), Output('processing-body', 'children'),
     Output('pin-modal', 'is_open', allow_duplicate=True),
     Output('current-pin-store', 'data', allow_duplicate=True), Output('transaction-refresh-signal', 'data'),
     Output('interval-component', 'disabled', allow_duplicate=True),
     Output('animation-interval', 'disabled', allow_duplicate=True),
     Output('animation-step-store', 'data', allow_duplicate=True)],
    Input('current-pin-store', 'data'),
    State('pending-transaction-store', 'data'),
    prevent_initial_call=True
)
def process_payment(pin, data):
    if not pin or len(pin) != 4:
        return [no_update] * 8

    if pin != '1234':
        body = create_processing_animation(status='failed', message="Invalid PIN.")
        return True, body, False, '', no_update, True, True, 0

    is_success, msg = False, ""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if data['type'] == 'transfer':
                payload = data['payload']
                amount = payload['amountExpected']
                sender_acct = cursor.execute("SELECT id, balance FROM accounts WHERE accountNumber = ?",
                                             (payload['senderAccount'],)).fetchone()
                if not sender_acct: raise ValueError(f"Sender account {payload['senderAccount']} not found.")
                if sender_acct['balance'] < amount: raise ValueError("Insufficient funds in the sender's account.")
                receiver_acct = cursor.execute("SELECT id FROM accounts WHERE accountNumber = ?",
                                               (payload['clientAccount'],)).fetchone()
                if not receiver_acct: raise ValueError(f"Recipient account {payload['clientAccount']} not found.")
                cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, sender_acct['id']))
                cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, receiver_acct['id']))
                cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                    payload['billRefNumber'], sender_acct['id'], receiver_acct['id'], amount, 'transfer', 'completed',
                    datetime.datetime.now(pytz.timezone('Africa/Nairobi')).isoformat(), 'A2A-INTERNAL'))
            elif data['type'] == 'payroll':
                amount = data['amount']
                ref = data['ref']
                from_acct = 'acc003'
                bal = cursor.execute("SELECT balance FROM accounts WHERE id = ?", (from_acct,)).fetchone()[0]
                if bal < amount: raise ValueError("Insufficient corporate funds for payroll.")
                cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_acct))
                cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                    ref, from_acct, 'EXTERNAL_BULK', amount, 'payroll', 'completed',
                    datetime.datetime.now(pytz.timezone('Africa/Nairobi')).isoformat(), 'API-Bulk'))
            conn.commit()
            is_success = True
    except (sqlite3.Error, ValueError, TypeError, IndexError) as e:
        msg = str(e)

    if is_success:
        initial_body = create_processing_animation(step=0)
        return True, initial_body, False, '', datetime.datetime.now().isoformat(), True, False, 0
    else:
        fail_body = create_processing_animation(status='failed', message=msg)
        return True, fail_body, False, '', no_update, True, True, 0


@app.callback(
    Output('processing-body', 'children', allow_duplicate=True),
    Output('animation-step-store', 'data', allow_duplicate=True),
    Output('animation-interval', 'disabled', allow_duplicate=True),
    Output('interval-component', 'disabled', allow_duplicate=True),
    Output('transaction-refresh-signal', 'data', allow_duplicate=True),
    Input('animation-interval', 'n_intervals'),
    State('animation-step-store', 'data'),
    prevent_initial_call=True
)
def update_animation_step(n, current_step):
    if n == 0: return [no_update] * 5
    next_step = current_step + 1
    number_of_animation_steps = 4
    if next_step <= number_of_animation_steps:
        new_body = create_processing_animation(step=next_step)
        is_animation_disabled = next_step == number_of_animation_steps
        close_interval_disabled = not is_animation_disabled
        refresh_signal = datetime.datetime.now().isoformat() if is_animation_disabled else no_update
        return new_body, next_step, is_animation_disabled, close_interval_disabled, refresh_signal
    return [no_update] * 5


@app.callback(
    [Output('pin-modal', 'is_open', allow_duplicate=True), Output('current-pin-store', 'data', allow_duplicate=True),
     Output('pin-entry-body', 'children', allow_duplicate=True)],
    [Input('pin-cancel-btn', 'n_clicks'), Input({'type': 'keypad-btn', 'index': ALL}, 'n_clicks')],
    [State('current-pin-store', 'data')], prevent_initial_call=True
)
def handle_pin_modal(canc, keys, pin):
    ctx = callback_context
    trig_id = ctx.triggered_id
    if trig_id == 'pin-cancel-btn': return False, '', no_update
    if not isinstance(trig_id, dict): return no_update, no_update, no_update
    index = trig_id['index']
    new_pin = pin or ""
    if index == 'del':
        new_pin = new_pin[:-1]
    elif index == 'confirm':
        return False, new_pin, no_update
    elif len(new_pin) < 4:
        new_pin += index
    return True, new_pin, create_mobile_keypad(new_pin)


@app.callback(Output('processing-modal', 'is_open', allow_duplicate=True), Input('interval-component', 'n_intervals'),
              prevent_initial_call=True)
def auto_close_processing_modal(n): return False


@app.callback([Output('processing-modal', 'is_open', allow_duplicate=True),
               Output('interval-component', 'disabled', allow_duplicate=True)],
              Input('close-processing-modal-btn', 'n_clicks'), prevent_initial_call=True)
def manual_close_processing_modal(n): return False, True


if __name__ == '__main__':
    app.run(debug=True, port=8859)

