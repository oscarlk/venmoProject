from simplegmail import Gmail
from simplegmail.query import construct_query
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

def update_paid_message(paidMessages, request_messages, all_transactions):
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

            # Check for a matching request
            for request in request_messages:
                if (request['name'] == paid_name and request['amount'] == paid_amount):
                    request['datePaid'] = paidMessage.date
                    request['dateDifferenceSeconds'] = (datetime.fromisoformat(request['datePaid']) - datetime.fromisoformat(request['dateRequested'])).total_seconds()
            # Add the transaction to all_transactions
            all_transactions.append({
                "name": paid_name,
                "amount": paid_amount,
                "dateRequested": paidMessage.date,
                "theyPaidYou": False,
                "item": item_match.group(1).strip() if item_match else "Emoji probably present",
            })

def update_paid_charge_message(paidMessages, request_messages, all_transactions):
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

            # Check for a matching request
            for request in request_messages:
                if (request['name'] == paid_name and request['amount'] == paid_amount):
                    request['datePaid'] = paidMessage.date
                    request['dateDifferenceSeconds'] = (datetime.fromisoformat(request['datePaid']) - datetime.fromisoformat(request['dateRequested'])).total_seconds()
            all_transactions.append({
                "name": paid_name,
                "amount": paid_amount,
                "dateRequested": paidMessage.date,
                "theyPaidYou": False,
                "item": item_match.group(1).strip() if item_match else "Emoji probably present",
            })

def average_payback_time(request_messages):
    request_count = len(request_messages)
    total_seconds = 0
    if request_count == 0:
        return 0
    for request in request_messages:
        if request['dateDifferenceSeconds'] is not None:
            total_seconds += request['dateDifferenceSeconds']
    average_seconds = total_seconds / request_count
    return average_seconds

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
        'total_amount': amount,
        'transaction_count': sum(1 for t in filtered_transactions if t['name'] == name)
    } for name, amount in top_3]

#function that returns venmo data
def get_venmo_data():
    #authentication, needs to be modified when creating unique id
    # token_path = 'gmail_token.json'

    try:
        # gmail = Gmail(client_secret_file=token_path)
        gmail = Gmail()
    except Exception as e:
        raise Exception(f"Gmail authentication failed for user {str(e)}")

    # get messages from gmail
    paid_messages = gmail.get_messages(query=construct_query(PAID_QUERY_PARAMS))
    paid_charge_messages = gmail.get_messages(query=construct_query(PAID_CHARGE_QUERY_PARAMS))

    all_transactions = []
    requests = extract_requests(gmail.get_messages(query=construct_query(REQUEST_QUERY_PARAMS)))
    payments = extact_payments(gmail.get_messages(query=construct_query(PAYMENT_QUERY_PARAMS)), all_transactions)
    
    # update requests object with your payments
    update_paid_message(paid_messages, requests, all_transactions)
    update_paid_charge_message(paid_charge_messages, requests, all_transactions)

    #sort all_transactions
    all_transactions.sort(key=lambda x: datetime.fromisoformat(x['dateRequested']), reverse=True)

    # for request in requests:
    #     print(request)
    
    #update final object
    # final object returned for api call, return at the end?
    final_object = {}
    final_object['requestCount'] = len(requests)
    final_object['paidCount'] = len(paid_messages) + len(paid_charge_messages)
    final_object['averagePaybackTime'] = average_payback_time(requests)
    final_object['paymentsReceived'] = len(payments)
    final_object['topPaidToMe'] = get_top_transactions(all_transactions, they_paid=True)
    final_object['topPaidByMe'] = get_top_transactions(all_transactions, they_paid=False)
    final_object['allTransactions'] = all_transactions

    return final_object
    #STILL NEED TO POPULATE ITEMS AND RENAME OBJECT KEY NAMES
    # count = 0
    # for transaction in all_transactions:
    #     count += 1
    #     if count > 10:
    #         break
    #     print(transaction)

    

# get_venmo_data()