#!/usr/bin/env python
"""
Allows you to programatically modify an RSS feed. It uses feedparser to parse the feeds.

You create a class, which extends FeedProc, with specifically named functions, for example, to remove all the letter "b" from the feed titles, you would do..

class IHateB(FeedProc):
    def parse_entries_title(title, full_item):
        return title.replace("b", "")

Whatever returned becomes the new title. This is ran on each feed entry.

If you wish to process the feeds title, you would do..

class AppendToTitle(FeedProc):
    def parse_feed_title(title, full_item):
        return "%s (I added this to the title!)" % (title)

The function name is important. parse_ is a prefix, entries is the part of the feedparser (the two useful ones are "entries" - the RSS feed items, and "feed" which has info about the feed, such as the feeds title)

To run the AppendToTitle processor on a feed, you would do
myproc = AppendToTitle("http://example.com/news.rss")
myproc()
"""
import feedparser

class FeedProc:
    def __init__(self, url):
        self.url = url

    def __call__(self):
        self._parse_feed()
        self._run_filters()

    def _parse_feed(self):
        self.feed = feedparser.parse(self.url)

    def _run_filters(self):
        for f_name in dir(self):
            # parse_entries_title
            if f_name.find("parse_") == 0 and f_name[6:].find("_") > -1:
                # entries
                element_section = f_name[6 : f_name[6:].find("_") + 6  ]
                # title
                element_name = f_name[f_name[6:].find("_") + 7 : ]

                if element_section in self.feed.keys():
                    print "found section", element_section

                    print "processing", element_name
                    for feed_item in self.feed['entries']:
                        orig_element = feed_item[element_name]
                        new_element = getattr(self, f_name)(orig_element,
                                                            feed_item)
                        feed_item[element_name] = new_element
                        print new_element
                    #end for feed_item
                else:
                    print "Invalid section %s (in function name %s)" % (
                        element_section, f_name
                    )
                #end if element_section
            #end if f_name
        #end for f_name
    #end __call__
#end FeedProc

class AppendToTitle(FeedProc):
    """Simple example processor.
    Appends a string to the start of each feed title."""
    def proc_entries_title(self, title, full_item):
        return "This is a title modification. %s %s" % (title, full_item['link'])

def main():
    # Setup the AppendToTitle processor on the reddit python RSS feed
    af = AppendToTitle("http://reddit.com/r/python/.rss")

    # Run the processor, it returns a string with the new RSS feed
    modified_feed = af()

    # Output the new feed
    print modified_feed

if __name__ == '__main__':
    main()