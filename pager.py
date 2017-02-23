"""
A simple class to help with paging result sets
"""

import logging

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class Pager(object):
    """
    Standard Pager used on back end of website.

    When viewing page 234 of 1000, the following page links will be displayed:
    
    1, 134, 184, 232, 233, 234, 235, 236, 284, 334, 1000
    """

    def __init__(self, page_size, page_number, query):
        self.page_size = page_size

        try:
            self.page_number = int(page_number)
        except ValueError:
            self.page_number = 1
        
        if self.page_number < 1:
            self.page_number = 1
        
        self.query = query
        
        # Do the paging here
        self.total_items = query.count()
        self.total_pages = (self.total_items - 1) // page_size + 1
        
        if self.page_number > self.total_pages:
            self.page_number = self.total_pages
        
        self.offset = self.page_size * (self.page_number - 1)
        if self.offset < 0:
            self.offset = 1

        self.items = query[self.offset:self.offset + self.page_size]
    
    @property
    def has_prev(self):
        return self.page_number > 1
    
    @property
    def has_next(self):
        return self.page_number < self.total_pages
    
    @property
    def prev(self):
        return self.page_number - 1
    
    @property
    def next(self):
        return self.page_number + 1
    
    @property
    def page_link_numbers(self):
        pages = [1]
        
        if self.total_pages <= 1:
            return pages
        
        if self.page_number > 103:
            pages.append(self.page_number - 100)
        
        if self.page_number > 53:
            pages.append(self.page_number - 50)
        
        if self.page_number > 3:
            pages.append(self.page_number - 2)
        
        if self.page_number > 2:
            pages.append(self.page_number - 1)
            
        if self.page_number != 1 and self.page_number != self.total_pages:
            pages.append(self.page_number)
            
        if self.page_number < self.total_pages - 1:
            pages.append(self.page_number + 1)

        if self.page_number < self.total_pages - 2:
            pages.append(self.page_number + 2)
        
        if self.page_number < self.total_pages - 52:
            pages.append(self.page_number + 50)

        if self.page_number < self.total_pages - 102:
            pages.append(self.page_number + 100)
        
        pages.append(self.total_pages)
        return pages

    @property
    def empty(self):
        return self.total_pages == 0


class SimplePager(Pager):
    """
    Uses the same api as above, but displays a range of continuous page numbers.
    If you are on page 6 of 10 the following page numbers will be displayed:

    1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    """

    def __init__(self, page_size, page_number, query, max_pages=12):
        """
        :param max_pages: The maximum number of page links to display
        """
        super().__init__(page_size, page_number, query)

        self.max_pages = max_pages
    
    @property
    def page_link_numbers(self):
        start = self.page_number - self.max_pages // 2 + 1
        if start < 1:
            start = 1

        end = start + self.max_pages - 1
        if end > self.total_pages:
            end = self.total_pages

            if start > 1:
                start = end - self.max_pages + 1

        return range(start, end + 1)


class ViewAllPager(object):
    """
    Uses the same API as pager, but lists all items on a single page.  This is to allow
    easy implementation of a "view all" function on a listing page
    """
    def __init__(self, query):
        self.page_number = 1

        self.query = query

        # Do the paging here
        self.total_items = query.count()
        self.page_size = self.total_items
        self.total_pages = 1

        self.offset = 0

        self.items = query.all()

    @property
    def has_prev(self):
        return False

    @property
    def has_next(self):
        return False

    @property
    def prev(self):
        return self.page_number - 1

    @property
    def next(self):
        return self.page_number + 1

    @property
    def page_link_numbers(self):
        return [1]

