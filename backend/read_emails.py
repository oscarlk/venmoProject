from simplegmail import Gmail
from simplegmail.query import construct_query
import re
from datetime import datetime, timedelta

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
                "Name": match.group(1).strip(),
                "Amount": float(match.group(2).replace(",", "")),
                "Requested Item": preview_match.group(1).strip() if preview_match else "Emoji probably present",
                # "Subject": message.subject,
                "dateRequested": message.date,
                # "Preview": message.snippet,
                "datePaid": None,
                "dateDifferenceSeconds": None
            })
    
    return stored_requests

# for paidMessage in paidMessages:
#     use regex to search for name from subject, (we know that the message with the specific subject will be like "You paid Yazan Awad $15.00")
#     use regex to search for amount from subject, (we know that the message with the specific subject will be like "You paid Yazan Awad $15.00")
#     use regex to search for requestedItem from preview, (we know that the message preview we are interested in has this format "You paid Bryan Chu $20.00 You paid Bryan Chu $ 20 . 00 Chinese food See transaction", so we can use regex to extract Chinese food)
#     go through the first 5 requests and see if name, amount, requestedItem match any of the first 5 requests
#     if the there is a match, add the paidMessage.date as another field for the first_5_requests as "Paid Date"
    

def update_paid_message(paidMessages, request_messages):
    name_pattern = re.compile(r"You paid ([\w\s]+) \$([\d,.]+)")
    amount_pattern = re.compile(r"You paid [\w\s]+ \$([\d,.]+)")
    for paidMessage in paidMessages:
        # Extract name and amount from the subject
        name_match = name_pattern.search(paidMessage.subject)
        amount_match = amount_pattern.search(paidMessage.subject)

        if name_match and amount_match:
            paid_name = name_match.group(1).strip()
            paid_amount = float(amount_match.group(1).replace(",", ""))

            # Check for a matching request
            for request in request_messages:
                if (request['Name'] == paid_name and request['Amount'] == paid_amount):
                    request['datePaid'] = paidMessage.date
                    request['dateDifferenceSeconds'] = (datetime.fromisoformat(request['datePaid']) - datetime.fromisoformat(request['dateRequested'])).total_seconds()

def update_paid_charge_message(paidMessages, request_messages):
    name_pattern_charge_request = re.compile(r"You completed (.+?)'s \$[\d.]+? charge request")
    amount_pattern_charge_request = re.compile(r"\$(\d+(?:\.\d{2})?)")
    for paidMessage in paidMessages:
        # Extract name and amount from the subject
        name_match = name_pattern_charge_request.search(paidMessage.subject)
        amount_match = amount_pattern_charge_request.search(paidMessage.subject)

        if name_match and amount_match:
            paid_name = name_match.group(1).strip()
            paid_amount = float(amount_match.group(1).replace(",", ""))

            # Check for a matching request
            for request in request_messages:
                if (request['Name'] == paid_name and request['Amount'] == paid_amount):
                    request['datePaid'] = paidMessage.date
                    request['dateDifferenceSeconds'] = (datetime.fromisoformat(request['datePaid']) - datetime.fromisoformat(request['dateRequested'])).total_seconds()

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

def extact_payments(paymentMessages):
    stored_payments = []
    name_and_amount_pattern = r"(.+?) paid (?:you|your) \$(\d+(?:\.\d{2})?)(?:\s+request)?"
    item_pattern = r"paid you \$ \d+ \. \d+ (.+?) See transaction"
    for payment in paymentMessages:
        # Extract name and amount from the subject
        name_and_amount_match = re.search(name_and_amount_pattern, payment.subject, re.IGNORECASE)
        item_match = re.search(item_pattern, payment.snippet, re.IGNORECASE)
        if name_and_amount_match:
            stored_payments.append({
                "Name": name_and_amount_match.group(1).strip(),
                "Amount": float(name_and_amount_match.group(2)),
                "Requested Item": item_match.group(1).strip() if item_match else "Emoji probably present",
                # "Subject": message.subject,
                "dateRequested": payment.date,
                # "Preview": message.snippet,
                "datePaid": None,
                "dateDifferenceSeconds": None
            })
    return stored_payments
#function that returns venmo data
def get_venmo_data():
    #authentication, needs to be modified when creating unique id
    token_path = 'gmail_token.json'

    try:
        gmail = Gmail(client_secret_file=token_path)
    except Exception as e:
        raise Exception(f"Gmail authentication failed for user {str(e)}")

    # get messages from gmail
    paid_messages = gmail.get_messages(query=construct_query(PAID_QUERY_PARAMS))
    paid_charge_messages = gmail.get_messages(query=construct_query(PAID_CHARGE_QUERY_PARAMS))

    requests = extract_requests(gmail.get_messages(query=construct_query(REQUEST_QUERY_PARAMS)))
    payments = extact_payments(gmail.get_messages(query=construct_query(PAYMENT_QUERY_PARAMS)))
    
    # update requests object with your payments
    update_paid_message(paid_messages, requests)
    update_paid_charge_message(paid_charge_messages, requests)

    # for request in requests:
    #     print(request)
    
    #update final object
    # final object returned for api call, return at the end?
    final_object = {}
    final_object['requestCount'] = len(requests)
    final_object['paidCount'] = len(paid_messages) + len(paid_charge_messages)
    final_object['averagePaybackTime'] = average_payback_time(requests)
    final_object['paynentsReceived'] = len(payments)

    print(final_object)

get_venmo_data()