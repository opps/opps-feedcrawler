
.PHONY: install
install:
	pip install -r requirements.txt --use-mirrors
	python setup.py develop

.PHONY: tx
tx:
	mkdir -p opps/feedcrawler/locale/en_US/LC_MESSAGES
	touch opps/feedcrawler/locale/en_US/LC_MESSAGES/django.po
	tx set --auto-remote https://www.transifex.com/projects/p/opps/resource/feedcrawler/
	tx set --auto-local -r opps.feedcrawler "opps/feedcrawler/locale/<lang>/LC_MESSAGES/django.po" --source-language=en_US --source-file "opps/feedcrawler/locale/en_US/LC_MESSAGES/django.po" --execute
	tx pull -f
