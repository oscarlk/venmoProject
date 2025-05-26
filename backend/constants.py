PAID_QUERY_PARAMS = {
    "sender": 'venmo@venmo.com',
    'newer_than': (6, 'month'),
    'subject': ['You paid'],
    'exact_phrase': 'You paid',
}

REQUEST_QUERY_PARAMS = {
    "sender": 'venmo@venmo.com',
    'newer_than': (6, 'month'),
    'subject': ['requests'],
    'exact_phrase': 'requests',
}

PAID_CHARGE_QUERY_PARAMS = {
    "sender": 'venmo@venmo.com',
    'newer_than': (6, 'month'),
    'subject': ['You completed'],
    'exact_phrase': ('You completed', 'charge request'),
}