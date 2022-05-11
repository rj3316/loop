#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#----------------------------------------------------------------------------
# Created By  : Igor Usunariz
# Created Date: 2022/04/20
# version ='2.0'
# Mail = 'i.usunariz.lopez@gmail.com'
#
# ---------------------------------------------------------------------------
# 
# MESSAGE CLASS DEFINITION
#
# ---------------------------------------------------------------------------

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha1

from queue import Queue

def send_message(queue = None, action = 'write_log', payload = None, sender = 'main', level = 'info'):
    try:
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        aux_hash = timestamp + "_" + action
        hash = sha1(aux_hash.encode('utf-8')).hexdigest()

        message = Message(timestamp, hash, sender, level, action, payload)

        # Check for message's receiver
        if isinstance(queue, Queue):
            queue.put_nowait(message)
            ret_val = None
        else:
            ret_val = message
    except:
        ret_val = None
    return ret_val

@dataclass
class Message:
    timestamp: datetime
    id: str
    sender: str
    level: str
    action: str
    payload: str = ''