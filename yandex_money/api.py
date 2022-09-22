from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.moves.urllib.parse import urlencode
import requests

from . import exceptions

# change it to debug/demo hosts
config = {
    'MONEY_URL': "https://yoomoney.ru",
}


class BasePayment(object):
    def send_request(self, url, headers=None, body=None):
        if not headers:
            headers = {}
        headers['User-Agent'] = "Yandex.Money.SDK/Python"

        if self.access_token:
            headers['Authorization'] = "Bearer " + self.access_token

        if not body:
            body = {}
        full_url = config['MONEY_URL'] + url
        return self.process_result(
            requests.post(full_url, headers=headers, data=body)
        )

    @classmethod
    def process_result(cls, result):
        if result.status_code == 400:
            raise exceptions.FormatError
        elif result.status_code == 401:
            raise exceptions.TokenError
        elif result.status_code == 403:
            raise exceptions.ScopeError
        return result.json()


class Wallet(BasePayment):
    def __init__(self, access_token):
        self.access_token = access_token

    def _send_authenticated_request(self, url, options=None):
        return self.send_request(url, body = options)

    def account_info(self):
        """
            Returns information about a user's wallet
            http://api.yandex.com/money/doc/dg/reference/account-info.xml
            https://tech.yandex.ru/money/doc/dg/reference/account-info-docpage/

            Returns:
                A dictionary containing account information.

            Raises:
                exceptions.FormatError: Authorization header is missing or has
                    an invalid value
                exceptions.TokenEror: Nonexistent, expired, or revoked token
                    specified
                exceptions.ScopeError: The token does not have permissions for
                    the requested operation
        """
        return self._send_authenticated_request("/api/account-info")

    def get_aux_token(self, scope):
        return self._send_authenticated_request("/api/token-aux", {
            "scope": ' '.join(scope)
        })

    def operation_history(self, options):
        """
            Returns operation history of a user's wallet
            http://api.yandex.com/money/doc/dg/reference/operation-history.xml
            https://tech.yandex.ru/money/doc/dg/reference/operation-history-docpage/

            Args:
                options: A dictionary with filter parameters according to
                documetation

            Returns:
                A dictionary containing user's wallet operations.

            Raises:
                exceptions.FormatError: Authorization header is missing or has
                    an invalid value
                exceptions.TokenEror: Nonexistent, expired, or revoked token
                    specified
                exceptions.ScopeError: The token does not have permissions for
                    the requested operation
        """
        return self._send_authenticated_request("/api/operation-history",
                                                options)

    def operation_details(self, operation_id):
        """
            Returns details of operation specified by operation_id
            http://api.yandex.com/money/doc/dg/reference/operation-details.xml
            https://tech.yandex.ru/money/doc/dg/reference/operation-details-docpage/

            Args:
                operation_id: A operation identifier

            Returns:
                A dictionary containing all details of requested operation.

            Raises:
                exceptions.FormatError: Authorization header is missing or has
                    an invalid value
                exceptions.TokenEror: Nonexistent, expired, or revoked token
                    specified
                exceptions.ScopeError: The token does not have permissions for
                    the requested operation
        """
        return self._send_authenticated_request("/api/operation-details",
                                                {"operation_id": operation_id})

    def request_payment(self, options):
        """
            Requests a payment.
            http://api.yandex.com/money/doc/dg/reference/request-payment.xml
            https://tech.yandex.ru/money/doc/dg/reference/request-payment-docpage/

            Args:
                options: A dictionary of method's parameters. Check out docs
                for more information.

            Returns:
                A dictionary containing `payment_id` and additional information
                about a recipient and payer

            Raises:
                exceptions.FormatError: Authorization header is missing or has
                    an invalid value
                exceptions.TokenEror: Nonexistent, expired, or revoked token
                    specified
                exceptions.ScopeError: The token does not have permissions for
                    the requested operation
        """
        return self._send_authenticated_request("/api/request-payment",
                                                options)

    def process_payment(self, options):
        """
            Confirms a payment that was created using the request-payment
            method.
            http://api.yandex.com/money/doc/dg/reference/process-payment.xml
            https://tech.yandex.ru/money/doc/dg/reference/process-payment-docpage/

            Args:
                options: A dictionary of method's parameters. Check out docs
                for more information.

            Returns:
                A dictionary containing status of payment and additional steps
                for authorization(if needed)

            Raises:
                exceptions.FormatError: Authorization header is missing or has
                    an invalid value
                exceptions.TokenEror: Nonexistent, expired, or revoked token
                    specified
                exceptions.ScopeError: The token does not have permissions for
                    the requested operation
        """
        return self._send_authenticated_request("/api/process-payment",
                                                options)

    def incoming_transfer_accept(self, operation_id, protection_code=None):
        """
            Accepts incoming transfer with a protection code or deferred
            transfer
            http://api.yandex.com/money/doc/dg/reference/incoming-transfer-accept.xml
            https://tech.yandex.ru/money/doc/dg/reference/incoming-transfer-accept-docpage/

            Args:
                operation_id: A operation identifier
                protection_code: secret code of four decimal digits. Specified
                for an incoming transfer proteced by a secret code. Omitted for
                deferred transfers

            Returns:
                A dictionary containing information about operation result

            Raises:
                exceptions.FormatError: Authorization header is missing or has
                    an invalid value
                exceptions.TokenEror: Nonexistent, expired, or revoked token
                    specified
                exceptions.ScopeError: The token does not have permissions for
                    the requested operation
        """
        return self._send_authenticated_request(
            "/api/incoming-transfer-accept", {
                "operation_id": operation_id,
                "protection_code": protection_code
            })

    def incoming_transfer_reject(self, operation_id):
        """
            Rejects incoming transfer with a protection code or deferred
            transfer
            http://api.yandex.com/money/doc/dg/reference/incoming-transfer-reject.xml
            https://tech.yandex.ru/money/doc/dg/reference/incoming-transfer-reject-docpage/

            Args:
                operation_id: A operation identifier

            Returns:
                A dictionary containing information about operation result

            Raises:
                exceptions.FormatError: Authorization header is missing or has
                    an invalid value
                exceptions.TokenEror: Nonexistent, expired, or revoked token
                    specified
                exceptions.ScopeError: The token does not have permissions for
                    the requested operation
        """
        return self._send_authenticated_request(
            "/api/incoming-transfer-reject",
            {
                "operation_id": operation_id
            })

    @classmethod
    def build_obtain_token_url(self, client_id, redirect_uri, scope):
        return "{}/oauth/authorize?{}".format(config['MONEY_URL'],
                                              urlencode({
                                                  "client_id": client_id,
                                                  "redirect_uri": redirect_uri,
                                                  "scope": " ".join(scope),
                                                  "response_type": "code"
                                              }))

    @classmethod
    def get_access_token(self, client_id, code, redirect_uri,
                         client_secret=None):
        full_url = config['MONEY_URL'] + "/oauth/token"
        return self.process_result(requests.post(full_url, data={
            "code": code,
            "client_id": client_id,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "client_secret": client_secret
            }
        ))

    @classmethod
    def revoke_token(self, token=None, revoke_all=False):
        """
            Revokes access token.
            http://api.yandex.com/money/doc/dg/reference/revoke-access-token.xml
            https://tech.yandex.ru/money/doc/dg/reference/revoke-access-token-docpage/

            Args:
                token: A token to be revoked

            Returns:
                None

            Raises:
                exceptions.FormatError: Authorization header is missing or has
                    an invalid value
                exceptions.TokenEror: Nonexistent, expired, or revoked token
                    specified
                exceptions.ScopeError: The token does not have permissions for
                    the requested operation
        """
        self.send_request("/api/revoke", body={
            "revoke-all": revoke_all
        }, headers={"Authorization": "Bearer {}".format(token)})


