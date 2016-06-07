try:
    import weechat
except Exception:
    print 'This script must be run under WeeChat.'
    print 'Get WeeChat now at: http://www.weechat.org/'
    import_ok = False

import time
import re

SCRIPT_NAME     = 'unhighlight'
SCRIPT_AUTHOR   = 'xiagu'
SCRIPT_VERSION  = '0.1.0'
SCRIPT_LICENSE  = 'MIT'
SCRIPT_DESC     = 'Allows per-buffer specification of words to suppress highlights'

if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
    weechat.prnt('', 'Hello, from python script!')

    # hook = weechat.hook_print('', '', '', 0, 'unhighlight_new_message', '')
    hook2 = weechat.hook_modifier('weechat_print', 'unhighlight_cb', '')

    # weechat.hook_signal('buffer_line_added', 'unhighlight_signal_cb', '')

# get list of things from buffer
# check if it has them
# add 'no_highlight' tag if it do


def unhighlight_new_message(data, buffer, date, tags, displayed, highlight, prefix, message):
    weechat.prnt('', "hook_print called with %s" % message)

    if not int(highlight):
        return weechat.WEECHAT_RC_OK

        if not matches_unhighlight_strings(message):
            return weechat.WEECHAT_RC_OK


            weechat.prnt('', 'Tags: ' + tags)
            weechat.prnt('', 'tags are a ' + str(type(tags)))
            weechat.prnt('', "data: %s; buffer: %s; prefix: %s" % (data, buffer, prefix))

    # set no_highlight tag
    return weechat.WEECHAT_RC_OK


def matches_unhighlight_strings(msg, regex):
    return weechat.string_has_highlight_regex(msg, regex)


def unhighlight_cb(data, modifier, modifier_data, message):
    # buffer names can have ; in them, but not plugins or tags (I HOPE),
    # so we use find and rfind to bracket the buffer name
    m = re.match("^(?P<plugin>\S+);(?P<full_name>\S+);(?P<tags>\S*)$", modifier_data)

    tags = m.group('tags')
    if 'no_highlight' in tags or 'notify_none' in tags:
        return message

    plugin = m.group('plugin')
    full_name = m.group('full_name')
    buffer = weechat.buffer_search(plugin, full_name)

    unhighlight_regex = weechat.buffer_get_string(buffer, 'localvar_unhighlight_regex')
    if not matches_unhighlight_strings(message, unhighlight_regex):
        return message

    weechat.prnt_date_tags(buffer, 0, "%s,no_highlight" % tags, message)
    return ''


def unhighlight_signal_cb(data, signal, signal_data):
    """Add no_highlight tag to message (this signal is sent before hook_print)."""
    line_data = weechat.hdata_pointer(weechat.hdata_get('line'), signal_data, 'data')
    hdata = weechat.hdata_get('line_data')

    # only trigger on highlights
    highlight = weechat.hdata_char(hdata, line_data, 'highlight')
    weechat.prnt('', "highlight value: %s" % highlight)
    if not int(highlight):
        return weechat.WEECHAT_RC_OK

    # make sure we get an unhighlight match
    message = weechat.hdata_string(hdata, line_data, 'message')
    if not matches_unhighlight_strings(message):
        return weechat.WEECHAT_RC_OK

    tags = [weechat.hdata_string(hdata, line_data, '%d|tags_array' % i)
            for i in range(0, weechat.hdata_get_var_array_size(hdata, line_data, 'tags_array'))]
    if 'no_highlight' not in tags:
        weechat.prnt('', "adding no_highlight tag")
        tags.append('no_highlight')
        weechat.hdata_update(hdata, line_data, { 'tags_array': ','.join(tags) })

    # clear the message
    weechat.hdata_update(hdata, line_data, { 'message': '' })

    buffer = weechat.hdata_pointer(hdata, line_data, 'buffer')
    weechat.prnt_date_tags(buffer, 0, ','.join(tags), message);

    return weechat.WEECHAT_RC_OK


def hdata_update_line3_cmd(data, buffer, args):
    """Remove tag "irc_smart_filter" on last line displayed in buffer (if line has such tag) and add " zzzz" to message."""
    own_lines = weechat.hdata_pointer(weechat.hdata_get('buffer'), weechat.current_buffer(), 'own_lines')
    if own_lines:
        line = weechat.hdata_pointer(weechat.hdata_get('lines'), own_lines, 'last_line')
        if line:
            data = weechat.hdata_pointer(weechat.hdata_get('line'), line, 'data')
            hdata = weechat.hdata_get('line_data')
            tags = [weechat.hdata_string(hdata, data, '%d|tags_array' % i)
                    for i in range(0, weechat.hdata_get_var_array_size(hdata, data, 'tags_array'))]
            if 'irc_smart_filter' in tags:
                tags.remove('irc_smart_filter')
            message = weechat.hdata_string(hdata, data, 'message') + ' zzzz'
            weechat.hdata_update(hdata, data, { 'tags_array': ','.join(tags), 'message': message, 'highlight': 0 })
    return weechat.WEECHAT_RC_OK


def buffer_line_added_cb(data, signal, signal_data):
    """Update new line displayed in buffer by removing one hour to date of message (this signal is sent before hook_print, so modified date is used by logger plugin)."""
    line_data = weechat.hdata_pointer(weechat.hdata_get('line'), signal_data, 'data')
    hdata = weechat.hdata_get('line_data')
    weechat.hdata_update(hdata, line_data, { 'date': str(weechat.hdata_time(hdata, line_data, 'date') - 3600) })
    return weechat.WEECHAT_RC_OK

