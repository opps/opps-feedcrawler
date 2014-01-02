#coding: utf-8
#import random
import urllib
import json
import xml.etree.ElementTree as ET
from ftplib import FTP
from tempfile import NamedTemporaryFile

from datetime import datetime, timedelta
from dateutil.parser import parse

from django.utils.text import slugify
from django.conf import settings
from .base import BaseProcessor
from .efe import iptc
from .category_efe import CATEGORY_EFE

from opps.articles.models import Post
from opps.channels.models import Channel


TZ_DELTA = timedelta(hours=getattr(settings, "TZ_DELTA", 2))


class EFEXMLProcessor(BaseProcessor):

    def connect(self):
        self.ftp = FTP()
        params = {"host": self.feed.source_url}
        if self.feed.source_port:
            params['port'] = int(self.feed.source_port)

        self.ftp.connect(**params)

        if self.feed.source_username:
            self.ftp.login(self.feed.source_username,
                           self.feed.source_password)

        self.verbose_print(self.ftp.getwelcome())

        return self.ftp

    def get_temp_file(self):
        f = NamedTemporaryFile(delete=True)
        self.verbose_print("%s tempfile created" % f.name)
        return f

    def process_file(self, s):

        self.verbose_print("-" * 78)

        if self.log_created(s):
            self.verbose_print("%s already processed, skipping." % s)
            return

        s = s.strip()
        s = s.replace("\n", "")
        ext = s.split('.')[-1]
        if ext not in ['XML', 'xml']:
            self.verbose_print("Skipping non xml %s" % s)
            return

        self.verbose_print("Retrieving file %s" % s)

        source_root_folder = self.feed.source_root_folder
        if not source_root_folder.endswith('/'):
            source_root_folder += "/"

        if self.feed.source_username:
            url = "ftp://{0}:{1}@{2}{3}{4}".format(self.feed.source_username,
                                                   self.feed.source_password,
                                                   self.feed.source_url,
                                                   source_root_folder,
                                                   s)
        else:
            url = "ftp://{0}{1}{2}".format(self.feed.source_url,
                                       source_root_folder,
                                       s)
        self.verbose_print(url)

        f = self.get_temp_file()
        try:
            urllib.urlretrieve(url, filename=f.name)
            self.verbose_print("File retrieved successfully")
        except Exception as e:
            self.verbose_print("error urlretrieve")
            self.verbose_print(str(e))
            return

        try:
            xml_string = f.read()
            self.verbose_print("xml_string read!")
        except Exception as e:
            self.verbose_print("error f.read")
            self.verbose_print(str(e))
            return

        if not xml_string:
            self.verbose_print("XML Empty")
            f.close()
            return


        news = self.parse_xml(f.name)
        created = None

        for data in news:
            data = self.categorize(data)
            # self.verbose_print(str(data))
            created = self.create_entry(data)

        if created:
            self.record_log(s)
        else:
            self.verbose_print("Entries not created")

        f.close()

    def parse_xml(self, filename):
        news = []

        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except:
            return


        for item in root.findall('./NewsItem'):
            data = {}

            try:
                data['headline'] = item.find(
                    './NewsComponent/NewsLines/HeadLine').text
                data['subheadline'] = item.find(
                    './NewsComponent/NewsLines/SubHeadLine').text
            except:
                pass

            try:
                tobject_attrib = item.find(
                    './NewsComponent/ContentItem/'
                    'DataContent/nitf/head/tobject/tobject.subject')
                data['iptc_code'] = tobject_attrib.get('tobject.subject.refnum')
                data['iptc_matter'] = tobject_attrib.get('tobject.subject.matter')
                data['iptc_type'] = tobject_attrib.get('tobject.subject.type')
            except:
                pass

            try:
                tags_attr =  item.find(
                    './NewsComponent/ContentItem/'
                    'DataContent/nitf/head/docdata/key-list/keyword')
                tags = tags_attr.get('key')
                data['tags'] = [tag.lower() for tag in tags.split()]
                self.verbose_print(data.get('tags'))
            except Exception as e:
                self.verbose_print("error tog et tags %s" % str(e))
                pass

            try:
                pub_data_attrib = item.find(
                    './NewsComponent/ContentItem/'
                    'DataContent/nitf/head/pubdata')
                data['pub_date'] = pub_data_attrib.get('date.publication')
                data['item_len'] = pub_data_attrib.get('item-length')
            except:
                pass

            try:
                data['abstract'] = item.find(
                    './NewsComponent/ContentItem'
                    '/DataContent/nitf/body/body.head/abstract/').text
            except:
                pass

            try:
                data['owner'] = item.find(
                    './NewsComponent/ContentItem/DataContent/nitf/'
                    'body/body.head/rights/').text
            except:
                pass

            try:
                data['story_data'] = item.find(
                    './NewsComponent/ContentItem/DataContent/nitf/'
                    'body/body.head/dateline/story.date').get('norm')
            except:
                pass

            try:
                body = item.find(
                    './NewsComponent/ContentItem/DataContent/nitf/'
                    'body/body.content')
                data['body'] = u"\n".join(
                    u"<p>{0}</p>".format(p.text) for p in body)
            except:
                pass

            if not all([data.get('body'), data.get('headline')]):
                self.verbose_print(
                    "Data does not have body and headline %s" % str(data))
            else:
                news.append(data)

        return news

    def parse_dt(self, s):
        self.verbose_print("Received to parse_dt %s" % s)
        try:
            try:
                new_s = parse(s) - TZ_DELTA
            except:
                new_s = datetime.strptime(s[:8], "%Y%m%d")

            self.verbose_print("parsed to %s" % new_s)
            return new_s
        except Exception as e:
            self.verbose_print("Cannot parse dt")
            self.verbose_print(str(e))
            return

    def create_entry(self, data):
        if not data:
            self.verbose_print("data is null")
            return

        pub_time = self.parse_dt(
            data.get('pub_date', data.get('story_data', None))
        )

        if pub_time:
            pub_time_str = pub_time.strftime("%Y-%m-%d")
        else:
            pub_time_str = ""

        # working
        entry_title = unicode(data.get('headline', ''))

        # slug generated as
        # feed-name-news-title-2013-01-01
        slug = slugify(self.feed.slug + "-" + entry_title[:100] + pub_time_str)

        exists = self.entry_model.objects.filter(slug=slug).exists()
        if exists:
            #slug = str(random.getrandbits(8)) + "-" + slug
            self.verbose_print("Entry slug exists, skipping")
            return

        try:
            tags = ",".join(data.get('tags'))
        except:
            tags = None

        self.verbose_print(tags)

        try:
            db_entry, created = self.entry_model.objects.get_or_create(
                entry_feed=self.feed,
                channel=self.feed.get_channel(),
                title=entry_title[:150],
                slug=slug[:150],
                entry_title=entry_title[:150],
                site=self.feed.site,
                user=self.feed.user,
                published=self.feed.publish_entries,
                show_on_root_channel=False,
                tags=unicode(tags)
            )
            db_entry.entry_description = unicode(data.get('abstract', ''))
            db_entry.entry_content = unicode(data.get('body', ''))
            db_entry.entry_category = unicode(data.get('iptc_matter', ''))
            db_entry.hat = unicode(data.get('subheadline', ''))
            db_entry.entry_category_code = unicode(data.get('iptc_code', ''))

            db_entry.entry_published_time = pub_time

            try:
                db_entry.entry_json = json.dumps(data)
            except Exception as e:
                self.verbose_print("Cound not dump json %s" % str(data))
                self.verbose_print(str(e))

            db_entry.save()
            self.verbose_print("Entry saved: %s" % db_entry.pk)

            db_entry.pub_time_str = pub_time_str
            self.run_hooks(db_entry)

            return db_entry.pk

        except Exception as e:
            self.verbose_print("Cannot save the entry")
            self.verbose_print(str(data))
            self.verbose_print(str(e))

    def categorize(self, data):
        if not data.get('iptc_code'):
            self.verbose_print("No iptc code to categorize")
            return data

        iptc_info = iptc.get(data['iptc_code'])
        if iptc_info:
            data.update(iptc_info)
        else:
            data['parent_desc'] = data.get('iptc_type')
            data['desc'] = data.get('iptc_matter')
            data['cod'] = data['iptc_code']
            data['parent'] = None
            data['cat'] = None


        return data

    def process(self):
        self.connect()
        self.ftp.cwd(self.feed.source_root_folder)
        self.verbose_print(
            "Root folder changed to: %s" % self.feed.source_root_folder)

        self.count = 0
        self.ftp.retrlines('NLST', self.process_file)

        self.feed.last_polled_time = datetime.now()
        self.feed.save()


    def hook_not_found(self, *args, **kwargs):
        self.verbose_print("Hook not found")

    def run_hooks(self, entry):
        hooks = getattr(self, 'hooks', [])
        for hook in hooks:
            try:
                getattr(self, hook, self.hook_not_found)(entry)
            except Exception as e:
                self.verbose_print(str(e))


