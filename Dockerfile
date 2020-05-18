FROM python:3
RUN pip3 install lxml
RUN pip3 install Scrapy
RUN pip3 install extruct
RUN pip3 install beautifulsoup4
RUN pip3 install extraction
RUN pip3 install nested-lookup
RUN pip3 install apify
COPY ./* ./
CMD [ "python3", "main.py" ]