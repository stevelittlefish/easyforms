"""
Classes for configuration of some of the more advanced fields
"""

import logging
import copy

from flask import url_for

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class CkeditorConfig(object):
    def __init__(
            self,
            ckeditor_url=None,
            filemanager_url='/fm/index.html',
            filemanager_iframe=True,
            underline_enabled=False,
            subscript_enabled=False,
            superscript_enabled=False,
            cut_enabled=False,
            copy_enabled=False,
            paste_enabled=False,
            undo_enabled=False,
            redo_enabled=False,
            anchor_enabled=False,
            image_enabled=True,
            codesnippet_enabled=False,
            allow_all_extra_content=False,
            allowed_content=None,
            disallowed_content=None,
            pretty_print_html=True,
            pretty_print_html_line_length=110,
            strip_empty_paragraphs=True,
            strip_nbsp=True,
            entities_latin=True,
            default_height=None,
            format_tags='p;h2;h3;h4;pre',
            custom_styles_js_url=None,
            custom_contents_css_url=None,
            force_paste_as_plain_text=False,
            unwrap_images=False
    ):
        """
        Used to configure the CkeditorField

        :param ckeditor_url: Url of ckeditor.js
        :param filemanager_url: Url of filebrowser for image widget
        :param filemanager_iframe: Whether or not to use flaskfilemanager iframe mode (recommended)
        :param underline_enabled: Enable the underline button
        :param subscript_enabled: Enable the subscript button
        :param superscript_enabled: Enable the superscript button
        :param cut_enabled: Enable the cut button
        :param copy_enabled: Enable the copy button
        :param paste_enabled: Enable the past button
        :param undo_enabled: Enable the undo button
        :param redo_enabled: Enable the redo button
        :param anchor_enabled: Enable the anchor button
        :param image_enabled: Enable the image button
        :param codesnippet_enabled: Enable the codesnippet button
        :param allow_all_extra_content: Allow all extra css classes and attributes to be saved.  This
                                        may be necessary if you have old content that you want to
                                        edit without totally trashing. This is ignored if
                                        allowed_content is set
        :param allowed_content: String defining elements that are allowed.  See CKEditor docs for info
        :param disallowed_content: String defininte elements that are not allowed
        :param pretty_print_html: Should the resulting html be formatted to be readable?
        :param pretty_print_html_line_length: What line length should be used for pretty printing
        :param strip_empty_paragraphs: Should empty paragraphs be removed
        :param strip_nbsp: Should nbsps be stripped
        :param entities_latin: Hmmm...
        :param default_height: Height to use if height field is not specified in field
        :param format_tags: Semicolon separated list of tags for format drop-down
        :param custom_styles_js_url: URL to custom styles.js
        :param custom_contents_css_url: URL to custom contents.css
        :param force_paste_as_plain_text: Should all pasted text have the formatting removed?
        :param unwrap_images: Set to true to automatically remove img tags from surrounding p tags.
                              This may be needed if you want to do something fancy with images, like
                              make them wider than the text content.
        """
        self._ckeditor_url = ckeditor_url
        self.filemanager_url = filemanager_url
        self.filemanager_iframe = filemanager_iframe
        self.underline_enabled = underline_enabled
        self.subscript_enabled = subscript_enabled
        self.superscript_enabled = superscript_enabled
        self.cut_enabled = cut_enabled
        self.copy_enabled = copy_enabled
        self.paste_enabled = paste_enabled
        self.undo_enabled = undo_enabled
        self.redo_enabled = redo_enabled
        self.anchor_enabled = anchor_enabled
        self.image_enabled = image_enabled
        self.codesnippet_enabled = codesnippet_enabled
        self.allow_all_extra_content = allow_all_extra_content
        self.allowed_content = allowed_content
        self.disallowed_content = disallowed_content
        self.pretty_print_html = pretty_print_html
        self.pretty_print_html_line_length = pretty_print_html_line_length
        self.strip_empty_paragraphs = strip_empty_paragraphs
        self.strip_nbsp = strip_nbsp
        self.entities_latin = entities_latin
        self.default_height = default_height
        self.format_tags = format_tags
        self.custom_styles_js_url = custom_styles_js_url
        self.custom_contents_css_url = custom_contents_css_url
        self.force_paste_as_plain_text = force_paste_as_plain_text
        self.unwrap_images = unwrap_images

    def clone(self, **kwargs):
        out = copy.deepcopy(self)

        for attr in kwargs:
            if hasattr(out, attr):
                setattr(out, attr, kwargs[attr])
            else:
                raise TypeError('{} is an invalid keyword argument for this function'.format(attr))

        return out

    @property
    def ckeditor_url(self):
        if self._ckeditor_url:
            return self._ckeditor_url

        return url_for('static', filename='ckeditor/ckeditor.js')

    @ckeditor_url.setter
    def ckeditor_url(self, value):
        self._ckeditor_url = value

    @property
    def remove_buttons(self):
        buttons = []
        if not self.underline_enabled:
            buttons.append('Underline')
        if not self.subscript_enabled:
            buttons.append('Subscript')
        if not self.superscript_enabled:
            buttons.append('Superscript')
        if not self.cut_enabled:
            buttons.append('Cut')
        if not self.copy_enabled:
            buttons.append('Copy')
        if not self.paste_enabled:
            buttons.append('Paste')
        if not self.undo_enabled:
            buttons.append('Undo')
        if not self.redo_enabled:
            buttons.append('Redo')
        if not self.anchor_enabled:
            buttons.append('Anchor')
        
        return ','.join(buttons)

    @property
    def extra_plugins(self):
        plugins = []
        if self.codesnippet_enabled:
            plugins.append('codesnippet')

        return ','.join(plugins)

    @property
    def remove_plugins(self):
        plugins = []
        if not self.image_enabled:
            plugins.append('image')
        if not self.codesnippet_enabled:
            plugins.append('codesnippet')

        return ','.join(plugins)

    @property
    def extra_allowed_content(self):
        if self.allowed_content:
            return self.allowed_content
        elif self.allow_all_extra_content:
            return '*(*);*{*}'
        return ''