class ExternalPayment(BasePayment):
    def __init__(self, instance_id):
        self.instance_id = instance_id

    @classmethod
    def get_instance_id(cls, client_id):
        """
            Registers an instance of the application
            http://api.yandex.com/money/doc/dg/reference/instance-id.xml
            https://tech.yandex.ru/money/doc/dg/reference/instance-id-docpage/

            Args:
                client_id: A identifier of an application

            Returns:
                A dictionary with status of an operation
        """
        return cls.send_request("/api/instance-id", body={
            "client_id": client_id
        })

    def request(self, options):
        """
            Requests an external payment
            http://api.yandex.com/money/doc/dg/reference/request-external-payment.xml
            https://tech.yandex.ru/money/doc/dg/reference/request-external-payment-docpage/

            Args:
                options: A dictionary of method's parameters. Check out docs
                for more information.

            Returns:
                A dictionary containing `payment_id` and additional information
                about a recipient and payer
        """
        options['instance_id'] = self.instance_id
        return self.send_request("/api/request-external-payment", body=options)

    def process(self, options):
        """
            Confirms a payment that was created using the
            request-extenral-payment method
            http://api.yandex.com/money/doc/dg/reference/process-external-payment.xml
            https://tech.yandex.ru/money/doc/dg/reference/process-external-payment-docpage/

            Args:
                options: A dictionary of method's parameters. Check out docs
                for more information.

            Returns:
                A dictionary containing status of payment and additional steps
                for authorization(if needed)
        """
        options['instance_id'] = self.instance_id
        return self.send_request("/api/process-external-payment", body=options)
