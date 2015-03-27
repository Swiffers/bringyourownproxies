#!/usr/bin/python
import functools 

from formatbytes.formatbytes import FormatBytes

from clint.textui.progress import Bar as ProgressBar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.errors import InvalidUploadCallback

ON_SUCCESS_UPLOAD = functools.partial(lambda video_request,account : None) 
ON_FAILED_UPLOAD = functools.partial(lambda exc,video_request,account,settings : None)


class Upload(object):
    
    DEFAULT_STARTED_CALLBACK = functools.partial(lambda **kwargs: None)
    DEFAULT_UPLOADING_CALLBACK = functools.partial(lambda **kwargs : None)
    DEFAULT_FAILED_CALLBACK = functools.partial(lambda **kwargs: None)
    DEFAULT_FINISHED_CALLBACK = functools.partial(lambda **kwargs: None)
    
    def __init__(self,hooks={},bubble_up_exception=False):
        
        self._validate_hooks(hooks)
        self._hooks = {'started':hooks.get('started',self.DEFAULT_STARTED_CALLBACK),
                        'uploading':hooks.get('uploading',self.DEFAULT_UPLOADING_CALLBACK),
                        'failed':hooks.get('failed',self.DEFAULT_FAILED_CALLBACK),
                        'finished':hooks.get('finished',self.DEFAULT_FINISHED_CALLBACK)}

        #Should we bubble up exception if any occurs during uploading.
        self.bubble_up_exception = bubble_up_exception

        self._started = False
        self._uploading = False
        self._failed = False
        self._finished = False
        
        self.upload_monitor = None
        

    @staticmethod
    def create_multipart_encoder(fields):
        return MultipartEncoder(fields=fields)
    
    @staticmethod
    def create_multipart_monitor(encoder,callback=None):
        callback = callback or Upload.DEFAULT_UPLOADING_CALLBACK
        if hasattr(callback,'__call__'):
            return MultipartEncoderMonitor(encoder,callback)
        else:
            raise InvalidUploadCallback('Callback {c} needs to be callable'.format(c=callback))
    
    def _validate_hooks(self,hooks):

        if not isinstance(hooks,dict):
            raise InvalidUploadCallback('hooks need to be a dictionary with 4 possible callbacks\n'\
                            '\tstarted: called when the upload has started\n'\
                            '\tuploading:called constantly during upload\n'\
                            '\tfailed:called when upload fails\n'\
                            '\tfinished:called when successfully finished uploading\n')
        for key in hooks:
            if not hasattr(hooks[key],'__call__'):
                raise InvalidUploadCallback('hook:{h} is not a callable'.format(h=key))

    def set_hooks(self,hooks):
        self._validate_hooks(hooks)
        self._hooks.update(hooks)
    
    def call_hook(self,hook,**kwargs):
        event = getattr(self,"_{hook}".format(hook=hook),None)
        
        if event is None:
            raise InvalidUploadCallback('Callback does not exist:{event}'.format(event=event))

        event = True
        
        #Dont call the callback uploading because the monitor will call it
        if hook != 'uploading':
            self._hooks.get(hook)(**kwargs)

    def remove_hook(self,hook):
        event = getattr(self,"_{hook}".format(hook=hook),None)
        
        if event is None:
            raise InvalidUploadCallback('Callback does not exist:{event}'.format(event=event))
        
        self._hooks[hook] = getattr(self,'DEFAULT_{hook}_CALLBACK'.format(hook=hook.upper()))
    
    def start(self):
        raise NotImplementedError('Subclasses need to implement this function,' \
                                   ' which will be the actual uploading function' \
                                   ' for each site')  
    
    def stop(self):
        raise NotImplementedError('Subclasses can implement this function,' \
                                   ' which will stop the current uploading')
                                   


if __name__ == '__main__':
    u = Upload()
    u.set_hooks({'uploading':lambda **h :'llol'})
    u.call_hook('uploading')
    print u._hooks
    u.remove_hook('uploading')
    print u._hooks    
