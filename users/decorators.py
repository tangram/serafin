from __future__ import unicode_literals
import json

import requests
from token_auth.json_status import STATUS_OK


def vault_post(func):
    """ A helper decorator for posting json request to Vault.
    """

    def _vault_post(*args, **kwargs):

        url, user_id, token = func(*args, **kwargs)

        if url and user_id and token:
            data = {
                'user_id': user_id,
                'token': token,
            }
            data.update(kwargs)

            response = requests.post(url, data=json.dumps(data))
            response.raise_for_status()

            response_json = response.json()
            status = response_json.get('status')
            if status and status == STATUS_OK:
                return True

        return False