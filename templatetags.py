from django.template.base import Library
from django.template.defaulttags import TemplateIfParser
from django.utils.safestring import mark_safe

from tags import InclusionTag
from tags import Tag
from tags import tag_block


#{ Reimplementation of popular tags


register = Library()


@register.tag('if')
class IfElifTag(Tag):
    """Smart if template tag with else-if support."""

    def __init__(self, *args, **kwargs):
        super(IfElifTag, self).__init__(*args, **kwargs)
        self._previous_condition_is_met = False

    @tag_block(
        'if', next_blocks=('elif', 'else', 'end_if'), resolve_parameters=False)
    def if_block(self, block, *raw_condition):
        return self._conditional_block(block, *raw_condition)
    
    @tag_block(
        'elif',
        next_blocks=('elif', 'else', 'end_if'),
        resolve_parameters=False,
        )
    def elif_block(self, block, *raw_condition):
        return self._conditional_block(block, *raw_condition)
    
    def _conditional_block(self, block, *raw_condition):
        if self._previous_condition_is_met:
            return mark_safe('')
        
        condition = TemplateIfParser(self.parser, raw_condition).parse()
        condition_is_met = condition.eval(self.template_context)
        if condition_is_met:
            self._previous_condition_is_met = True
            block_result = block.render(self.template_context)
        else:
            block_result = None

        return block_result
    
    @tag_block('else', next_blocks=('end_if',))
    def else_block(self, block):
        if self._previous_condition_is_met:
            return mark_safe('')
        
        return block.render(self.template_context)


@register.tag('headed_box')
class BoxWithHeadWidgetTag(InclusionTag):
    """
    Render a box with a header and a block of content.
    
    The header will be wrapped within a h2 tag if no other is specified
    as the second argument.
    
    .. code-block:: jinja
    
        {% headed_box 'h3' %}
            Title for the header
        {% begin_box_content %}
            <span>This is the body of the box</span>
        {% end_headed_box %}
    
    """

    template_name = 'headed_box.html'
    
    @tag_block(next_blocks=('begin_box_content',))
    def headed_box(self, block, title_tag='h2'):
        return {
            'title': block.render(self.template_context),
            'title_tag': title_tag,
            }
    
    @tag_block(next_blocks=('end_headed_box',))
    def begin_box_content(self, block):
        return {'content': block.render(self.template_context)}
