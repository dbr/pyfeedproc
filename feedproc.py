#!/usr/bin/env python
#encoding:utf-8
#author:dbr/Ben
#project:py-feedproc
#repository:http://github.com/dbr/py-feedproc
#license:Public Domain

"""
This is a simple feed-processing framework, written in Python.

Allows you to programatically modify an RSS feed. It uses feedparser to parse the feeds.

Processors are classes, which inherent the FeedProc class. The processor uses specifically named functions to determine which item to modify. For example, proc_enteries_title will process each feed item's "title".

Each function is given two arguments, the first is the original value, the second is the entire element (with entries, this is the entire news <item>).
Each function simply returns the desired new value.

As a simple example processor, to truncate every RSS item's title to 20 characters:

class ExampleProcessor(FeedProc):
    proc_enteries_title(self, orig_title, full_item):
        truncated_title = orig_title[20:]
        return truncated_title

The whole system is quite simple. It is intended to remove annoyances from RSS feeds, such as adverts, similar to what "Yahoo Pipes" is, but FeedProc is *much* simpler, does not depend on third-party servers proxying, and is much more flexible (it is Python, you can call anything you with form the processor)
"""

import feedparser
import PyRSS2Gen
import datetime

class FeedProc:
    def __init__(self, url):
        self.url = url

    def __call__(self):
        """Runs filter on supplied URL, returns modified feed
        """
        self._parse_feed()
        self._run_filters()
        self._gen_modified_feed()
        return self.xml

    def _parse_feed(self):
        """Parses the feed using feedparser
        """
        self.feed = feedparser.parse(self.url)

    def _run_filters(self):
        """Runs all proc_ filters
        """
        for f_name in dir(self):
            # parse_entries_title
            if f_name.find("proc_") == 0 and f_name[5:].find("_") > -1:
                # entries
                element_section = f_name[5 : f_name[5:].find("_") + 5  ]
                # title
                element_name = f_name[f_name[6:].find("_") + 7 : ]
                
                if element_section in self.feed.keys():
                    for feed_item_index in xrange(len(self.feed['entries'])):
                        feed_item = self.feed['entries'][feed_item_index]
                        orig_element = feed_item[element_name]
                        
                        new_element = getattr(self, f_name)(orig_element,
                                                            feed_item)
                        self.feed['entries'][feed_item_index][element_name] = new_element
                    #end for feed_item
                else:
                    print "Invalid section %s (in function name %s)" % (
                        element_section, f_name
                    )
                #end if element_section
            #end if f_name
        #end for f_name
    #end _run_filters
    
    def _gen_modified_feed(self):
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

            for x in self.feed['entries']
        ]
        
        #rss = PyRSS2Gen.RSS2(
        #    title = self.feed['feed'].get("title"),
        #    link = self.feed['feed'].get("link"),
        #    description = self.feed['feed'].get("description"),
        #
        #    language = self.feed['feed'].get("language"),
        #    copyright = self.feed['feed'].get("copyright"),
        #    managingEditor = self.feed['feed'].get("managingEditor"),
        #    webMaster = self.feed['feed'].get("webMaster"),
        #    pubDate = self.feed['feed'].get("pubDate"),
        #    lastBuildDate = self.feed['feed'].get("lastBuildDate"),
        #
        #    categories = self.feed['feed'].get("categories"),
        #    generator = self.feed['feed'].get("generator"),
        #    docs = self.feed['feed'].get("docs"),
        #
        #    items = items
        #)
        valid_keys = ["title", "link", "description", "language", "copyright",
        "managingEditor", "webMaster", "pubDate", "lastBuildDate ",
        "categories", "generator", "docs", "items"]
        
        # Remove feed elements that PyRSS2Gen doesn't accept
        cleaned_args = {}
        for cur_key, cur_val in self.feed['feed'].items():
            if cur_key in valid_keys:
                cleaned_args[cur_key] = cur_val
        
        rss = PyRSS2Gen.RSS2(**cleaned_args)
        
        self.xml = rss.to_xml()
        return self.xml
    #end _gen_modified_feed
        
#end FeedProc

class AppendToTitle(FeedProc):
    """Simple example processor.
    Appends a string to the start of each feed title."""
    def proc_entries_title(self, title, full_item):
        return "This is a title modification. %s" % (title)

def main():
    # Setup the AppendToTitle processor on the reddit python RSS feed
    af = AppendToTitle("http://reddit.com/r/python/.rss")

    # Run the processor, it returns a string with the new RSS feed
    modified_feed = af()

    # Output the new feed
    print modified_feed

if __name__ == '__main__':
    main()