# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from urllib import parse

import requests

logger = logging.getLogger('opp')


# payment types
PA = 'Preauthorization' # A stand-alone authorisation that will also trigger optional risk management and validation. A Capture (CP) with reference to the Preauthorisation (PA) will confirm the payment..
DB = 'Debit'  # Debits the account of the end customer and credits the merchant account.
CD = 'Credit'  # Credits the account of the end customer and debits the merchant account.
CP = 'Capture'  # Captures a preauthorized (PA) amount.
RV = 'Reversal'  # Reverses an already processed Preauthorization (PA), Debit (DB) or Credit (CD) transaction. As a consequence, the end customer will never see any booking on his statement. A Reversal is only possible until a connector specific cut-off time. Some connectors don't support Reversals.
RF = 'Refund'  # Credits the account of the end customer with a reference to a prior Debit (DB) or Credit (CD) transaction. The end customer will always see two bookings on his statement. Some connectors do not support Refunds.


class Gateway(object):

    CHECKOUTS_ENDPOINT = "checkouts"
    CHECKOUTS_DETAIL_ENDPOINT = "checkouts/{checkout_id}/payment"

    def __init__(self, host, auth_userid, auth_password, auth_entityid):
        self.host = host
        self.auth_userId = auth_userid
        self.auth_password = auth_password
        self.auth_entityid = auth_entityid

    def check_credentials(self):
        # TODO: [a-f0-9]{32}  \   [a-zA-Z0-9]{8,32}   \ [a-f0-9]{32}
        pass

    def get_credentials(self):
        data = {
            'authentication.userId': self.auth_userId,
            'authentication.password': self.auth_password,
            'authentication.entityId': self.auth_entityid,
        }
        return data

    def get_checkout_id(
            self, amount, currency, payment_type,
            payment_brand=None,
            descriptor=None,
            merchant_transaction_id=None,
            merchant_invoice_id=None,
    ):
        """
        1. Prepare the checkout

        First, perform a server-to-server POST request to prepare the checkout
        with the required data, including the order type, amount and currency.
        The response to a successful request is a JSON string with an id,
        which is required in the second step to create the payment form.

        https://docs.oppwa.com/tutorials/integration-guide#CNPStep1
        """
        data = self.get_credentials()
        data.update({
            'amount': amount,
            'currency': currency,
            'paymentType': payment_type
        })

        if payment_brand:
            data['paymentBrand'] = payment_brand
        if descriptor:
            data['descriptor'] = descriptor
        if merchant_transaction_id:
            data['merchantTransactionId'] = merchant_transaction_id
        if merchant_invoice_id:
            data['merchantInvoiceId'] = merchant_invoice_id

        response = requests.post(
            parse.urljoin(self.host, self.CHECKOUTS_ENDPOINT),
            data
        )
        logger.debug('RESPONSE: Url: {}\nHeaders: {}\nStatus: {}\nData: {}'.format(response.url, response.headers, response.status_code, repr(response.content)))
        return response

    def get_payment_status(self, checkout_id):
        """
        3. Get the payment status

        Once the payment has been processed, the customer is redirected to your
        'shopperResultUrl' along with a GET parameter 'resourcePath'.

        Then, to get the status of the payment, you should make a GET request
        to the 'baseUrl' + 'resourcePath', including your authentication
        parameters.

        https://docs.oppwa.com/tutorials/integration-guide#CNPStep3
        """
        response = requests.get(
            parse.urljoin(self.host, self.CHECKOUTS_DETAIL_ENDPOINT.format(checkout_id=checkout_id))
        )
        logger.debug('Url: {}\nHeaders: {}\nStatus: {}\nData: {}'.format(response.url, response.headers, response.status_code, repr(response.content)))
        return response

