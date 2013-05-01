# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Group'
        db.create_table(u'feedcrawler_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
        ))
        db.send_create_signal(u'feedcrawler', ['Group'])

        # Adding model 'Feed'
        db.create_table(u'feedcrawler_feed', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site'])),
            ('date_available', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=150)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('xml_url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('published_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_polled_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feedcrawler.Group'], null=True, blank=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Channel'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('main_image', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='feed_image', null=True, on_delete=models.SET_NULL, to=orm['images.Image'])),
        ))
        db.send_create_signal(u'feedcrawler', ['Feed'])

        # Adding model 'Entry'
        db.create_table(u'feedcrawler_entry', (
            (u'article_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['articles.Article'], unique=True, primary_key=True)),
            ('entry_feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feedcrawler.Feed'])),
            ('entry_title', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('entry_link', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('entry_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('entry_content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('entry_published_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('entry_source', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'feedcrawler', ['Entry'])

        # Adding model 'FeedConfig'
        db.create_table(u'feedcrawler_feedconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site'])),
            ('date_available', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('key_group', self.gf('django.db.models.fields.SlugField')(max_length=150, null=True, blank=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=150)),
            ('format', self.gf('django.db.models.fields.CharField')(default='text', max_length=20)),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['articles.Article'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Channel'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='feedconfig_feeds', null=True, on_delete=models.SET_NULL, to=orm['feedcrawler.Feed'])),
        ))
        db.send_create_signal(u'feedcrawler', ['FeedConfig'])

        # Adding unique constraint on 'FeedConfig', fields ['key_group', 'key', 'site', 'channel', 'article', 'feed']
        db.create_unique(u'feedcrawler_feedconfig', ['key_group', 'key', 'site_id', 'channel_id', 'article_id', 'feed_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'FeedConfig', fields ['key_group', 'key', 'site', 'channel', 'article', 'feed']
        db.delete_unique(u'feedcrawler_feedconfig', ['key_group', 'key', 'site_id', 'channel_id', 'article_id', 'feed_id'])

        # Deleting model 'Group'
        db.delete_table(u'feedcrawler_group')

        # Deleting model 'Feed'
        db.delete_table(u'feedcrawler_feed')

        # Deleting model 'Entry'
        db.delete_table(u'feedcrawler_entry')

        # Deleting model 'FeedConfig'
        db.delete_table(u'feedcrawler_feedconfig')


    models = {
        u'accounts.customuser': {
            'Meta': {'object_name': 'CustomUser'},
            'accept_terms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'childs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'civil_state': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'complement': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'education': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'home_phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'lives_with': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'mobile_carrier': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'newsletter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'partner_newsletter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'salary_range': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'articles.article': {
            'Meta': {'ordering': "['-date_available']", 'object_name': 'Article'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']"}),
            'channel_long_slug': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'db_index': 'True'}),
            'channel_name': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'db_index': 'True'}),
            'child_class': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'db_index': 'True'}),
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'hat': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'}),
            'headline': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'article_images'", 'to': u"orm['images.Image']", 'through': u"orm['articles.ArticleImage']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['images.Image']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True'}),
            'short_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sources.Source']", 'null': 'True', 'through': u"orm['articles.ArticleSource']", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"})
        },
        u'articles.articleimage': {
            'Meta': {'object_name': 'ArticleImage'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articleimage_articles'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['articles.Article']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['images.Image']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'articles.articlesource': {
            'Meta': {'object_name': 'ArticleSource'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articlesource_articles'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['articles.Article']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articlesource_sources'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['sources.Source']"})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'channels.channel': {
            'Meta': {'object_name': 'Channel'},
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'homepage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'long_slug': ('django.db.models.fields.SlugField', [], {'max_length': '250'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'subchannel'", 'null': 'True', 'to': u"orm['channels.Channel']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'show_in_menu': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'feedcrawler.entry': {
            'Meta': {'ordering': "['-entry_published_time']", 'object_name': 'Entry', '_ormbases': [u'articles.Article']},
            u'article_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['articles.Article']", 'unique': 'True', 'primary_key': 'True'}),
            'entry_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'entry_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'entry_feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedcrawler.Feed']"}),
            'entry_link': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'entry_published_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry_source': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'entry_title': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'})
        },
        u'feedcrawler.feed': {
            'Meta': {'ordering': "['title']", 'object_name': 'Feed'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedcrawler.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_polled_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'feed_image'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['images.Image']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'published_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"}),
            'xml_url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'feedcrawler.feedconfig': {
            'Meta': {'unique_together': "(('key_group', 'key', 'site', 'channel', 'article', 'feed'),)", 'object_name': 'FeedConfig'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.Article']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'feedconfig_feeds'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['feedcrawler.Feed']"}),
            'format': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'key_group': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'feedcrawler.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'})
        },
        u'images.image': {
            'Meta': {'object_name': 'Image'},
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sources.Source']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'sources.source': {
            'Meta': {'object_name': 'Source'},
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '140'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        }
    }

    complete_apps = ['feedcrawler']