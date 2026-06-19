import gmail_client
from gmail_client import build_query
import re
from datetime import datetime
from collections import Counter

from constants import (
    PAID_QUERY_PARAMS,
    REQUEST_QUERY_PARAMS,
    PAID_CHARGE_QUERY_PARAMS,
    PAYMENT_QUERY_PARAMS
)

#take all you paid subjects and then run this regex pattern on it to get relevant messages pattern = r"You paid ([\w\s]+) \$([\d,.]+)"
def extract_requests(requestMessages):
    stored_requests = []

    # Regex pattern to extract name and amount from subject
    pattern = re.compile(r"([\w\s]+) requests \$([\d,.]+)")
    # preview_pattern = re.compile(r"requests\s+\$[\d\s,.]+\s+([\w\s]+?)\s+See Request") doesnt work for emoji
    preview_pattern = re.compile(r"requests\s+\$\s+\d+\s+\.\s+\d+\s+(.+?)\s+See")


    for message in requestMessages:
        # Apply regex to check if the subject is a request
        match = pattern.search(message.subject)
        preview_match = preview_pattern.search(message.snippet)

        if match:
            # Store the relevant information
            stored_requests.append({
                "name": match.group(1).strip(),
                "amount": float(match.group(2).replace(",", "")),
                "requestedItem": preview_match.group(1).strip() if preview_match else "Emoji probably present",
                "dateRequested": message.date,
                "datePaid": None,
                "dateDifferenceSeconds": None
            })
    
    return stored_requests    

def update_paid_message(paidMessages, all_transactions, paid_events):
    name_pattern = re.compile(r"You paid ([\w\s]+) \$([\d,.]+)")
    amount_pattern = re.compile(r"You paid [\w\s]+ \$([\d,.]+)")
    item_pattern = re.compile(r"You paid .+ \$ \d+ \. \d+ (.+?) See transaction")
    for paidMessage in paidMessages:
        # Extract name and amount from the subject
        name_match = name_pattern.search(paidMessage.subject)
        amount_match = amount_pattern.search(paidMessage.subject)
        item_match = item_pattern.search(paidMessage.snippet)

        if name_match and amount_match:
            paid_name = name_match.group(1).strip()
            paid_amount = float(amount_match.group(1).replace(",", ""))

            all_transactions.append({
                "name": paid_name,
                "amount": paid_amount,
                "dateRequested": paidMessage.date,
                "theyPaidYou": False,
                "item": item_match.group(1).strip() if item_match else "Emoji probably present",
            })
            paid_events.append({"name": paid_name, "amount": paid_amount, "date": paidMessage.date})

def update_paid_charge_message(paidMessages, all_transactions, paid_events):
    name_pattern_charge_request = re.compile(r"You completed (.+?)'s \$[\d.]+? charge request")
    amount_pattern_charge_request = re.compile(r"\$(\d+(?:\.\d{2})?)")
    item_pattern = re.compile(r"charged You (.+?) Transfer Date")
    for paidMessage in paidMessages:
        # Extract name and amount from the subject
        name_match = name_pattern_charge_request.search(paidMessage.subject)
        amount_match = amount_pattern_charge_request.search(paidMessage.subject)
        item_match = item_pattern.search(paidMessage.snippet)

        if name_match and amount_match:
            paid_name = name_match.group(1).strip()
            paid_amount = float(amount_match.group(1).replace(",", ""))

            all_transactions.append({
                "name": paid_name,
                "amount": paid_amount,
                "dateRequested": paidMessage.date,
                "theyPaidYou": False,
                "item": item_match.group(1).strip() if item_match else "Emoji probably present",
            })
            paid_events.append({"name": paid_name, "amount": paid_amount, "date": paidMessage.date})

