###
# Copyright (c) 2016, Johannes Löthberg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import os
import json
import subprocess

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Googler')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class Googler(callbacks.Plugin):
    """Plugin for wrapping the googler tool"""
    threaded = True

    def google(self, irc, msg, args, search):
        """<query>

        Searches Google using the googler tool
        """
        googlerCmd = self.registryValue('command')
        if googlerCmd:
            try:
                with open(os.devnull, 'r+') as null:
                    inst = subprocess.Popen([googlerCmd, '--json --lang en', search],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdin=null)
            except OSError:
                irc.error(_('It seems the configured googler command was not '
                            'available.'), Raise=True)

            (out, err) = inst.communicate()
            inst.wait()
            if out:
                response = json.loads(out.decode('utf-8'))
                if response:
                    res = response[0]
                    irc.reply('{} <{}>'.format(res['title'], res['url']))
                else:
                    irc.reply('No results found.')
            elif err:
                response = err.decode('utf-8').splitlines()
                irc.replies(response, joiner=' ')
            else:
                irc.reply('No reply.')

        else:
            irc.error(_('The googler command is not configured.  If googler is '
                        'installed on this system, reconfigure the '
                        'supybot.plugins.Googler.command configuration '
                        'variable appropriately'))
    google = wrap(google, ['text'])


Class = Googler


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
