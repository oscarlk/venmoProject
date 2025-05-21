from simplegmail import Gmail
from simplegmail.query import construct_query
import re
from datetime import datetime, timedelta

#authentication
gmail = None

def init_gmail():
    global gmail
    if gmail is None:
        gmail = Gmail()

#init gmail
init_gmail()

query_params = {
    "sender": 'venmo@venmo.com',
    'newer_than': (6, 'month'),
    'subject': ['You paid'],
    'exact_phrase': 'You paid',
}
#take all you paid subjects and then run this regex pattern on it to get relevant messages pattern = r"You paid ([\w\s]+) \$([\d,.]+)"

request_query_params = {
    "sender": 'venmo@venmo.com',
    'newer_than': (6, 'month'),
    'subject': ['requests'],
    'exact_phrase': 'requests',
}

def extract_first_5_requests(requestMessages):
    stored_requests = []

    # Regex pattern to extract name and amount from subject
    pattern = re.compile(r"([\w\s]+) requests \$([\d,.]+)")
    preview_pattern = re.compile(r"requests\s+\$[\d\s,.]+\s+([\w\s]+?)\s+See Request")

    for message in requestMessages:
        # Apply regex to check if the subject is a request
        match = pattern.search(message.subject)
        preview_match = preview_pattern.search(message.snippet)

        if match:
            # Store the relevant information
            stored_requests.append({
                "Name": match.group(1).strip(),
                "Amount": float(match.group(2).replace(",", "")),
                "Requested Item": preview_match.group(1).strip() if preview_match else "Emoji",
                "Subject": message.subject,
                "dateRequested": message.date,
                "Preview": message.snippet,
                "datePaid": None
            })

            # Stop after storing 5 requests
            if len(stored_requests) == 5:
                break
    
    return stored_requests

#get all the senders from the reqeuest messages and then use them to help construct the paid messages so there are less searches

requestMessages = gmail.get_messages(query=construct_query(request_query_params))
# for message in requestMessages:
    # print("Subject: " + message.subject)
    # print("Date: " + message.date)
    # print("Preview: " + message.snippet)
    # print("Message Body " + message.plain)

first_5_requests = extract_first_5_requests(requestMessages)

# Print the results
for request in first_5_requests:
    print(request)


# for paidMessage in paidMessages:
#     use regex to search for name from subject, (we know that the message with the specific subject will be like "You paid Yazan Awad $15.00")
#     use regex to search for amount from subject, (we know that the message with the specific subject will be like "You paid Yazan Awad $15.00")
#     use regex to search for requestedItem from preview, (we know that the message preview we are interested in has this format "You paid Bryan Chu $20.00 You paid Bryan Chu $ 20 . 00 Chinese food See transaction", so we can use regex to extract Chinese food)
#     go through the first 5 requests and see if name, amount, requestedItem match any of the first 5 requests
#     if the there is a match, add the paidMessage.date as another field for the first_5_requests as "Paid Date"
    

name_pattern = re.compile(r"You paid ([\w\s]+) \$([\d,.]+)")
amount_pattern = re.compile(r"You paid [\w\s]+ \$([\d,.]+)")
item_pattern = re.compile(r"\$[\d\s,.]+\s+([\w\s]+?)\s+See transaction")

paidMessages = gmail.get_messages(query=construct_query(query_params))

for paidMessage in paidMessages:
    # print("Subject: " + paidMessage.subject)
    # print("Preview: " + paidMessage.snippet)
    name_match = name_pattern.search(paidMessage.subject)
    amount_match = amount_pattern.search(paidMessage.subject)
    for paidMessage in paidMessages:
        # Extract name and amount from the subject
        name_match = name_pattern.search(paidMessage.subject)
        amount_match = amount_pattern.search(paidMessage.subject)

        if name_match and amount_match:
            paid_name = name_match.group(1).strip()
            paid_amount = float(amount_match.group(1).replace(",", ""))

            # Check for a matching request in the first 5 requests
            for request in first_5_requests:
                if (request['Name'] == paid_name and request['Amount'] == paid_amount):
                    request['datePaid'] = paidMessage.date

time_differences = []
# Print the results
for request in first_5_requests:
    print("Name: " + request['Preview'])
    print("date paid: " + str(request['datePaid']))
    print(request.get('Paid Date', 'No Payment Found'))
    d1 = datetime.fromisoformat(request['dateRequested'])
    d2 = datetime.fromisoformat(request['datePaid'])
    time_differences.append(d2 - d1)

total_time = sum(time_differences, timedelta())
average_time = total_time / len(time_differences)

days = average_time.days
hours, remainder = divmod(average_time.seconds, 3600)
minutes, seconds = divmod(remainder, 60)

print(f"Average Time for last 5 transactions: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds")