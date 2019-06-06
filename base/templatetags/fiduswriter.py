from django import template
from django.templatetags.static import PrefixNode
from django.apps import apps
from django.conf import settings

register = template.Library()


@register.inclusion_tag('fiduswriter/config.html', takes_context=True)
def fiduswriter_config_js(context):
    """
    Add Fidus Writer config variables to the window object in JavaScript.
    Usage::
        {% fiduswriter_config_js %}
    """
    if apps.is_installed('django.contrib.staticfiles'):
        from django.contrib.staticfiles.storage import staticfiles_storage
        static_url = staticfiles_storage.base_url
    else:
        static_url = PrefixNode.handle_simple("STATIC_URL")
    if 'WS_PORT' in settings.SERVER_INFO:
        ws_port = settings.SERVER_INFO['WS_PORT']
    else:
        ws_port = ''
    if 'WS_SERVER' in settings.SERVER_INFO:
        ws_server = settings.SERVER_INFO['WS_SERVER']
    else:
        ws_server = ''
    return {
        'static_url': static_url,
        'ws_port': ws_port,
        'ws_server': ws_server,
        'is_free': ('true' if settings.IS_FREE else 'false'),
        'registration_open': (
            'true' if settings.REGISTRATION_OPEN else 'false'
        ),
        'logged_in': (
            'true' if context['request'].user.is_authenticated else 'false'
        ),
        'language': context['request'].LANGUAGE_CODE
    }
