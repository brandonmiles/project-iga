import zipfile
import xml.etree.ElementTree

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
WORD_PROPERTIES = '{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}'


# NOTES: Know these conversions
# Line Spacing: 240 = 1.0 line spacing
# Font Sizes: 24 = 12 pt font
# Margins and Indent: 1440 = 1 inch
class Format:

    # Open the docx as a series of xml files
    def __init__(self, file_name):
        try:
            file_tree = zipfile.ZipFile(file_name)
            self.document = xml.etree.ElementTree.XML(file_tree.read('word/document.xml'))
            self.font = xml.etree.ElementTree.XML(file_tree.read('word/fontTable.xml'))
            general = xml.etree.ElementTree.XML(file_tree.read('docProps/app.xml'))
            style = xml.etree.ElementTree.XML(file_tree.read('word/styles.xml'))

            self.word_count = int(general.find(WORD_PROPERTIES + 'Words').text)
            self.page_count = int(general.find(WORD_PROPERTIES + 'Pages').text)

            # Need to get the default style now
            rPr = style.find(WORD_NAMESPACE + 'docDefaults').find(WORD_NAMESPACE + 'rPrDefault') \
                .find(WORD_NAMESPACE + 'rPr')
            pPr = style.find(WORD_NAMESPACE + 'docDefaults').find(WORD_NAMESPACE + 'pPrDefault') \
                .find(WORD_NAMESPACE + 'pPr')
            secPr = self.document.find(WORD_NAMESPACE + 'body').find(WORD_NAMESPACE + 'sectPr')

            font = rPr.find(WORD_NAMESPACE + 'rFonts').attrib[WORD_NAMESPACE + 'ascii']
            size = rPr.find(WORD_NAMESPACE + 'sz').attrib[WORD_NAMESPACE + 'val']
            line = pPr.find(WORD_NAMESPACE + 'spacing').attrib[WORD_NAMESPACE + 'line']
            after = pPr.find(WORD_NAMESPACE + 'spacing').attrib[WORD_NAMESPACE + 'after']
            before = '0'
            if WORD_NAMESPACE + 'before' in pPr.keys():
                before = pPr.find(WORD_NAMESPACE + 'spacing').attrib[WORD_NAMESPACE + 'before']
            pgSzW = secPr.find(WORD_NAMESPACE + 'pgSz').attrib[WORD_NAMESPACE + 'w']
            pgSzH = secPr.find(WORD_NAMESPACE + 'pgSz').attrib[WORD_NAMESPACE + 'h']
            pgMarLeft = secPr.find(WORD_NAMESPACE + 'pgMar').attrib[WORD_NAMESPACE + 'left']
            pgMarBottom = secPr.find(WORD_NAMESPACE + 'pgMar').attrib[WORD_NAMESPACE + 'bottom']
            pgMarRight = secPr.find(WORD_NAMESPACE + 'pgMar').attrib[WORD_NAMESPACE + 'right']
            pgMarTop = secPr.find(WORD_NAMESPACE + 'pgMar').attrib[WORD_NAMESPACE + 'top']
            header = secPr.find(WORD_NAMESPACE + 'pgMar').attrib[WORD_NAMESPACE + 'header']
            footer = secPr.find(WORD_NAMESPACE + 'pgMar').attrib[WORD_NAMESPACE + 'footer']
            gutter = secPr.find(WORD_NAMESPACE + 'pgMar').attrib[WORD_NAMESPACE + 'gutter']

            self.default_style = {'font': font, 'size': int(size) / 2, 'line_spacing': int(line) / 240,
                                  'after_spacing': int(after) / 20, 'before_spacing': int(before) / 20,
                                  'page_width': int(pgSzW) / 1440, 'page_height': int(pgSzH) / 1440,
                                  'left_margin': int(pgMarLeft) / 1440, 'bottom_margin': int(pgMarBottom) / 1440,
                                  'right_margin': int(pgMarRight) / 1440, 'top_margin': int(pgMarTop) / 1440,
                                  'header': int(header) / 1440, 'footer': int(footer) / 1440,
                                  'gutter': int(gutter) / 1440}
        except FileNotFoundError:
            print("File doesn't exist")

    # Returns a list of all the fonts used, plus Times New Roman, Calibri and Calibri Light
    def get_font_table(self):
        a = []

        for f in self.font.iter(WORD_NAMESPACE + 'font'):
            a.append(f.attrib[WORD_NAMESPACE + 'name'])

        return a

    # Returns a list of Fonts paired with the used sizes
    def get_font(self):
        fonts = []

        paragraphs = self.document.find(WORD_NAMESPACE + 'body')

        # Checking every paragraph
        for p in paragraphs.iter(WORD_NAMESPACE + 'p'):
            # Checking every sentence break-up
            for r in p.iter(WORD_NAMESPACE + 'r'):
                f = self.default_style['font']
                s = 2 * self.default_style['size']

                rPr = r.find(WORD_NAMESPACE + 'rPr')
                # Attempt to grab the font and size, otherwise assume default is used
                if rPr is not None:
                    rFonts = rPr.find(WORD_NAMESPACE + 'rFonts')
                    if rFonts is not None:
                        if WORD_NAMESPACE + 'ascii' in rFonts.keys():
                            f = rFonts.attrib[WORD_NAMESPACE + 'ascii']
                        else:
                            if WORD_NAMESPACE + 'asciiTheme' in rFonts.keys():
                                f = rFonts.attrib[WORD_NAMESPACE + 'asciiTheme']
                    sz = rPr.find(WORD_NAMESPACE + 'sz')
                    if sz is not None:
                        s = sz.attrib[WORD_NAMESPACE + 'val']
                # Note that for whatever reason, font sizes are stored twice the actual pt size
                if (f, int(s) / 2) not in fonts:
                    fonts.append((f, int(s) / 2))

        return fonts

    # Returns a list of line spacing, after paragraph spacing, and before paragraph spacing
    def get_spacing(self):
        spacing_list = []

        paragraphs = self.document.find(WORD_NAMESPACE + 'body')

        # Check every paragraph
        for p in paragraphs.iter(WORD_NAMESPACE + 'p'):
            dl = 240 * self.default_style['line_spacing']
            da = 20 * self.default_style['after_spacing']
            db = 20 * self.default_style['before_spacing']
            pPr = p.find(WORD_NAMESPACE + 'pPr')

            # If any part is missing, assume default is used
            if pPr is not None:
                spacing = pPr.find(WORD_NAMESPACE + 'spacing')
                if spacing is not None:
                    if WORD_NAMESPACE + 'line' in spacing.keys():
                        dl = spacing.attrib[WORD_NAMESPACE + 'line']
                    if WORD_NAMESPACE + 'after' in spacing.keys():
                        da = spacing.attrib[WORD_NAMESPACE + 'after']
                    if WORD_NAMESPACE + 'before' in spacing.keys():
                        db = spacing.attrib[WORD_NAMESPACE + 'before']

            if (int(dl) / 240, int(da) / 20, int(db) / 20) not in spacing_list:
                spacing_list.append((int(dl) / 240, int(da) / 20, int(db) / 20))

        return spacing_list

    # Returns a double, where 0 is no indents, 1 is all indented, and getting close to 0.5 means either
    # inconsistent indentation or non-standard indentation, either way bad
    def get_indentation(self):
        indent = 0
        paragraph_number = 0

        paragraphs = self.document.find(WORD_NAMESPACE + 'body')

        # Check every paragraph
        for p in paragraphs.iter(WORD_NAMESPACE + 'p'):
            paragraph_number = paragraph_number + 1
            pPr = p.find(WORD_NAMESPACE + 'pPr')
            if pPr is not None:
                ind = pPr.find(WORD_NAMESPACE + 'ind')
                if WORD_NAMESPACE + 'firstLine' in ind.keys():
                    if int(ind.attrib[WORD_NAMESPACE + 'firstLine']) == 720:
                        indent = indent + 1
                    else:
                        if int(ind.attrib[WORD_NAMESPACE + 'firstLine']) != 0:
                            indent = indent + 0.5

            return indent / paragraph_number

    # Returns a double, where 0 is consistent margins, and 1~2 is wildly inconsistent margins between paragraphs
    def get_margin(self):
        margin = 0
        paragraph_number = 0

        paragraphs = self.document.find(WORD_NAMESPACE + 'body')

        # Check every paragraph
        for p in paragraphs.iter(WORD_NAMESPACE + 'p'):
            paragraph_number = paragraph_number + 1
            pPr = p.find(WORD_NAMESPACE + 'pPr')

            # Assume default unless otherwise stated
            if pPr is not None:
                ind = pPr.find(WORD_NAMESPACE + 'ind')
                if WORD_NAMESPACE + 'left' in ind.keys():
                    if int(ind.attrib[WORD_NAMESPACE + 'left']) != 0:
                        margin = margin + 1
                if WORD_NAMESPACE + 'right' in ind.keys():
                    if int(ind.attrib[WORD_NAMESPACE + 'right']) != 0:
                        margin = margin + 1

            return margin / paragraph_number

    def get_text(self):
        text = ""

        paragraphs = self.document.find(WORD_NAMESPACE + 'body')

        # Checking every paragraph
        for p in paragraphs.iter(WORD_NAMESPACE + 'p'):
            # Checking every sentence break-up
            for r in p.iter(WORD_NAMESPACE + 'r'):
                t = r.find(WORD_NAMESPACE + 't')
                # Attempt to any text
                if t is not None:
                    text = text + t.text

        return text

    # Returns the documents count of words
    def get_word_count(self):
        return self.word_count

    # Returns the documents count of pages
    def get_page_count(self):
        return self.page_count

    # Returns the documents default style
    def get_default_style(self):
        return self.default_style
