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
import json
import re
import warnings
import os

# --- BRAND COLORS ---
CP_PRIMARY = "#EF5E41"  # Orange-Red
CP_SECONDARY = "#006E92"  # Dark Teal/Blue
CP_ACCENT_PURPLE = "#892887"  # Gradient Start
CP_ACCENT_ORANGE = "#F27224"  # Accent Orange
# --- END BRAND COLORS ---

# Suppress the FutureWarnings from Pandas related to downcasting
warnings.filterwarnings("ignore", category=FutureWarning)
pd.set_option('future.no_silent_downcasting', True)

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
    if account_id == 'EXTERNAL_PAYEE': return "Individual External Payee"
    with get_db_connection() as conn:
        details = conn.execute("SELECT name FROM accounts WHERE id = ?", (account_id,)).fetchone()
    return details['name'] if details else 'Unknown Account'


def format_currency(amount):
    if amount is None: amount = 0
    return f"TZs {float(amount):,.2f}"


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename or 'xlsx' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return html.Div(['Please upload a CSV or Excel file.'])

        # Standardize column names
        df.columns = [re.sub(r'[^a-zA-Z0-9]', '', str(col).lower().strip()) for col in df.columns]

        # Mapping common header variants to internal column names
        required_mapping = {
            'clientName': ['clientname', 'name', 'fullname'],
            'clientBank': ['clientbank', 'bank', 'recipientbank'],
            'clientAccountNum': ['clientaccountnum', 'accountnumber', 'account'],
            'clientMSISDN': ['clientmsisdn', 'msisdn', 'phone'],
            'clientIDNumber': ['clientidnumber', 'id', 'idnumber'],
            'clientEmail': ['clientemail', 'email'],
            'amountExpected': ['amountexpected', 'amount', 'salary'],
            'billDesc': ['billdesc', 'desc', 'narration']
        }

        final_cols = {}
        for target_col, variants in required_mapping.items():
            found = False
            for variant in variants:
                if variant in df.columns:
                    final_cols[variant] = target_col
                    found = True
                    break
            if not found:
                # Set smart defaults
                default_value = 'External Bank' if target_col == 'clientBank' else '' if target_col == 'clientEmail' else 'N/A'
                df[target_col] = default_value
                final_cols[target_col] = target_col

        df.rename(columns=final_cols, inplace=True)
        final_df = df.reindex(columns=list(required_mapping.keys()))

        final_df['clientMSISDN'] = final_df['clientMSISDN'].fillna('N/A')
        final_df['clientIDNumber'] = final_df['clientIDNumber'].fillna('N/A')
        final_df['billDesc'] = final_df['billDesc'].fillna('Bulk Payment')
        final_df['clientBank'] = final_df['clientBank'].fillna('External Bank')
        final_df['clientAccountNum'] = final_df['clientAccountNum'].fillna('N/A')
        final_df['clientEmail'] = final_df['clientEmail'].fillna('')

        final_df['amountExpected'] = pd.to_numeric(final_df['amountExpected'], errors='coerce').fillna(0)

        final_df = final_df[final_df['clientName'].astype(str).str.strip() != '']

        return final_df.to_dict('records')

    except Exception as e:
        return html.Div(
            [f'There was an error processing this file. Ensure it is not locked and is a valid CSV/Excel file: {e}'])


# --- Logo Handling (Simplified to use static URL) ---
STATIC_LOGO_URL = '/assets/LOGO.png'
# The following variable is no longer used for image display but is kept for minimal change impact
ENCODED_LOGO = STATIC_LOGO_URL 


# --- Initialize App ---
app = dash.Dash(
    __name__,
    title="CapitalPay Operating System"
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, '/assets/capitalpay_brand.css'], 
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

# *** IMPORTANT: app.index_string removed to fix InvalidIndexException ***

app.config.suppress_callback_exceptions = True
SECURE_PASSPHRASE = "Test123"
server = app.server


# --- UI Component Creation Functions ---
def create_processing_animation(step=0, status='processing', message=None):
    if status == 'failed':
        return html.Div([
            html.I(className="fas fa-times-circle fa-4x", style={'color': CP_PRIMARY, 'marginBottom': '10px'}),
            html.H4("Transaction Failed", style={'color': CP_PRIMARY}),
            html.P(message, className="text-muted mt-2")
        ], className="text-center p-4")

    animation_steps = [
        {"icon": "fa-shield-alt", "text": "Encrypting Transaction Details...", "progress": 20},
        {"icon": "fa-network-wired", "text": " Capital Pay Aggregator Engine Contacting Banking Network...",
         "progress": 40},
        {"icon": "fa-random", "text": "Authorizing Payment...", "progress": 60},
        {"icon": "fa-money-bill-wave", "text": "Securely Transferring Funds...", "progress": 80},
    ]

    if step < len(animation_steps):
        current_step = animation_steps[step]
        return html.Div([
            html.Div(html.I(className=f"fas {current_step['icon']} fa-beat-fade fa-3x", style={'color': CP_SECONDARY}),
                     style={'marginBottom': '20px'}),
            html.H4(current_step['text'], style={'color': CP_SECONDARY}),
            dbc.Progress(value=current_step['progress'], striped=True, animated=True, className="mt-3", color="primary")
        ], className="text-center p-4")
    else:
        return html.Div([
            html.I(className="fas fa-check-circle fa-4x", style={'color': CP_SECONDARY, 'marginBottom': '10px'}),
            html.H4("Transaction Successful!", style={'color': CP_SECONDARY}),
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
                 style={'fontSize': '32px', 'letterSpacing': '10px', 'fontFamily': 'monospace', 'color': CP_SECONDARY},
                 className="text-center mb-4"),
        html.Div([dbc.Row([dbc.Col(btn) for btn in row], className="justify-content-center") for row in rows],
                 style={'maxWidth': '280px', 'margin': '0 auto'})
    ])


