#!/bin/bash
echo "Start to run crawler ..."
# go to the spider directory
cd /home/rdadmin/monthly-report-crawler
# run the spider
/home/rdadmin/.local/bin/poetry run scrapy crawl sensor