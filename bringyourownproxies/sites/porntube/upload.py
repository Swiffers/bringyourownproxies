# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import traceback

from bringyourownproxies.errors import InvalidVideoUploadRequest,InvalidAccount,NotLogined
from bringyourownproxies.sites.upload import _Upload,KummUploader
from bringyourownproxies.sites.porntube.account import PornTubeAccount
from bringyourownproxies.sites.porntube.video import PornTubeVideoUploadRequest

__all__ = ['PornTubeUpload']

class PornTubeUpload(_Upload):

    def start(self):

        try:
            if not isinstance(self.video_upload_request,PornTubeVideoUploadRequest):
                raise InvalidVideoUploadRequest('Invalid video_upload_request, ' \
                                        'it needs to be a PornTubeVideoUploadRequest instance')

            if not isinstance(self.account,PornTubeAccount):
                raise InvalidAccount('Invalid account, it needs to be a PornTubeAccount instance')


            if not self.account.is_logined():
                raise NotLogined('PornTube account is not logined')

            self.call_hook('started',video_upload_request=self.video_upload_request,account=self.account)


            domain="http://porntube.com"
            website="porntube"
            username = self.account.username
            http_settings=self.account.http_settings
            drop_incorrect_tags = self.video_upload_request.drop_incorrect_tags
            add_all_autocorrect_tags = self.video_upload_request.add_all_autocorrect_tags
            autocorrect_tags = self.video_upload_request.autocorrect_tags

            uploader = KummUploader(domain,
                                    website,
                                    username,
                                    http_settings=http_settings,
                                    drop_incorrect_tags=drop_incorrect_tags,
                                    add_all_autocorrect_tags=add_all_autocorrect_tags,
                                    autocorrect_tags=autocorrect_tags)

            video_file = self.video_upload_request.video_file
            title = self.video_upload_request.title
            porn_stars = self.video_upload_request.porn_stars
            tags = [t.name for t in self.video_upload_request.tags]
            orientation = self.video_upload_request.category.category_id

            uploader.upload(video_file,title,porn_stars,tags,orientation)

        except Exception as exc:

            self.call_hook('failed',video_upload_request=self.video_upload_request,
                                    account=self.account,
                                    traceback=traceback.format_exc(),
                                    exc_info=sys.exc_info())

            if self.bubble_up_exception:
                raise exc

        else:

            self.call_hook('finished',
                            video_request=self.video_upload_request,
                            account=self.account,
                            settings={''})

            return {'status':True}

