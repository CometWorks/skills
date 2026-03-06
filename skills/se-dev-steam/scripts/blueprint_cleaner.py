#!/usr/bin/python3
# -*- coding: ascii -*-
import sys
from xml.sax.saxutils import prepare_input_source, XMLGenerator

try:
    from defusedxml.sax import parse
except ImportError:
    from xml.sax import parse


MAX_PROJECTION_DEPTH = 1


class BlueprintCleaner(XMLGenerator):
    """Removes ProjectedGrids from the second level of nesting

    Why? See https://support.keenswh.com/spaceengineers/pc/topic/projector-storing-nested-projector-data

    """
    def __init__(self, out):
        # Space Engineers is using UTF-8 encoded XMLs without a BOM and supports shorting empty elements
        super().__init__(out, encoding='UTF-8', short_empty_elements=True)
        self.projection_depth = 0
        self.keep = True

    def startElement(self, name, attrs):
        if name == 'ProjectedGrids':
            self.projection_depth += 1
            self.update_decision()

        if self.keep:
            super().startElement(name, attrs)

    def endElement(self, name):
        if self.keep:
            super().endElement(name)

        if name == 'ProjectedGrids':
            self.projection_depth -= 1
            self.update_decision()

    def update_decision(self):
        self.keep = self.projection_depth <= MAX_PROJECTION_DEPTH

    def characters(self, content):
        if self.keep:
            super().characters(content)

    def ignorableWhitespace(self, content):
        if self.keep:
            super().ignorableWhitespace(content)

    def processingInstruction(self, target, data):
        if self.keep:
            super().processingInstruction(target, data)


def clean_blueprint(clean_blueprint_path, dirty_blueprint_path):
    with open(dirty_blueprint_path, 'rt', encoding='utf8') as dirty_xml:
        reader = prepare_input_source(dirty_xml)
        with open(clean_blueprint_path, 'wt', encoding='utf8') as clean_xml:
            content_handler = BlueprintCleaner(clean_xml)
            parse(reader, content_handler)


def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} bp.sbc', file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    clean_blueprint(f'{path}.clean', path)


if __name__ == '__main__':
    main()
