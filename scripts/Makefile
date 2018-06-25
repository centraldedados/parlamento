scrape:
	# por omissão só descarregamos as da última legislatura, para todas é make scrape-all
	. `pwd`/.env/bin/activate; csvgrep ../data/urls-datasets.csv -c legislatura -m 13 | csvcut -c slug,url-json | tail -n +2 | sed 's/,/ /' > jsonurls.txt
	make fetch

scrape-all:
	# fazer a lista de URLs a ir buscar a partir da lista que fizemos no urls-datasets.csv
	. `pwd`/.env/bin/activate; csvcut ../data/urls-datasets.csv -c slug,url-json | tail -n +2 | sed 's/,/ /' > jsonurls.txt
	make fetch
fetch:
	# usar o wget para ir buscar cada um
	while read -r slug url; do wget $$url --output-document=$$slug-pre.json; done < jsonurls.txt
	# pós-processar o JSON com o jq
	for f in *-pre.json; do cat $$f | jq . > `echo $$f | sed 's/-pre//'`; done
	# apagar ficheiros temporários
	rm -f *-pre.json
	rm -f jsonurls.txt
	# gravar por cima dos antigos
	for f in *.json; do mv -f $$f ../data; done
	
install:
	virtualenv .env --python=/usr/bin/python3 --no-site-packages --distribute
	. `pwd`/.env/bin/activate; pip install -r requirements.txt

deploy:
	git add ../data/
	git commit -am "Atualização automática"; git push origin master