def match_payments_to_requests(request_messages, paid_events):
    """Match each request to the earliest payment of the same name+amount that
    occurred at or after the request, using each payment at most once.

    This avoids matching a request to an unrelated earlier payment (which
    produced negative/garbage payback times). Sets datePaid and
    dateDifferenceSeconds on matched requests.
    """
    events = sorted(paid_events, key=lambda e: datetime.fromisoformat(e['date']))
    used = [False] * len(events)

    for request in sorted(request_messages, key=lambda r: datetime.fromisoformat(r['dateRequested'])):
        req_dt = datetime.fromisoformat(request['dateRequested'])
        for i, event in enumerate(events):
            if used[i]:
                continue
            if event['name'] != request['name'] or event['amount'] != request['amount']:
                continue
            if datetime.fromisoformat(event['date']) >= req_dt:
                used[i] = True
                request['datePaid'] = event['date']
                request['dateDifferenceSeconds'] = (
                    datetime.fromisoformat(event['date']) - req_dt
                ).total_seconds()
                break

def average_payback_time(request_messages):
    # Average only over requests that were actually matched to a payment.
    matched = [r for r in request_messages if r['dateDifferenceSeconds'] is not None]
    if not matched:
        return 0
    return sum(r['dateDifferenceSeconds'] for r in matched) / len(matched)

def extact_payments(paymentMessages, all_transactions):
    stored_payments = []
    #regex doesn't work for ariana case where value is 1,691.00
    # name_and_amount_pattern = r"(.+?) paid (?:you|your) \$(\d+(?:\.\d{2})?)(?:\s+request)?"
    name_and_amount_pattern = r"(.+?) paid (?:you|your) \$([\d,]+(?:\.\d{2})?)(?:\s+request)?"
    item_pattern = r"paid you \$ \d+ \. \d+ (.+?) See transaction"
    for payment in paymentMessages:
        # Extract name and amount from the subject
        name_and_amount_match = re.search(name_and_amount_pattern, payment.subject, re.IGNORECASE)
        item_match = re.search(item_pattern, payment.snippet, re.IGNORECASE)
        if name_and_amount_match:
            stored_payments.append({
                "name": name_and_amount_match.group(1).strip(),
                "amount": float(name_and_amount_match.group(2).replace(",", "")),
                "requestedItem": item_match.group(1).strip() if item_match else "Emoji probably present",
                "dateRequested": payment.date,
                "datePaid": None,
                "dateDifferenceSeconds": None
            })
            all_transactions.append({
                "name": name_and_amount_match.group(1).strip(),
                "amount": float(name_and_amount_match.group(2).replace(",", "")),
                "dateRequested": payment.date,
                "theyPaidYou": True,
                "item": item_match.group(1).strip() if item_match else "Emoji probably present",
            })
    return stored_payments

def get_top_transactions(transactions, they_paid=True):
    # Filter transactions by who paid
    filtered_transactions = [t for t in transactions if t['theyPaidYou'] == they_paid]
    
    # Count transactions by name and amount
    name_totals = {}
    for t in filtered_transactions:
        name = t['name']
        amount = t['amount']
        name_totals[name] = name_totals.get(name, 0) + amount
    
    # Sort by total amount and get top 3
    top_3 = sorted(name_totals.items(), key=lambda x: x[1], reverse=True)[:3]
    return [{
        'name': name,
        'total_amount': round(amount, 2),
        'transaction_count': sum(1 for t in filtered_transactions if t['name'] == name)
    } for name, amount in top_3]

def calculate_monthly_totals(all_transactions):
    from datetime import datetime
    
    monthly_totals = {}
    
    for transaction in all_transactions:
        date_obj = datetime.fromisoformat(transaction['dateRequested'])
        year_month = date_obj.strftime('%Y-%m')
        
        # if month doesn't exist, create it
        if year_month not in monthly_totals:
            monthly_totals[year_month] = {
                'month': year_month,
                'moneySpent': 0,
                'moneyReceived': 0,
                'totalBalance': 0
            }
        
        if transaction['theyPaidYou']:
            monthly_totals[year_month]['moneyReceived'] += transaction['amount']
        else:
            monthly_totals[year_month]['moneySpent'] += transaction['amount']
        
        monthly_totals[year_month]['totalBalance'] = (
            monthly_totals[year_month]['moneyReceived'] - 
            monthly_totals[year_month]['moneySpent']
        )
    
    monthly_list = list(monthly_totals.values())
    monthly_list.sort(key=lambda x: x['month'])
    return monthly_list

