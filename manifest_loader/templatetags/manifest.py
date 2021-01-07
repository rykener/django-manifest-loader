from django import template
from manifest_loader.utils import _get_value, manifest, manifest_match

register = template.Library()


@register.tag('manifest')
def do_manifest(parser, token): 
    """Returns the manifest tag"""
    return ManifestNode(token)


@register.tag('manifest_match')
def do_manifest_match(parser, token):
    """Returns manifest match tag"""
    return ManifestMatchNode(token)


class ManifestNode(template.Node):
    """
    Template node for the manifest tag
    """
    def __init__(self, token):
        bits = token.split_contents()
        if len(bits) < 2:
            raise template.TemplateSyntaxError(
                "'%s' takes one argument (name of file)" % bits[0])
        self.bits = bits

    def render(self, context):
        """
        returns the url of the found asset
        """
        manifest_key = _get_value(self.bits[1], context)
        return manifest(manifest_key, context)


class ManifestMatchNode(template.Node):
    """
    Template node for the manifest match tag
    """
    def __init__(self, token):
        self.bits = token.split_contents()
        if len(self.bits) < 3:
            raise template.TemplateSyntaxError(
                "'%s' takes two arguments (pattern to match and string to "
                "insert into)" % self.bits[0]
            )

    def render(self, context):
        """
        returns a string of all found urls,
            each embedded in the provided string
        """
        search_string = _get_value(self.bits[1], context)
        output_tag = _get_value(self.bits[2], context)
        return manifest_match(search_string, output_tag, context)

