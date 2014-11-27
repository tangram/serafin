from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model
from huey.djhuey import db_task
from system.engine import Engine


@db_task()
def transition(user_id, node_id):
    '''A task to schedule an Engine transition'''

    engine = Engine(user_id)
    node = engine.transition(node_id)

    if node:
        message = _('%(session)s transitioned to %(node)s') % {
            'session': engine.session.name,
            'node': node.name
        }

        return message


@db_task()
def init_session(session_id, user_id):
    '''Initialize a given session from start and traverse on behalf of user'''

    init = {
        'current_session': session_id,
        'current_page': 0,
    }

    engine = Engine(user_id, init)
    engine.run()

    if engine.session.trigger_login:
        engine.user.send_login_link()
        message = _('Session initialized and login e-mail sent')
    else:
        message = _('Session initialized')

    return message