def create_transfer_form():
    with get_db_connection() as conn:
        senders = conn.execute("SELECT id, name FROM saved_senders ORDER BY name").fetchall()
        recipients = conn.execute("SELECT id, name FROM saved_recipients ORDER BY name").fetchall()
    sender_options = [{'label': s['name'], 'value': s['id']} for s in senders]
    recipient_options = [{'label': r['name'], 'value': r['id']} for r in recipients]

    # NOTE: The outer Div has ID 'transfer-form-container' for isolation/debugging
    return html.Div(id='transfer-form-container', children=[
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.Div([
                    html.I(className="fas fa-arrow-circle-up me-2", style={'color': CP_PRIMARY}),
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
                    html.I(className="fas fa-arrow-circle-down me-2", style={'color': CP_SECONDARY}),
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
                html.I(className="fas fa-file-invoice-dollar me-2", style={'color': CP_ACCENT_PURPLE}),
                "Transaction Details"
            ], className="form-section-card-header")),
            dbc.CardBody(dbc.Row([
                dbc.Col([
                    dbc.Label("Amount (TZs)"),
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
                        dbc.Button("Confirm & Continue", id="confirm-transfer-popover-btn", color="primary", size="sm")
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
        dcc.Store(id='payroll-temp-data-store', data=[]),
        dcc.Store(id='uploaded-data-store', data=None),
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
                        "File must contain Name, Account No., Email, Amount, and Recipient Bank Name columns (or common variants).",
                        className="text-muted d-block mt-2"),
                    html.Div(id='upload-alert-container', className="mt-2")
                ], id='payroll-input-upload', style={'display': 'none'}),
                html.Div(
                    [
                        dbc.Button([html.I(className="fas fa-plus me-2"), "Add New Row"], id='add-payroll-row-btn',
                                   color='primary', outline=True, className="w-100"),
                    ],
                    id='payroll-input-manual',
                    style={'display': 'none'}
                ),
            ])
        ]),
        dbc.Card([
            dbc.CardHeader(html.H5("Step 2: Review and Process Payroll Batch")),
            dbc.CardBody([
                dash_table.DataTable(
                    id='payroll-table',
                    columns=[
                        {"name": "Name", "id": "clientName", "editable": True},
                        {"name": "Recipient Bank", "id": "clientBank", "editable": True},
                        {"name": "Account Number", "id": "clientAccountNum", "editable": True},
                        {"name": "Email (Opt.)", "id": "clientEmail", "editable": True},
                        {"name": "Phone (MSISDN)", "id": "clientMSISDN", "editable": True},
                        {"name": "ID No", "id": "clientIDNumber", "editable": True},
                        {"name": "Amount", "id": "amountExpected", "type": "numeric",
                         "format": {'specifier': ',.2f'}, "editable": True},
                        {"name": "Narration", "id": "billDesc", "editable": True}
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
            # --- 3 Dynamic Submit Buttons ---
            html.Div(id="payroll-submit-container", children=[
                dbc.Button("Process Bulk Payroll", id="process-payroll-btn-default",
                           color="success", size="lg", className="w-100", disabled=True),
                dbc.Button([html.I(className="fas fa-list me-2"), "Process Selected Employees"],
                           id="process-payroll-btn-select", color="primary", size="lg",
                           className="w-100 mt-2", style={'display': 'none'}),
                dbc.Button([html.I(className="fas fa-file-upload me-2"), "Process Uploaded Batch"],
                           id="process-payroll-btn-upload", color="info", size="lg",
                           className="w-100 mt-2", style={'display': 'none'}),
                dbc.Button([html.I(className="fas fa-keyboard me-2"), "Process Manual Batch"],
                           id="process-payroll-btn-manual", color="warning", size="lg",
                           className="w-100 mt-2", style={'display': 'none'}),
            ], className="mt-4"),

            # --- Single Popover for all buttons ---
            dbc.Popover(
                [
                    dbc.PopoverHeader("Confirm Payroll Run"),
                    dbc.PopoverBody([
                        html.P("Please verify all details are correct before proceeding."),
                        dbc.Button("Confirm & Continue", id="confirm-payroll-popover-btn", color="primary", size="sm")
                    ]),
                ],
                id="payroll-popover",
                target="process-payroll-btn-default",
                trigger="click",
                placement="top",
            ),
        ], className="mt-4")
    ])


def create_header():
    """Creates the application header with the logo and the Total Network Volume KPI."""
    with get_db_connection() as conn:
        total_volume_query = "SELECT SUM(amount) FROM transactions WHERE status='completed'"
        total_volume = conn.execute(total_volume_query).fetchone()[0] or 0
        
    # LOGO INTEGRATION: Use STATIC_LOGO_URL for robust serving
    logo_display = html.Img(
        src=STATIC_LOGO_URL,
        style={'height': '50px', 'width': 'auto', 'marginRight': '20px'}
    )
    
    return dbc.Card(dbc.CardBody(dbc.Row([
        dbc.Col([
            html.Div([
                logo_display,  # Use the logo here
                html.Div([
                    html.H1("CapitalPay Operating System", className="app-title", style={'color': CP_SECONDARY}),
                    html.P("Secure Corporate Payments", className="app-subtitle", style={'color': CP_SECONDARY})
                ])
            ], className="d-flex align-items-center")
        ], width='auto'),
        dbc.Col(html.Div([
            html.Small("Total Network Volume", className="text-muted"),
            html.H3(format_currency(total_volume), className="fw-bold text-success")
        ], className="kpi-card"), className="d-flex align-items-center justify-content-end")
    ])), className="app-header")

# --- FOOTER FUNCTION ---
def create_footer():
    """Creates the application footer with the logo, date, and copyright info."""
    current_date_formatted = datetime.datetime.now(pytz.timezone('Africa/Nairobi')).strftime("%B %d, %Y")
    
    # LOGO INTEGRATION: Use STATIC_LOGO_URL for robust serving
    logo_display = html.Img(
        src=STATIC_LOGO_URL,
        style={'height': '20px', 'width': 'auto', 'marginRight': '10px'}
    )

    return html.Footer([
        dbc.Container([
            dbc.Row([
                dbc.Col(html.Div([
                    logo_display,
                    html.Span(f"Powered by Capital Pay. © 2025. All rights reserved.", 
                              className="text-white-50 small")
                ], className="d-flex align-items-center"), md=6),
                dbc.Col(html.Div([
                    html.Span(f"Today: {current_date_formatted}", className="text-white-50 small")
                ], className="text-md-end"), md=6)
            ], className="align-items-center")
        ], fluid=True)
    ], className="app-footer p-3 mt-4")


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
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='transaction-type-pie', config={'displayModeBar': False}))),
                    lg=5),
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='amount-vs-time-scatter', config={'displayModeBar': False}))),
                    lg=7),
        ])
    ])


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

    EXTERNAL_BANK_NAME = 'External Payee Banks'

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

        # 1. Internal Outflow (Money leaving an account in our system)
        outflow_query = f"""
            SELECT a.bank, SUM(t.amount) as outflow
            FROM transactions t
            JOIN accounts a ON t.from_acct = a.id
            WHERE DATE(t.timestamp) >= ? AND t.status='completed'
            GROUP BY a.bank
        """
        # 2. Internal Inflow (Money entering an account in our system)
        inflow_query = f"""
            SELECT a.bank, SUM(t.amount) as inflow
            FROM transactions t
            JOIN accounts a ON t.to_acct = a.id
            WHERE DATE(t.timestamp) >= ? AND t.status='completed'
            AND t.to_acct NOT IN ('EXTERNAL_BULK', 'EXTERNAL_PAYEE') 
            GROUP BY a.bank
        """

        # 3. External Payroll Flow (Tagged by recipient bank name)
        external_payroll_flow_query = f"""
            SELECT SUBSTR(t.method, INSTR(t.method, '_') + 1) as bank, SUM(t.amount) as amount
            FROM transactions t
            WHERE DATE(t.timestamp) >= ? AND t.status='completed'
            AND t.method LIKE 'API-Individual_%' 
            GROUP BY bank
        """

        df_outflow = pd.read_sql_query(outflow_query, conn, params=(seven_days_ago_str,))
        df_inflow = pd.read_sql_query(inflow_query, conn, params=(seven_days_ago_str,))
        df_external_inflow = pd.read_sql_query(external_payroll_flow_query, conn, params=(seven_days_ago_str,))

        # 1. Start with a base containing all internal banks
        internal_banks_list = get_all_banks()
        df_network = pd.DataFrame({'bank': internal_banks_list})

        # 2. Merge internal flows and rename explicitly
        df_network = pd.merge(df_network, df_outflow, on='bank', how='left').fillna(0)
        df_network = pd.merge(df_network, df_inflow.rename(columns={'inflow': 'inflow_internal'}), on='bank',
                              how='left').fillna(0)

        # 3. Merge external payroll flows
        df_network = pd.merge(df_network, df_external_inflow.rename(columns={'amount': 'inflow_external_payroll'}),
                              on='bank', how='left').fillna(0)

        # Ensure all necessary columns are float for safety
        df_network['outflow'] = df_network['outflow'].astype(float)
        df_network['inflow_internal'] = df_network['inflow_internal'].astype(float)
        df_network['inflow_external_payroll'] = df_network['inflow_external_payroll'].astype(float)

        # Calculate final Inflow and Outflow
        df_network['inflow'] = df_network['inflow_internal'] + df_network['inflow_external_payroll']
        df_network['outflow'] = df_network['outflow']

        # Aggregate flows for the External Payee Banks category
        external_outflow_total = df_external_inflow[~df_external_inflow['bank'].isin(internal_banks_list)][
            'amount'].sum()

        # Filter df_network to keep only the internal banks
        df_network = df_network[df_network['bank'].isin(internal_banks_list)].copy()

        # Add the aggregated External Payee Banks row back ONLY IF there was activity (as requested)
        if external_outflow_total > 0:
            external_row = pd.DataFrame([{'bank': EXTERNAL_BANK_NAME, 'inflow': external_outflow_total, 'outflow': 0}])
            df_network = pd.concat([df_network, external_row], ignore_index=True)

        # Final Calculation
        df_network['net_value'] = df_network['inflow'] - df_network['outflow']
        df_network['total_value'] = df_network['inflow'] + df_network['outflow']

        bank_metrics = df_network.set_index('bank').to_dict('index')

    bank_cards = []

    # Generate the complete list of banks for display
    display_banks = internal_banks_list
    if external_outflow_total > 0:
        display_banks.append(EXTERNAL_BANK_NAME)

    for bank in sorted(display_banks):
        metrics = bank_metrics.get(bank, {'inflow': 0, 'outflow': 0, 'net_value': 0, 'total_value': 0})

        # Condition to suppress the card if it's the external placeholder and has no activity (already fixed above, but safe to repeat)
        if bank == EXTERNAL_BANK_NAME and metrics['total_value'] == 0:
            continue

        if metrics['total_value'] == 0:
            status_text = "Active"
            status_color = "primary"
        else:
            status_text = "Net Positive" if metrics['net_value'] > 0 else "Net Negative" if metrics[
                                                                                                'net_value'] < 0 else "Balanced"
            # Use brand colors for status text
            status_color = "success" if metrics['net_value'] > 0 else "danger" if metrics['net_value'] < 0 else "muted"

        card = dbc.Col(dbc.Card([
            dbc.CardHeader(html.Div([html.I(className="fas fa-university me-2"), html.Span(bank)],
                                    className="d-flex align-items-center")),
            dbc.CardBody([
                html.P([f"Status: ", html.Span(status_text, className=f"text-{status_color} fw-bold small")]),

                # Use requested metric names
                html.Div([
                    html.P([html.I(className="fas fa-arrow-circle-down me-2", style={'color': CP_SECONDARY}), "Transacted amount: ",
                            format_currency(metrics['inflow'])], className="mb-1 small"),
                    html.P([html.I(className="fas fa-arrow-circle-up me-2", style={'color': CP_PRIMARY}), "Outgoing Cash Flow: ",
                            format_currency(metrics['outflow'])], className="mb-1 small"),
                ], className="border-bottom pb-2 mb-2"),

                html.Div([
                    # Display Total Value - Color set to CP_ACCENT_PURPLE for prominence
                    html.H5(format_currency(metrics['total_value']), 
                            style={'color': CP_ACCENT_PURPLE},
                            className=f"fw-bold d-inline me-2"),
                    html.Small("Total Value (7-Day)", className="text-muted d-inline")
                ]),
                html.Div([
                    # Display Cash Flow (Net Value)
                    html.H5(format_currency(metrics['net_value']),
                            className=f"fw-bold text-{status_color} d-inline me-2"),
                    html.Small("Cash Flow (Net) (7-Day)", className="text-muted d-inline")
                ])
            ])
        ], outline=True, color="secondary"), md=4, lg=3, className="mb-3")
        bank_cards.append(card)

    return dbc.Row([
        dbc.Col(dbc.Card(
            [dbc.CardHeader(html.H4("Connected Banking Network Performance")), dbc.CardBody(dbc.Row(bank_cards))]),
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
    
    # *** Global definition ensures the object always exists in the layout ***
    dcc.Store(id='payroll-table-data-store-aux', data=None), 

    dbc.Toast(
        id="payment-toast-notification",
        header="Payment Successful",
        icon="success",
        is_open=False,
        dismissable=True,
        duration=6000,
        style={"position": "fixed", "top": 20, "right": 10, "width": 350, "zIndex": 9999},
    ),

    dcc.Store(id='ipn-trigger-store', data=None),

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
    html.Div(id='page-content'),
    
    create_footer()

], className="app-container py-4", fluid=True)


# ==============================================================================
# AUXILIARY CALLBACK TO FIX CROSS-PAGE OUTPUT ERROR
# ==============================================================================
@app.callback(
    Output('payroll-table', 'data', allow_duplicate=True),
    Input('payroll-table-data-store-aux', 'data'),
    prevent_initial_call=True
)
def update_payroll_table_data_safely(data):
    """Updates the payroll table data only when the table component exists."""
    if isinstance(data, list):
        return data
    return no_update


# ==============================================================================
# REST OF THE CALLBACKS
# ==============================================================================
@app.callback(
    [Output('page-content', 'children'),
     Output('current-view-store', 'data')],
    Input('url', 'pathname'),
    Input('transaction-refresh-signal', 'data')
)
def display_page(pathname, refresh_signal):
    triggered_id = callback_context.triggered_id
    view = (pathname or "/").strip("/").split("/")[-1]
    if not view: view = 'transfer'

    if triggered_id == 'transaction-refresh-signal' and view == 'dashboard':
        return create_dashboard(), view

    if view == 'payroll':
        return create_payroll_section(), view
    elif view == 'transactions':
        return create_transactions_view(), view
    elif view == 'dashboard':
        return create_dashboard(), view
    elif view == 'analytics':
        return create_analytics_view(), view
    else:
        return create_transfer_form(), 'transfer'


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


@app.callback(
    Output('uploaded-data-store', 'data'),
    [Input('upload-payroll-data', 'contents')],
    [State('upload-payroll-data', 'filename')],
    prevent_initial_call=True
)
def parse_uploaded_file_payroll(contents, filename):
    if contents:
        parsed_data = parse_contents(contents, filename)
        if isinstance(parsed_data, list):
            return parsed_data
    return None


@app.callback(
    [Output('payroll-table', 'data', allow_duplicate=True),
     Output('payroll-temp-data-store', 'data', allow_duplicate=True),
     Output('upload-alert-container', 'children')],
    [Input('employee-selection-dropdown', 'value'),
     Input('add-payroll-row-btn', 'n_clicks'),
     Input('uploaded-data-store', 'data'),
     Input('payroll-table', 'data')],
    [State('payroll-mode-radios', 'value'),
     State('payroll-temp-data-store', 'data')],
    prevent_initial_call=True
)
def handle_payroll_data_input(employee_ids, add_row_n_clicks, uploaded_data, table_data_in, mode, current_data_store):
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update

    trig_id = ctx.triggered[0]['prop_id'].split('.')[0]

    new_data = no_update
    alert = no_update

    if mode == 'select' and trig_id == 'employee-selection-dropdown':
        if not employee_ids:
            new_data = []
        else:
            # Added account number and placeholders for email
            placeholders = ','.join(['?'] * len(employee_ids))
            query = f"SELECT name AS clientName, bank AS clientBank, account AS clientAccountNum, '' AS clientEmail, account AS clientMSISDN, 'N/A' AS clientIDNumber, amount AS amountExpected, 'Monthly Salary' AS billDesc FROM master_employees WHERE id IN ({placeholders})"
            with get_db_connection() as conn:
                df = pd.read_sql_query(query, conn, params=employee_ids)
            new_data = df.to_dict('records')
        return new_data, new_data, no_update

    elif mode == 'manual' and trig_id == 'add-payroll-row-btn':
        data_to_use = current_data_store if current_data_store is not None else []
        new_row = {'clientName': 'Jane Doe', 'clientBank': 'Equity Bank', 'clientAccountNum': '123456789',
                   'clientEmail': 'jane@example.com', 'clientMSISDN': '0712345678', 'clientIDNumber': 'ID-3459012',
                   'amountExpected': 5700.0,
                   'billDesc': 'Salary'}
        new_data = data_to_use + [new_row]
        return new_data, new_data, no_update

    elif mode == 'upload' and trig_id == 'uploaded-data-store':
        if uploaded_data and isinstance(uploaded_data, list):
            new_data = uploaded_data
            alert = dbc.Alert(f"Successfully loaded {len(new_data)} rows for preview. Review below before processing.",
                              color="success", dismissable=True)
            return new_data, new_data, alert
        elif uploaded_data is None:
            return [], [], no_update

    elif trig_id == 'payroll-table' and table_data_in is not None and mode in ['manual', 'upload']:
        return no_update, table_data_in, no_update

    return no_update, no_update, no_update


@app.callback(
    [Output('payroll-input-select', 'style'),
     Output('payroll-input-upload', 'style'),
     Output('payroll-input-manual', 'style'),
     Output('payroll-temp-data-store', 'data', allow_duplicate=True),
     Output('upload-alert-container', 'children', allow_duplicate=True)],
    Input('payroll-mode-radios', 'value'),
    prevent_initial_call='initial_duplicate'
)
def switch_payroll_mode(mode):
    select_style = upload_style = manual_style = {'display': 'none'}

    if mode == 'select':
        select_style = {'display': 'block'}
    elif mode == 'upload':
        upload_style = {'display': 'block'}
    elif mode == 'manual':
        manual_style = {'display': 'block'}

    return select_style, upload_style, manual_style, [], None


@app.callback(
    [Output('process-payroll-btn-select', 'disabled'),
     Output('process-payroll-btn-upload', 'disabled'),
     Output('process-payroll-btn-manual', 'disabled'),
     Output('payroll-popover', 'target'),
     Output('process-payroll-btn-default', 'style'),
     Output('process-payroll-btn-select', 'style'),
     Output('process-payroll-btn-upload', 'style'),
     Output('process-payroll-btn-manual', 'style')],
    [Input('payroll-table', 'data'),
     Input('payroll-mode-radios', 'value')]
)
def toggle_process_payroll_buttons(data, mode):
    is_data_valid = False
    if data:
        try:
            is_data_valid = not any(float(row.get('amountExpected', 0) or 0) <= 0 for row in data)
        except:
            is_data_valid = False

    disabled_state = not is_data_valid

    default_style = {'display': 'none'}
    select_style = {'display': 'none'}
    upload_style = {'display': 'none'}
    manual_style = {'display': 'none'}
    target_id = "process-payroll-btn-default"

    if mode == 'select':
        select_style = {'display': 'block'}
        target_id = "process-payroll-btn-select"
    elif mode == 'upload':
        upload_style = {'display': 'block'}
        target_id = "process-payroll-btn-upload"
    elif mode == 'manual':
        manual_style = {'display': 'block'}
        target_id = "process-payroll-btn-manual"
    else:
        default_style = {'display': 'block'}

    return [disabled_state, disabled_state, disabled_state, target_id,
            default_style, select_style, upload_style, manual_style]


@app.callback(
    Output('payroll-summary', 'children'),
    Input('payroll-table', 'data')
)
def update_payroll_summary(data):
    if not data:
        return "Total Payroll: TZs 0.00"

    try:
        valid_data = [row for row in data if float(row.get('amountExpected', 0) or 0) > 0]
        total_amount = sum(float(row['amountExpected']) for row in valid_data)
        num_employees = len(valid_data)
        return html.Div([
            html.Span(f"Employees: {num_employees} | ", className="me-2"),
            html.Span(f"Total Payroll: {format_currency(total_amount)}")
        ])
    except:
        return html.Div("Error calculating summary. Check amount column for non-numeric data.", className="text-danger")


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
    if not all([s_name, s_acct, r_name, r_acct, amount]):
        return True
    try:
        return float(amount) <= 0
    except:
        return True


@app.callback(
    [Output('passphrase-modal', 'is_open', allow_duplicate=True),
     Output('passphrase-summary-body', 'children', allow_duplicate=True),
     Output('pending-transaction-store', 'data', allow_duplicate=True),
     Output('transfer-popover', 'is_open'),
     Output('load-sender-dropdown', 'options'),
     Output('load-recipient-dropdown', 'options'),
     Output('passphrase-alert-container', 'children')],
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
    if amount is None or float(amount) <= 0:
        return False, no_update, no_update, False, no_update, no_update, dbc.Alert("Amount must be greater than zero.",
                                                                                   color="warning")

    with get_db_connection() as conn:
        recipient_check = conn.execute("SELECT id FROM accounts WHERE accountNumber = ?", (r_acct,)).fetchone()
        if not recipient_check:
            return False, no_update, no_update, False, no_update, no_update, dbc.Alert(
                f"Recipient account number {r_acct} not found in our network. (Transfers only work for existing accounts)",
                color="danger")

        sender_check = conn.execute("SELECT id, type, balance FROM accounts WHERE accountNumber = ?", (s_acct,)).fetchone()
        if not sender_check:
            return False, no_update, no_update, False, no_update, no_update, dbc.Alert(
                f"Sender account number {s_acct} not found in our network. (Transfers must originate from an existing account)",
                color="danger")
        
        # A2A logic bypasses the pre-check for limits as requested.
        
        sender_options, recipient_options = no_update, no_update
        if save_sender and s_name:
            conn.execute(
                "INSERT OR REPLACE INTO saved_senders (name, msisdn, id_number, email, bank_name, bank_account_number) VALUES (?, ?, ?, ?, ?, ?)",
                (s_name, s_msisdn, s_id, s_email, s_bank, s_acct))
            senders = conn.execute("SELECT id, name FROM saved_senders ORDER BY name").fetchall()
            sender_options = [{'label': s['name'], 'value': s['id']} for s in senders]

        if save_recipient and r_name:
            conn.execute(
                "INSERT OR REPLACE INTO saved_recipients (name, msisdn, id_number, email, bank_name, bank_account_number) VALUES (?, ?, ?, ?, ?, ?)",
                (r_name, r_msisdn, r_id, r_email, r_bank, r_acct))
            recipients = conn.execute("SELECT id, name FROM saved_recipients ORDER BY name").fetchall()
            recipient_options = [{'label': r['name'], 'value': r['id']} for r in recipients]
        conn.commit()

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

    return True, summary_list, data, False, sender_options, recipient_options, None


@app.callback(
    [Output('passphrase-modal', 'is_open', allow_duplicate=True),
     Output('passphrase-summary-body', 'children', allow_duplicate=True),
     Output('pending-transaction-store', 'data', allow_duplicate=True),
     Output('payroll-popover', 'is_open')],
    [Input('confirm-payroll-popover-btn', 'n_clicks'),
     Input('process-payroll-btn-select', 'n_clicks'),
     Input('process-payroll-btn-upload', 'n_clicks'),
     Input('process-payroll-btn-manual', 'n_clicks')],
    State('payroll-table', 'data'),
    prevent_initial_call=True
)
def handle_payroll_confirmation(popover_clicks, select_clicks, upload_clicks, manual_clicks, p_data):
    ctx = callback_context
    trig_id = ctx.triggered_id

    if trig_id != 'confirm-payroll-popover-btn':
        if not p_data: return no_update, no_update, no_update, False

        try:
            valid_data = [row for row in p_data if float(row.get('amountExpected', 0) or 0) > 0]
            if not valid_data: return no_update, no_update, no_update, False
        except:
            return no_update, no_update, no_update, False

        return False, no_update, no_update, True

    if not p_data:
        return False, no_update, no_update, False

    try:
        valid_data = [row for row in p_data if float(row.get('amountExpected', 0) or 0) > 0]
        if not valid_data:
            return False, no_update, no_update, False

        total_amount = sum(float(row['amountExpected']) for row in valid_data)
        num_employees = len(valid_data)
        ref = f'PAYROLL-{uuid.uuid4().hex[:6].upper()}'

        data = {'type': 'payroll', 'ref': ref, 'total_amount': total_amount, 'batch_data': valid_data}

        summary_list = dbc.ListGroup([
            dbc.ListGroupItem(f"Employees: {num_employees}", className="text-info fw-bold"),
            dbc.ListGroupItem(f"Reference: {ref}"),
            dbc.ListGroupItem(f"Total Amount: {format_currency(total_amount)}", color="primary",
                              className="fw-bold fs-5"),
        ], flush=True)

        return True, summary_list, data, False
    except:
        return False, no_update, no_update, False


@app.callback(
    [Output('pin-modal', 'is_open'),
     Output('passphrase-modal', 'is_open', allow_duplicate=True),
     Output('passphrase-alert-container', 'children', allow_duplicate=True),
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
     Output('current-pin-store', 'data', allow_duplicate=True),
     Output('interval-component', 'disabled', allow_duplicate=True),
     Output('animation-interval', 'disabled', allow_duplicate=True),
     Output('animation-step-store', 'data', allow_duplicate=True)],
    Input('current-pin-store', 'data'),
    prevent_initial_call=True
)
def process_payment_precheck(pin):
    if not pin or len(pin) != 4:
        return [no_update] * 7

    if pin != '1234':
        body = create_processing_animation(status='failed', message="Invalid PIN. Please try again.")
        return True, body, False, '', True, True, 0

    return True, create_processing_animation(step=0), False, '', True, False, 0


@app.callback(
    [Output('processing-body', 'children', allow_duplicate=True),
     Output('animation-step-store', 'data', allow_duplicate=True),
     Output('animation-interval', 'disabled', allow_duplicate=True),
     Output('interval-component', 'disabled', allow_duplicate=True),
     Output('transaction-refresh-signal', 'data', allow_duplicate=True),
     Output('ipn-trigger-store', 'data', allow_duplicate=True),
     Output('payroll-table-data-store-aux', 'data', allow_duplicate=True)],
    Input('animation-interval', 'n_intervals'),
    [State('animation-step-store', 'data'),
     State('pending-transaction-store', 'data'),
     State('current-view-store', 'data')],
    prevent_initial_call=True
)
def update_animation_step(n, current_step, data, current_view):
    if n == 0: return [no_update] * 7

    next_step = current_step + 1
    number_of_animation_steps = 4

    if next_step < number_of_animation_steps:
        new_body = create_processing_animation(step=next_step)
        return new_body, next_step, False, True, no_update, no_update, no_update

    is_success, msg = False, "Unknown Error"
    now_iso = datetime.datetime.now(pytz.timezone('Africa/Nairobi')).isoformat()
    
    payroll_store_update = [] if data.get('type') == 'payroll' and current_view == 'payroll' else no_update
    payroll_store_output = payroll_store_update if data.get('type') == 'payroll' else no_update

    try:
        with get_db_connection() as conn:
            if data['type'] == 'transfer':
                payload = data['payload']
                amount = float(payload['amountExpected'])
                
                # Fetch account details for ID and balance
                sender_acct = conn.execute("SELECT id, balance, type FROM accounts WHERE accountNumber = ?",
                                           (payload['senderAccount'],)).fetchone()
                receiver_acct = conn.execute("SELECT id, type FROM accounts WHERE accountNumber = ?",
                                             (payload['clientAccount'],)).fetchone()

                if not sender_acct or not receiver_acct: raise ValueError(
                    "Sender or Recipient account not found in system.")
                
                # A2A TRANSFER: No explicit limit enforced here as requested.
                
                conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, sender_acct['id']))
                conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, receiver_acct['id']))
                conn.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                    payload['billRefNumber'], sender_acct['id'], receiver_acct['id'], amount, 'transfer', 'completed',
                    now_iso, 'A2A-INTERNAL'))

            elif data['type'] == 'payroll':
                ref = data['ref']
                total_amount = float(data['total_amount'])
                batch_data = data['batch_data']
                from_acct = 'acc003'

                bal = conn.execute("SELECT balance FROM accounts WHERE id = ?", (from_acct,)).fetchone()[0]
                if bal < total_amount: raise ValueError("Insufficient corporate funds for bulk payroll.")

                conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (total_amount, from_acct))

                conn.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                    ref, from_acct, 'EXTERNAL_BULK', total_amount, 'payroll', 'completed', now_iso, 'API-Bulk'))

                for i, record in enumerate(batch_data):
                    pay_ref = f"{ref}-{i + 1}"
                    pay_amount = float(record['amountExpected'])
                    recipient_bank = record.get('clientBank', 'External Bank')

                    conn.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                        pay_ref, from_acct, 'EXTERNAL_PAYEE', pay_amount, 'payroll', 'completed', now_iso,
                        f'API-Individual_{recipient_bank}'))

            conn.commit()
            is_success = True

    except (sqlite3.Error, ValueError, TypeError, IndexError) as e:
        print(f"Transaction failed: {e}")
        msg = str(e)

    if is_success:
        final_body = create_processing_animation(step=number_of_animation_steps)
        return final_body, next_step, True, False, datetime.datetime.now().isoformat(), data, payroll_store_output
    else:
        fail_body = create_processing_animation(status='failed', message=msg)
        return fail_body, next_step, True, False, no_update, no_update, no_update


