"""
A simple class to help with paging result sets
"""

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

import logging

log = logging.getLogger(__name__)


class Pager(object):
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
        self.total_pages = (self.total_items - 1) / page_size + 1
        
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