class EFEXMLProcessorAuto(EFEXMLProcessor):

    hooks = ['create_post']

    # match category X channel

    def get_channel_by_slug(self, slug):
        if not slug:
            return
        try:
            return Channel.objects.filter(long_slug=slug)[0]
        except:
            return

    def create_post(self, entry):

        channel_slug = CATEGORY_EFE.get(
            str(entry.entry_category_code).strip().zfill(8)
        )

        # log for debug
        if not channel_slug:
            msg = "{e.id} - {e.entry_category_code} not match category_efe \n"
            open("/tmp/debug_feeds.log", "a").write(
                msg.format(e=entry)
            )

        channel = self.get_channel_by_slug(channel_slug) or entry.channel

        self.verbose_print(channel_slug)
        self.verbose_print(entry.entry_category_code)

        slug = slugify(entry.entry_title + "-" + entry.pub_time_str)[:150]
        if Post.objects.filter(channel=channel,
                               slug=slug,
                               site=entry.site).exists():
            # slug = str(random.getrandbits(8)) + "-" + slug
            self.verbose_print("Post slug exists")
            # do not create duplicates
            return

        post = Post(
            title=entry.entry_title[:150],
            slug=slug,
            content=entry.entry_content,
            channel=channel,
            site=entry.site,
            user=entry.user,
            show_on_root_channel=True,
            published=True,
            hat=entry.hat,
            tags=entry.tags,
            date_insert=entry.entry_published_time,
            date_available=entry.entry_published_time
        )

        if self.feed.group:
            post.source = self.feed.group.name

        post.save()

        self.verbose_print(post.tags)
        entry.post_created = True
        entry.save()

        self.verbose_print(u"Post {p.id}- {p.title} - {p.slug} created".format(p=post))

        return post

# LIST retrieves a list of files and information about those files.
# NLST retrieves a list of file names.
# On some servers, MLSD retrieves a machine readable list of files and information
# about those files