@app.callback(
    [Output('senderName-input', 'value', allow_duplicate=True),
     Output('clientName-input', 'value', allow_duplicate=True),
     Output('amountExpected-input', 'value', allow_duplicate=True),
     Output('billDesc-input', 'value', allow_duplicate=True)],
    Input('ipn-trigger-store', 'data'),
    State('current-view-store', 'data'),
    prevent_initial_call=True
)
def reset_transfer_form_on_success(transaction_data, current_view):
    if transaction_data and transaction_data.get('type') == 'transfer' and current_view == 'transfer':
        return '', '', None, ''
    return no_update, no_update, no_update, no_update


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


@app.callback(
    [Output('payment-toast-notification', 'is_open'),
     Output('payment-toast-notification', 'children'),
     Output('payment-toast-notification', 'header')],
    Input('ipn-trigger-store', 'data'),
    prevent_initial_call=True
)
def display_payment_notification(transaction_data):
    if not transaction_data:
        return False, no_update, no_update

    if transaction_data.get('type') == 'transfer':
        payload = transaction_data.get('payload', {})
        amount = payload.get('amountExpected', 0)
        recipient = payload.get('clientName', 'the recipient')
        message = f"Successfully sent {format_currency(amount)} to {recipient}."
        header = "Transfer Successful"
    elif transaction_data.get('type') == 'payroll':
        amount = transaction_data.get('total_amount', 0)
        message = f"Successfully processed payroll for a total of {format_currency(amount)}."
        header = "Bulk Payroll Processed"
    else:
        return False, no_update, no_update

    return True, message, header


