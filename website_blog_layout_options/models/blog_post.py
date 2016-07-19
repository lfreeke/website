# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from lxml import etree


class BlogPost(models.Model):

    _inherit = 'blog.post'

    @api.one
    @api.onchange('extract_auto', 'display_type', 'content', 'teaser_input')
    def _extract_teaser(self):
        if self.display_type == "teaser":
            # no empty teasers
            if (self.teaser_input or '') and (not self.extract_auto):
                self.teaser = self.teaser_input
            else:
                res = ""
                # limit length to roughly 3-4 lines.
                teaser_length = 500
                parser = etree.HTMLParser()
                if self.content:
                    tree = etree.fromstring(self.content, parser)
                    paragraphs = tree.xpath('//p')
                    # get the first non empty paragraph
                    for paragraph in paragraphs:
                        if paragraph.text and len(res) < teaser_length:
                            res = res + paragraph.text + '\n'
                        else:
                            break
                    # trim it to the intended length
                    self.teaser = res[:teaser_length] + " ..."
                    self.teaser_input = res[:teaser_length] + " ..."
                else:
                    # has no teaser or content,  just revert.
                    # frontend controls needed not to have a bad workflow.
                    # content cannot be inserted in backend by default.
                    # add content to backend in view
                    self.display_type = "no_teaser"

    @api.onchange('blog_id')
    def set_new_default(self):
        self.background_image_show = self.blog_id.background_image_show

    background_image_show = fields.Selection(
        string="Type of header image on blog post",
        selection=lambda self: self.blog_id._get_image_options(),
        default=lambda self: self.blog_id.background_image_show,
        required=True,
        help="Choose if how you want to display the blog post:"
        "Just the title above the post, a small header image"
        "above the blog post title, or a big full screen image,"
        "before showing the post, (odoo default)")

    thumbnail = fields.Many2one(
        string='Blog Post Thumbnail',
        comodel_name='ir.attachment',
        help='A small image shown in teaser and content'
    )

    display_type = fields.Selection(
        selection=lambda self: self.blog_id._get_display_types(),
        string='Display type',
        default=lambda self: self.blog_id.display_type or 'no_teaser',
        required=True,
        help="Select no_teaser if you just want the clickable title,"
             "in the list. Select Teaser if you want to display,"
             "title+first lines of post select Complete if you prefer,"
             "the entire text  to be viewed in the blog list.")

    teaser = fields.Text(string='Teaser for Blog Post',
                         compute="_extract_teaser")

    teaser_input = fields.Text(string="Teaser text")
    extract_auto = fields.Boolean(
        string="Create teaser from content", default=False)

    category_id = fields.Many2many(
        string="Categories",
        comodel_name='blog.category',
        help='Blog post category, categories are a different type of classification, other than tags')

