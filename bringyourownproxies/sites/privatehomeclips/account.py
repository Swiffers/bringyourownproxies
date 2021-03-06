# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account

__all__ = ['PrivateHomeClipsAccount']

class PrivateHomeClipsAccount(_Account):

    SITE = 'PrivateHomeClips'
    SITE_URL = 'www.PrivateHomeClips.com'

    def __init__(self,username,password,email,**kwargs):
        super(PrivateHomeClipsAccount,self).__init__(username=username,password=password,email=email,**kwargs)

    def login(self):

        attempt_login  = self._login(password='pass',
                                    extra_post_vars={"action":"login",
                                                    "redirect_to":"http://www.privatehomeclips.com/soffer.php",
                                                    },
                                    post_url='http://www.privatehomeclips.com/login.php')


        self._find_login_errors(response=attempt_login,
                                error_msg_xpath='//div[@class="message_error"]/text()',
                                wrong_pass_msg='Invalid Username or Password. Username and Password are case-sensitive.')
    def is_logined(self):

        return self._is_logined(sign_out_xpath='//a[@href="/logout.php" and @class="logout"]')

