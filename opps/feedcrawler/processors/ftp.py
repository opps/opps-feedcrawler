#coding: utf-8
import urllib
import json
import xml.etree.ElementTree as ET
from ftplib import FTP
from tempfile import NamedTemporaryFile

from datetime import datetime

from django.utils.text import slugify

from .base import BaseProcessor
from .efe import iptc


class EFEXMLProcessor(BaseProcessor):

    def connect(self):
        self.ftp = FTP(self.feed.source_url)
        self.ftp.login(self.feed.source_username, self.feed.source_password)
        self.verbose_print(self.ftp.getwelcome())
        return self.ftp

    def get_temp_file(self):
        f = NamedTemporaryFile(delete=True)
        self.verbose_print("%s tempfile created" % f.name)
        return f

    def process_file(self, s):

        self.verbose_print("-" * 78)

        if self.log_model.objects.filter(type="created", text=s,
                                         feed=self.feed).exists():

            self.verbose_print("%s already exists, skipping." % s)
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

        url = "ftp://{0}:{1}@{2}{3}{4}".format(self.feed.source_username,
                                               self.feed.source_password,
                                               self.feed.source_url,
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

        data = self.parse_xml(f.name)
        data = self.categorize(data)
        self.verbose_print(str(data))

        f.close()

        created = self.create_entry(data)
        if created:
            self.record_log(s)
        else:
            self.verbose_print("Entry not created")

    def parse_xml(self, filename):
        data = {}

        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except:
            return

        try:
            data['headline'] = root.find(
                './NewsItem/NewsComponent/NewsLines/HeadLine').text
            data['subheadline'] = root.find(
                './NewsItem/NewsComponent/NewsLines/SubHeadLine').text
        except:
            pass

        try:
            tobject_attrib = root.find(
                './NewsItem/NewsComponent/ContentItem/'
                'DataContent/nitf/head/tobject/tobject.subject')
            data['iptc_code'] = tobject_attrib.get('tobject.subject.refnum')
            data['iptc_matter'] = tobject_attrib.get('tobject.subject.matter')
            data['iptc_type'] = tobject_attrib.get('tobject.subject.type')
        except:
            pass

        try:
            pub_data_attrib = root.find(
                './NewsItem/NewsComponent/ContentItem/'
                'DataContent/nitf/head/pubdata')
            data['pub_date'] = pub_data_attrib.get('date.publication')
            data['item_len'] = pub_data_attrib.get('item-length')
        except:
            pass

        try:
            data['abstract'] = root.find(
                './NewsItem/NewsComponent/ContentItem'
                '/DataContent/nitf/body/body.head/abstract/').text
        except:
            pass

        try:
            data['owner'] = root.find(
                './NewsItem/NewsComponent/ContentItem/DataContent/nitf/'
                'body/body.head/rights/').text
        except:
            pass

        try:
            data['story_data'] = root.find(
                './NewsItem/NewsComponent/ContentItem/DataContent/nitf/'
                'body/body.head/dateline/story.date').get('norm')
        except:
            pass

        try:
            body = root.find(
                './NewsItem/NewsComponent/ContentItem/DataContent/nitf/'
                'body/body.content')
            data['body'] = u"\n".join(
                u"<p>{0}</p>".format(p.text) for p in body)
        except:
            pass

        if not all([data.get('body'), data.get('headline')]):
            self.verbose_print(
                "Data does not have body and headline %s" % str(data))
            return

        return data

    def parse_dt(self, s):
        self.verbose_print("REceived to parse_dt %s" % s)
        try:
            new_s = datetime.strptime(s[:8], "%Y%m%d")
            self.verbose_print("parsed to %s" % new_s)
            return new_s
        except Exception as e:
            self.verbose_print("CAnt parse dt")
            self.verbose_print(str(e))
            return

    def create_entry(self, data):
        if not data:
            self.verbose_print("data is null")
            return

        # working
        entry_title = unicode(data.get('headline'))

        try:
            db_entry, created = self.entry_model.objects.get_or_create(
                entry_feed=self.feed,
                channel=self.feed.get_channel(),
                title=entry_title[:140],
                slug=slugify(self.feed.slug + "-" + entry_title[:150]),
                entry_title=entry_title,
                site=self.feed.site,
                user=self.feed.user,
                published=self.feed.publish_entries,
                show_on_root_channel=True
            )
            db_entry.entry_description = unicode(data.get('abstract', ''))
            db_entry.entry_content = unicode(data.get('body', ''))
            db_entry.entry_category = unicode(data.get('iptc_matter', ''))
            db_entry.hat = unicode(data.get('subheadline', ''))
            db_entry.entry_category_code = unicode(data.get('iptc_code', ''))

            db_entry.entry_published_time = self.parse_dt(
                data.get('pub_date', data.get('story_data', None))
            )

            try:
                db_entry.entry_json = json.dumps(data)
            except Exception as e:
                self.verbose_print("Cound not dump json %s" % str(data))
                self.verbose_print(str(e))

            db_entry.save()
            self.verbose_print("Entry saved: %s" % db_entry.pk)

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

    def record_log(self, s):
        self.log_model.objects.create(
            feed=self.feed,
            type="created",
            text=s
        )
        self.verbose_print("Process log created")

    def process(self):
        self.connect()
        self.ftp.cwd(self.feed.source_root_folder)
        self.verbose_print("Root folder changed to: %s" % self.feed.source_root_folder)

        self.count = 0
        self.ftp.retrlines('NLST', self.process_file)


# LIST retrieves a list of files and information about those files.
# NLST retrieves a list of file names.
# On some servers, MLSD retrieves a machine readable list of files and information
# about those files


{'story_data': '20130712T192900+0000',
 'body': u'<p>Montevid\xe9u, 12 jul (EFE).- Os pa\xedses do Mercosul decidiram nesta sexta-feira em sua c\xfapula semestral no Uruguai revogar a partir do dia 15 de agosto a suspens\xe3o do Paraguai, uma vez que Horacio Cartes assuma a presid\xeancia do pa\xeds.</p>\n<p>Ap\xf3s "avaliar positivamente" a realiza\xe7\xe3o das elei\xe7\xf5es gerais no Paraguai no \xfaltimo dia 21 de abril, os presidentes de Brasil, Dilma Rousseff; Argentina, Cristina Kirchner; Uruguai, Jos\xe9 Mujica; e Venezuela, Nicol\xe1s Maduro, decidiram "cessar" a suspens\xe3o imposta no dia 29 de junho de 2012 devido \xe0 cassa\xe7\xe3o por parte do Parlamento paraguaio do ent\xe3o presidente Fernando Lugo.</p>\n<p>A partir da posse do novo governo paraguaio "ser\xe3o considerados cumpridos" os requisitos estabelecidos no artigo 7 do Protocolo de Ushuaia sobre o compromisso democr\xe1tico.</p>\n<p>A partir do pr\xf3ximo m\xeas, o Paraguai "reassumir\xe1 plenamente seu direito de participar dos \xf3rg\xe3os do Mercosul e das delibera\xe7\xf5es", informa a declara\xe7\xe3o dos l\xedderes.</p>\n<p>As autoridades do Paraguai, o quinto integrante do Mercado Comum do Sul, n\xe3o participam da reuni\xe3o. EFE</p>\n<p>jf/rsd</p>',
 'item_len': '00166',
 'iptc_matter': 'Organismos internacionais',
 'headline': u'Mercosul revogar\xe1 suspens\xe3o do Paraguai a partir de 15 de agosto',
 'iptc_code': '11014000',
 'iptc_type': u'Pol\xedtica',
 'subheadline': u'MERCOSUL C\xdaPULA',
 'owner': 'Agencia EFE',
 'pub_date': '20130712T192900+0000',
 'abstract': u'Os pa\xedses do Mercosul decidiram nesta sexta-feira em sua c\xfapula semestral no Uruguai revogar a partir do dia 15 de agosto a suspens\xe3o do Paraguai, uma vez que Horacio Cartes assuma a presid\xeancia do pa\xeds.'}
