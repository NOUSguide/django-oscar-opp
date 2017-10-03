# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from enum import Enum, unique

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import base


@unique
class PaymentStatusCode(Enum):
    UNKNOWN_ERROR = ''
    TRANSACTION_SUCCEEDED = '000.000.000'
    SUCCESSFUL_REQUEST = '000.000.100'
    SUCCESS_CHECKOUT_CREATED = '000.200.100'
    SUCCESS_INTEGRATOR_TEST_MODE = '000.100.110'
    SUCCESS_VALIDATOR_TEST_MODE = '000.100.111'
    SUCCESS_CONNECTOR_TEST_MODE = '000.100.112'
    USER_AUTHENTICATION_FAILED = '100.380.401'
    PARES_VALIDATION_FAILED_SIGNATURE = '100.390.103'
    TRANSACTION_REJECTED_NO_3D_PROGRAM = '100.390.108'
    CANNOT_FIND_TRANSACTION = '700.400.580'
    TRANSACTION_DECLINED = '800.100.152'
    TRANSACTION_DECLINED_INVALID_CARD = '800.100.151'

    def get_message(self):
        descriptions = {
            PaymentStatusCode.UNKNOWN_ERROR: 'Bei der Zahlung ist ein Fehler aufgetreten',
            PaymentStatusCode.SUCCESSFUL_REQUEST: 'Buchung erfolgreich',
            PaymentStatusCode.SUCCESS_INTEGRATOR_TEST_MODE: 'Buchung erfolgreich',
            PaymentStatusCode.SUCCESS_VALIDATOR_TEST_MODE: 'Buchung erfolgreich',
            PaymentStatusCode.SUCCESS_CONNECTOR_TEST_MODE: 'Buchung erfolgreich',
            PaymentStatusCode.USER_AUTHENTICATION_FAILED: 'Authentifizierung fehlgeschlagen',
            PaymentStatusCode.PARES_VALIDATION_FAILED_SIGNATURE: 'Signatur Validierung fehlgeschlagen.',
            PaymentStatusCode.TRANSACTION_REJECTED_NO_3D_PROGRAM: 'Die Zahlung kann mit dieser Kreditkarte nicht durchgeführt werden.',
            PaymentStatusCode.CANNOT_FIND_TRANSACTION: 'Unbekannte Kreditkarte',
            PaymentStatusCode.TRANSACTION_DECLINED: 'Transaktion wurde abgelehnt.',
            PaymentStatusCode.TRANSACTION_DECLINED_INVALID_CARD: 'Unbekannte Kreditkarte'
        }
        return descriptions.get(self, '')

    def is_valid_status(self):
        return any([status == self for status in VALID_STATUS])


VALID_STATUS = [
    PaymentStatusCode.SUCCESSFUL_REQUEST,
    PaymentStatusCode.SUCCESS_CONNECTOR_TEST_MODE,
    PaymentStatusCode.SUCCESS_INTEGRATOR_TEST_MODE,
    PaymentStatusCode.SUCCESS_VALIDATOR_TEST_MODE
]
VALID_STATUS_CODES = [s.value for s in VALID_STATUS]


@python_2_unicode_compatible
class Transaction(base.ResponseModel):
    """
    Model to store every confirmation for successful or failed payments.
    """
    CLEAN_REGEX = [
        (r'password=\w+&', 'password=XXXXXX&'),
        (r'userId=\w+&', 'userId=XXXXXX&'),
        (r'entityID=\w+&', 'entityID=XXXXXX&'),
    ]

    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, null=True, blank=True)

    result_code = models.CharField(max_length=32)
    result_description = models.CharField(max_length=512, null=True, blank=True)

    checkout_id = models.CharField(max_length=48, unique=True, null=True, editable=False)
    correlation_id = models.CharField(max_length=32, null=True, editable=False)

    class Meta:
        verbose_name = _('Transaction')
        ordering = ('-date_created',)

    def __str__(self):
        return "Transaction %s" % self.id

    def save(self, *args, **kwargs):
        for regex, s in self.CLEAN_REGEX:
            self.raw_request = re.sub(regex, s, self.raw_request)
        return super(Transaction, self).save(*args, **kwargs)

    @property
    def is_approved(self):
        return self.result_code in VALID_STATUS_CODES
