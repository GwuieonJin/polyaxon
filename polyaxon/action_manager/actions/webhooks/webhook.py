from django.conf import settings

from action_manager.action import Action, logger
from action_manager.action_event import ActionExecutedEvent
from action_manager.exception import PolyaxonActionException
from event_manager.event_actions import EXECUTED
from event_manager.event_context import get_event_context, get_readable_event
from libs.http import safe_request, validate_url
from polyaxon_schemas.utils import to_list

WEBHOOK_ACTION_EXECUTED = 'webhook_action.{}'.format(EXECUTED)


class WebHookActionExecutedEvent(ActionExecutedEvent):
    event_type = WEBHOOK_ACTION_EXECUTED


class WebHookAction(Action):
    action_key = 'webhook'
    name = 'WebHook'
    event_type = WEBHOOK_ACTION_EXECUTED
    description = ("Webhooks send an HTTP payload to the webhook's configured URL."
                   "Webhooks can be used automaticaly "
                   "by subscribing to certain events on Polyaxon, "
                   "or manually triggered by a user operation.")
    raise_empty_context = False

    @classmethod
    def _validate_config(cls, config):
        if not config:
            return []
        return cls._get_valid_config(config)

    @classmethod
    def _get_valid_config(cls, config, *fields):
        config = to_list(config)
        web_hooks = []
        for web_hook in config:
            if not web_hook.get('url'):
                logger.warning("Settings contains a non compatible web hook: `%s`", web_hook)
                continue

            url = web_hook['url']
            if not validate_url(url):
                raise PolyaxonActionException('{} received invalid URL `{}`.'.format(cls.name, url))

            method = web_hook.get('method', 'POST')
            if not isinstance(method, str):
                raise PolyaxonActionException(
                    '{} received invalid method `{}`.'.format(cls.name, method))

            _method = method.upper()
            if _method not in ['GET', 'POST']:
                raise PolyaxonActionException(
                    '{} received non compatible method `{}`.'.format(cls.name, method))

            result_web_hook = {'url': url, 'method': _method}
            for field in fields:
                if field in web_hook:
                    result_web_hook[field] = web_hook[field]
            web_hooks.append(result_web_hook)

        return web_hooks

    @classmethod
    def _get_config(cls):
        """Configuration for webhooks.

        Should be a list of urls and potentially a method.

        If no method is given, then by default we use POST.
        """
        return settings.INTEGRATIONS_WEBHOOKS

    @classmethod
    def serialize_event_to_context(cls, event):
        event_context = get_event_context(event)

        context = {
            'subject': event_context.subject_action,
            'body': get_readable_event(event_context),
            'datetime': event_context.datetime
        }
        return context

    @classmethod
    def _pre_execute_web_hook(cls, data, config):
        return data

    @classmethod
    def _execute(cls, data, config):
        for web_hook in config:
            data = cls._pre_execute_web_hook(data=data, config=web_hook)
            if web_hook['method'] == 'POST':
                safe_request(url=web_hook['url'], method=web_hook['method'], json=data)
            else:
                safe_request(url=web_hook['url'], method=web_hook['method'], params=data)