@app.callback(
    Output('all-transactions-content', 'children'),
    Output('transfer-transactions-content', 'children'),
    Output('payroll-transactions-content', 'children'),
    Input('transaction-refresh-signal', 'data'),
    Input('url', 'pathname')
)
def update_transaction_tables(refresh_signal, pathname):
    is_transaction_page = 'transactions' in (pathname or '')
    is_triggered_by_refresh = callback_context.triggered_id == 'transaction-refresh-signal'

    if not is_transaction_page and not is_triggered_by_refresh:
        return no_update, no_update, no_update

    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY timestamp DESC", conn)

    if df.empty:
        no_data_msg = html.Div("No transactions found.", className="text-center text-muted p-4")
        return no_data_msg, no_update, no_update

    # --- UPDATED: Retrieve and use the names for From and To columns ---
    
    # 1. Get descriptive names for 'From'
    df['From_Name'] = df['from_acct'].apply(get_account_name)

    # 2. Get descriptive names for 'To'
    def get_to_name_and_bank(row):
        if row['to_acct'] == 'EXTERNAL_PAYEE' and row['method'].startswith('API-Individual_'):
            bank_name = row['method'].split('API-Individual_')[-1]
            return f"External Payee ({bank_name})"
        return get_account_name(row['to_acct'])

    df['To_Name'] = df.apply(get_to_name_and_bank, axis=1)

    df['amount'] = df['amount'].apply(format_currency)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

    df.rename(columns={
        'id': 'Reference', 'From_Name': 'From (Sender)', 'To_Name': 'To (Recipient)', 'amount': 'Amount',
        'type': 'Type', 'status': 'Status', 'timestamp': 'Timestamp'
    }, inplace=True)
    
    # Define columns to display, excluding the raw account IDs and 'method'
    display_cols = ['Reference', 'From (Sender)', 'To (Recipient)', 'Amount', 'Type', 'Status', 'Timestamp']
    
    table_style = {
        'style_cell': {'textAlign': 'left', 'padding': '10px', 'fontFamily': 'sans-serif', 'border': '1px solid #eee'},
        'style_header': {'backgroundColor': '#f8f9fa', 'fontWeight': 'bold', 'borderBottom': '2px solid #dee2e6'},
        'style_data_conditional': [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
        'page_size': 10,
        'style_table': {'overflowX': 'auto'}
    }

    df_all_display = df[df['Type'].isin(['transfer', 'payroll'])][display_cols]
    df_transfer_display = df[df['Type'] == 'transfer'][display_cols]
    df_payroll_display = df[df['Type'] == 'payroll'][display_cols]

    columns_config = [{'name': i, 'id': i} for i in display_cols]

    all_table = dash_table.DataTable(data=df_all_display.to_dict('records'),
                                     columns=columns_config,
                                     **table_style)
    transfer_table = dash_table.DataTable(data=df_transfer_display.to_dict('records'),
                                          columns=columns_config,
                                          **table_style)
    payroll_table = dash_table.DataTable(data=df_payroll_display.to_dict('records'),
                                         columns=columns_config,
                                         **table_style)

    return all_table, transfer_table, payroll_table


@app.callback(
    Output('kpi-cards', 'children'),
    Output('payroll-by-dept-chart', 'figure'),
    Output('transfer-dist-chart', 'figure'),
    Output('monthly-trends-chart', 'figure'),
    Output('top-transfer-banks-chart', 'figure'),
    Output('transaction-type-pie', 'figure'),
    Output('amount-vs-time-scatter', 'figure'),
    Input('url', 'pathname'),
    Input('transaction-refresh-signal', 'data')
)
def update_analytics_page(pathname, refresh_signal):
    is_analytics_page = 'analytics' in (pathname or '')
    is_triggered_by_refresh = callback_context.triggered_id == 'transaction-refresh-signal'

    if not is_analytics_page and not is_triggered_by_refresh:
        return [no_update] * 7

    with get_db_connection() as conn:
        total_volume = conn.execute("SELECT SUM(amount) FROM transactions WHERE status='completed'").fetchone()[0] or 0
        total_transactions = conn.execute("SELECT COUNT(*) FROM transactions WHERE status='completed'").fetchone()[
                                 0] or 0
        avg_transfer = \
            conn.execute(
                "SELECT AVG(amount) FROM transactions WHERE status='completed' AND type='transfer'").fetchone()[
                0] or 0
        df_payroll = pd.read_sql_query(
            "SELECT department, SUM(amount) as total_payroll FROM master_employees GROUP BY department", conn)
        df_trends = pd.read_sql_query(
            "SELECT STRFTIME('%Y-%m', timestamp) as month, SUM(amount) as volume FROM transactions WHERE status='completed' GROUP BY month ORDER BY month ASC",
            conn)

        inflow_query = f"""
            SELECT a.bank, SUM(t.amount) as volume
            FROM transactions t
            JOIN accounts a ON t.to_acct = a.id
            WHERE t.status='completed' AND t.to_acct NOT IN ('EXTERNAL_BULK', 'EXTERNAL_PAYEE', 'acc003')
            GROUP BY a.bank
            ORDER BY volume DESC 
            LIMIT 5
        """
        df_banks = pd.read_sql_query(inflow_query, conn)

        df_trans_full = pd.read_sql_query("SELECT amount, timestamp, type FROM transactions WHERE status='completed'",
                                          conn)

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

    plot_template = 'plotly_white'
    # Use brand colors for chart elements
    
    fig_payroll = px.bar(df_payroll, x='department', y='total_payroll', title="Payroll Costs by Department",
                         labels={'department': 'Department', 'total_payroll': 'Total Payroll Amount'},
                         template=plot_template, color_discrete_sequence=[CP_SECONDARY, CP_ACCENT_PURPLE, CP_PRIMARY])
    
    bins = [0, 10000, 50000, 100000, float('inf')]
    labels = ['< 10k', '10k - 50k', '50k - 100k', '> 100k']
    df_trans_full['range'] = pd.cut(df_trans_full['amount'], bins=bins, labels=labels, right=False)
    dist_data = df_trans_full['range'].value_counts().reset_index()
    fig_dist = px.pie(dist_data, names='range', values='count', title="Distribution of Transaction Sizes", hole=.3,
                      template=plot_template, color_discrete_sequence=[CP_PRIMARY, CP_ACCENT_ORANGE, CP_SECONDARY, CP_ACCENT_PURPLE])
    
    fig_trends = px.line(df_trends, x='month', y='volume', title="Monthly Transaction Volume", markers=True,
                         labels={'month': 'Month', 'volume': 'Transaction Volume'}, template=plot_template,
                         color_discrete_sequence=[CP_ACCENT_PURPLE])
    
    fig_banks = px.bar(df_banks, x='bank', y='volume', title="Top 5 Banks by Inbound Volume (Internal Transfers)",
                       labels={'bank': 'Bank', 'volume': 'Inbound Volume'}, template=plot_template, 
                       color_discrete_sequence=[CP_SECONDARY])
                       
    type_counts = df_trans_full['type'].str.capitalize().value_counts().reset_index()
    fig_type_pie = px.pie(type_counts, names='type', values='count', title='Transaction Count by Type', hole=0.3,
                          template=plot_template, color_discrete_sequence=[CP_PRIMARY, CP_SECONDARY])
                          
    df_trans_full['timestamp'] = pd.to_datetime(df_trans_full['timestamp'])
    df_trans_full['Type_Capitalized'] = df_trans_full['type'].str.capitalize()
    fig_scatter = px.scatter(df_trans_full, x='timestamp', y='amount', color='Type_Capitalized',
                             title='Transaction Amount vs. Time',
                             labels={'timestamp': 'Date', 'amount': 'Amount (TZs)', 'color': 'Type'},
                             hover_data={'amount': ':.2f'}, template=plot_template,
                             color_discrete_map={'Transfer': CP_PRIMARY, 'Payroll': CP_SECONDARY})
                             
    for fig in [fig_payroll, fig_dist, fig_trends, fig_banks, fig_type_pie, fig_scatter]:
        fig.update_layout(title_x=0.5, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
        fig.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')), 
                          selector=dict(mode='markers')) # Style scatter markers for visibility

    return kpi_cards, fig_payroll, fig_dist, fig_trends, fig_banks, fig_type_pie, fig_scatter


if __name__ == '__main__':
    pd.set_option('future.no_silent_downcasting', True)
    app.run(debug=True, port=8899)


