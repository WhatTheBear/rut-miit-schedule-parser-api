from litestar import get, MediaType

from hashlib import sha256

import hmac
import os


def is_user_data_valid(hash: str, data_check_string: str):

    bot_token =  sha256(os.getenv("TG_BOT_TOKEN").encode('utf-8')).digest()

    data_check_string = bytes(data_check_string, 'utf-8')
    
    secret =  hmac.new(key=bot_token, msg=data_check_string, digestmod=sha256).hexdigest()

    return str(secret) == str(hash)









