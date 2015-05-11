from bringyourownproxies.parser import VideoParser

from bringyourownproxies.sites import (YouPornComment,YouPornTag,YouPornCategory,
                                       YouPornAuthor)
class YouPornVideoParser(VideoParser):

    def get_video_stats(self,html):

        categories = []
        tags = []
        porn_stars = []

        document = self.etree.fromstring(html,self.parser)
        ratings = document.xpath('//div[@class="rating-count"]')[0].text.replace(' ratings)','').replace('(','')
        ratings_percentage = document.xpath('//div[@class="rating-percentage"]')[0]
        views = document.xpath('//div[@id="stats-views"]/text()')[0].replace(',','')
        uploaded_date = document.xpath('//div[@id="stats-date"]/text()')[0]
        title = document.xpath('//div[@class="container_15"]/h1[@class="grid_9"]')[0].text
        get_video_details = document.xpath('//ul[@class="info-list-content"]//a')

        for a in get_video_details:
            get_type = re.match(r'/(.*?)/(.*?)/',a.attrib['href'],re.I|re.M)
            if get_type:
                #figure out the type of data, either tag, category or porn star name
                item_type = get_type.group(1)
                if item_type == 'category':
                    #create a new YouPornCategory
                    categories.append(YouPornCategory(name=a.text,href=a.attrib['href']))
                elif item_type == 'porntags':
                    #create a new YouPornTag
                    tags.append(YouPornTag(name=a.text,href=a.attrib['href']))
                elif item_type == 'pornstar':
                    porn_stars.append((a.text,a.attrib['href']))

        video_url = doc.xpath('//link[@href]/@href')[0]
        embed_code = "<iframe src={url}" \
        " frameborder=0 height=481 width=608" \
        " scrolling=no name=yp_embed_video>" \
        "</iframe>".format(url=video_url)

        author_name = document.xpath('//button[@data-name]//@data-name')[0]
        author_href = document.xpath('//div[@class="author-block--line"]//a')[0].attrib['href']
        author = YouPornAuthor(name=author_name,href=author_href)
        total_comments =document.xpath('//li[@id="tabComments"]//a[@href="javascript:void(0)"]')[0] \
                         .text.replace('Comments (','').replace(')','')

        return {'total_comments':int(total_comments),
                'author':author,
                'porn_stars':porn_stars,
                'categories':categories,
                'tags':tags,
                'uploaded_date':uploaded_date,
                'views':views,
                'ratings':ratings,
                'ratings_percentage':ratings_percentage,
                'title':title,
                'embed_code':embed_code}

    def get_download_url(self,html):
        document = self.etree.fromstring(html,self.parser)
        get_video_url = document.xpath('//video[@id="player-html5"]/@src')
        if not get_video_url:
            raise VideoParserError('Cannot find video download url for youporn video')
        return get_video_url[0]

    def get_all_comments(self,html):
        comments = []
        current_page = None
        total_pages = None
        document = self.etree.fromstring(html,self.parser)

        grab_comments = document.xpath('//li')

        if len(grab_comments):
            for div in grab_comments:
                div_doc = self.etree.fromstring(self.tostring(div),self.parser)

                author = div_doc.xpath('//p[@class="name"]')[0].text
                date = div_doc.xpath('//span[@class="date"]/text()')[0].lstrip()
                text = div_doc.xpath('//p[@class="message"]/text()')[0]
                thumbs_up = int(div_doc.xpath('//div[@class="option-links"]/@data-likes')[0])
                thumbs_down = int(div_doc.xpath('//div[@class="option-links"]/@data-dislikes')[0])
                comment_id = div_doc.xpath('//div[@data-commentid]/@data-commentid')[0]

                comments.append(YouPornComment(author=author,
                                                text=text,
                                                posted_date=date,
                                                thumbs_up=thumbs_up,
                                                thumbs_down=thumbs_down,
                                                comment_id=comment_id))

            get_comments_page = document.xpath('//div[@id="watch-comment-pagination"]//div[@class="pageIndicator"]//text()')

            current_page = int(get_comments_page[1])
            total_pages = int(get_comments_page[2].replace(' of ',''))


            return (comments,current_page,total_pages)

        else:
            return (None,None,None)

c