def _windowed(params, months):
    """Copy a query-param dict with a different time window."""
    p = dict(params)
    p['newer_than'] = (months, 'month')
    return p


def fetch_transactions(service, months=12):
    """Fetch and parse Venmo emails from Gmail for the last `months` months.

    `service` is a Gmail API service (see gmail_client.build_service).

    Returns the raw parsed data (requests + all transactions) WITHOUT
    aggregation, so it can be cached once and then sliced into smaller
    time windows (1m / 6m / 1y) without re-scanning Gmail.
    """
    paid_messages = gmail_client.search_messages(service, build_query(_windowed(PAID_QUERY_PARAMS, months)))
    paid_charge_messages = gmail_client.search_messages(service, build_query(_windowed(PAID_CHARGE_QUERY_PARAMS, months)))

    all_transactions = []
    paid_events = []
    requests = extract_requests(gmail_client.search_messages(service, build_query(_windowed(REQUEST_QUERY_PARAMS, months))))
    extact_payments(gmail_client.search_messages(service, build_query(_windowed(PAYMENT_QUERY_PARAMS, months))), all_transactions)

    # record your payments (for the table) and collect them as events
    update_paid_message(paid_messages, all_transactions, paid_events)
    update_paid_charge_message(paid_charge_messages, all_transactions, paid_events)

    # match payments back to the requests that prompted them (temporal, 1:1)
    match_payments_to_requests(requests, paid_events)

    return {'requests': requests, 'allTransactions': all_transactions}


def filter_window(data, days):
    """Slice cached data down to transactions within the last `days` days."""
    from datetime import timezone, timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    def recent(items):
        kept = []
        for item in items:
            try:
                d = datetime.fromisoformat(item['dateRequested'])
            except (ValueError, KeyError, TypeError):
                continue
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            if d >= cutoff:
                kept.append(item)
        return kept

    return {
        'requests': recent(data.get('requests', [])),
        'allTransactions': recent(data.get('allTransactions', [])),
    }


def aggregate_transactions(requests, all_transactions):
    """Compute the dashboard stats from parsed requests + transactions."""
    paid = [t for t in all_transactions if not t['theyPaidYou']]
    received = [t for t in all_transactions if t['theyPaidYou']]
    ordered = sorted(
        all_transactions,
        key=lambda x: datetime.fromisoformat(x['dateRequested']),
        reverse=True,
    )

    return {
        'requestCount': len(requests),
        'paidCount': len(paid),
        'averagePaybackTime': average_payback_time(requests),
        'paymentsReceived': len(received),
        'topPaidToMe': get_top_transactions(all_transactions, they_paid=True),
        'topPaidByMe': get_top_transactions(all_transactions, they_paid=False),
        'allTransactions': ordered,
        'monthlyTotals': calculate_monthly_totals(all_transactions),
    }


def payback_summary(full, range_days):
    """Compute this user's average payback time for each range window.

    `range_days` is a {label: days} map. Returns {label: {'avg': seconds|None,
    'count': matched_requests}} — used to populate the cross-user leaderboard.
    """
    out = {}
    for label, days in range_days.items():
        windowed = filter_window(full, days)
        matched = [r for r in windowed['requests'] if r['dateDifferenceSeconds'] is not None]
        avg = sum(r['dateDifferenceSeconds'] for r in matched) / len(matched) if matched else None
        out[label] = {'avg': avg, 'count': len(matched)}
    return out


def get_venmo_data(token, months=6):
    """Fetch + aggregate in one call (used for direct/local invocation).

    `token` is a stored token dict (see token_store).
    """
    service, _ = gmail_client.build_service(token)
    data = fetch_transactions(service, months=months)
    return aggregate_transactions(data['requests'], data['allTransactions'])