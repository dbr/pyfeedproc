#!/usr/bin/env python
import datetime

# http://www.feedparser.org/
import feedparser
# http://www.dalkescientific.com/Python/PyRSS2Gen.html
import PyRSS2Gen

# Get the data
parsed_feed = feedparser.parse('http://reddit.com/.rss')

items = [
    PyRSS2Gen.RSSItem(
        title = x.title,
        link = x.link,
        description = x.summary,
        guid = x.link,
        pubDate = datetime.datetime(
            x.modified_parsed[0],
            x.modified_parsed[1],
            x.modified_parsed[2],
            x.modified_parsed[3],
            x.modified_parsed[4],
            x.modified_parsed[5])
        )

    for x in parsed_feed.entries
]

# make the RSS2 object
# Try to grab the title, link, language etc from the orig feed

rss = PyRSS2Gen.RSS2(
    title = parsed_feed['feed'].get("title"),
    link = parsed_feed['feed'].get("link"),
    description = parsed_feed['feed'].get("description"),

    language = parsed_feed['feed'].get("language"),
    copyright = parsed_feed['feed'].get("copyright"),
    managingEditor = parsed_feed['feed'].get("managingEditor"),
    webMaster = parsed_feed['feed'].get("webMaster"),
    pubDate = parsed_feed['feed'].get("pubDate"),
    lastBuildDate = parsed_feed['feed'].get("lastBuildDate"),

    categories = parsed_feed['feed'].get("categories"),
    generator = parsed_feed['feed'].get("generator"),
    docs = parsed_feed['feed'].get("docs"),

    items = items
)


write_to_file = False

if write_to_file:
    rss.write_xml(
        open("/tmp/afeed.rss", "w")
    )
else:
    xml = rss.to_xml()
    print xml
