###
# Copyright (c) 2003-2005, Jeremiah Fincher
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

from supybot.test import *

class PythonTestCase(ChannelPluginTestCase):
    plugins = ('Python',)
    def testPydoc(self):
        self.assertError('pydoc foobar')
        self.assertError('pydoc assert')
        self.assertNotError('pydoc str')
        self.assertNotError('pydoc copy')
        self.assertNotError('pydoc list.reverse')
        if os.name == 'posix':
            self.assertNotRegexp('pydoc crypt.crypt', 'NameError')
            self.assertNotError('pydoc crypt.crypt')
            # .so modules don't have an __file__ in Windows.
            self.assertNotError('pydoc math.sin')
        self.assertNotError('pydoc string.translate')
        self.assertNotError('pydoc fnmatch.fnmatch')
        self.assertNotError('pydoc socket.socket')
        self.assertNotError('pydoc logging.Logger')
        self.assertNotRegexp('pydoc str.replace', r"^'")
        self.assertNotError('pydoc os.path.expanduser')
        self.assertNotRegexp('pydoc math.hypot', r'\)\.R')
        self.assertNotRegexp('pydoc threading.Thread', 'NoneType')

    def testZen(self):
        self.assertNotError('zen')

    def testObjects(self):
        self.assertNotError('objects')

    if network:
        def testAspnRecipes(self):
            try:
                conf.supybot.plugins.Python.aspnSnarfer.setValue(True)
                self.assertSnarfRegexp(
                    'http://aspn.activestate.com/ASPN/Cookbook/Python/'
                    'Recipe/230113',
                    'Implementation of sets using sorted lists')
                self.assertSnarfNotRegexp('http://aspn.activestate.com/ASPN/'
                                          'Cookbook/Python/Recipe/144183',
                                          '\n')
            finally:
                conf.supybot.plugins.Python.aspnSnarfer.setValue(False)


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
