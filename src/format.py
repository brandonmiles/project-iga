import zipfile
import xml.etree.ElementTree
import json

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
WORD_PROPERTIES = '{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}'
STYLE_SKELETON = {'font': None,  # This should be a list of the font names
                  'size': None,  # This should be the allowed font size
                  'line_spacing': None,  # This is an float that defines the spacing between every line
                  'after_spacing': None,  # This is a float that defines the spacing after every paragraph
                  'before_spacing': None,  # This is a float that defines the spacing before every paragraph
                  'page_width': None,  # This is the page width in inches
                  'page_height': None,
                  'left_margin': None,  # The page margin size in inches
                  'bottom_margin': None,
                  'right_margin': None,
                  'top_margin': None,
                  'header': None,  # The size of the header space in inches
                  'footer': None,
                  'gutter': None,
                  'indent': None}


# Get the dictionary structure for the style
def get_style():
    return STYLE_SKELETON


# Get the style format from a JSON file
def get_format_file(filepath):
    try:
        data = open(filepath, 'r')
        json_obj = json.loads(data.read())

        style = {'font': json_obj['font'], 'size': json_obj["size"], 'line_spacing': json_obj["line_spacing"],
                 'after_spacing': json_obj["after_spacing"], 'before_spacing': json_obj["before_spacing"],
                 'page_width': json_obj["page_width"], 'page_height': json_obj["page_height"],
                 'left_margin': json_obj["left_margin"], 'bottom_margin': json_obj["bottom_margin"],
                 'right_margin': json_obj["right_margin"], 'top_margin': json_obj["top_margin"],
                 'header': json_obj["header"], 'footer': json_obj["footer"], 'gutter': json_obj["gutter"],
                 'indent': json_obj["indent"]}
        return style
    except FileNotFoundError:
        raise Exception(filepath + " not found")


# Store the style format as a JSON for later use
def update_format_file(filepath, style):
    if set(style.keys()) != set(STYLE_SKELETON.keys()):
        return False

    try:
        json_obj = json.dumps(style, indent=1)
        data = open(filepath, 'w')
        data.write(json_obj)
        return True

    except PermissionError:
        return False


# NOTES: Know these conversions
# Font Sizes: 24 = 12 pt font
# Margins and Indent: 1440 = 1 inch
class Format:

    # Open the docx as a series of xml files
    def __init__(self, filepath):
        try:
            # Opening up the needed xml documents
            file_tree = zipfile.ZipFile(filepath)
            self.document = xml.etree.ElementTree.XML(file_tree.read('word/document.xml'))
            self.font = xml.etree.ElementTree.XML(file_tree.read('word/fontTable.xml'))
            general = xml.etree.ElementTree.XML(file_tree.read('docProps/app.xml'))
            style = xml.etree.ElementTree.XML(file_tree.read('word/styles.xml'))

            # Saving these values for later so we don't need to keep general
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

            # Odds are, before paragraph line spacing doesn't exist, but a necessary countermeasure
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

            # Saving all these values as an easy to access dictionary
            self.default_style = {'font': font, 'size': int(size) / 2, 'line_spacing': int(line) / 240,
                                  'after_spacing': int(after) / 20, 'before_spacing': int(before) / 20,
                                  'page_width': int(pgSzW) / 1440, 'page_height': int(pgSzH) / 1440,
                                  'left_margin': int(pgMarLeft) / 1440, 'bottom_margin': int(pgMarBottom) / 1440,
                                  'right_margin': int(pgMarRight) / 1440, 'top_margin': int(pgMarTop) / 1440,
                                  'header': int(header) / 1440, 'footer': int(footer) / 1440,
                                  'gutter': int(gutter) / 1440}
        except FileNotFoundError:
            print(filepath + "not found")

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
            paragraph_number += 1
            pPr = p.find(WORD_NAMESPACE + 'pPr')
            if pPr is not None:
                ind = pPr.find(WORD_NAMESPACE + 'ind')
                if ind is not None:
                    if WORD_NAMESPACE + 'firstLine' in ind.keys():
                        # 720 is equal to half an inch, the correct standard indent length
                        if int(ind.attrib[WORD_NAMESPACE + 'firstLine']) == 720:
                            indent += 1
                        else:
                            if int(ind.attrib[WORD_NAMESPACE + 'firstLine']) != 0:
                                indent += 0.5

            return indent / paragraph_number

    # Returns a double, where 0 is consistent margins, and 1~2 is wildly inconsistent margins between paragraphs
    def get_margin(self):
        margin = 0
        paragraph_number = 0

        paragraphs = self.document.find(WORD_NAMESPACE + 'body')

        # Check every paragraph
        for p in paragraphs.iter(WORD_NAMESPACE + 'p'):
            paragraph_number += 1
            pPr = p.find(WORD_NAMESPACE + 'pPr')

            # Assume default unless otherwise stated
            if pPr is not None:
                ind = pPr.find(WORD_NAMESPACE + 'ind')
                if ind is not None:
                    if WORD_NAMESPACE + 'left' in ind.keys():
                        if int(ind.attrib[WORD_NAMESPACE + 'left']) != 0:
                            margin += 1
                    if WORD_NAMESPACE + 'right' in ind.keys():
                        if int(ind.attrib[WORD_NAMESPACE + 'right']) != 0:
                            margin += 1

            return margin / paragraph_number

    # Return the actual text of the file
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
                    text += t.text

        return text

    # Returns the documents count of words, note that the exact count of words is dependent on Words standards
    def get_word_count(self):
        return self.word_count

    # Returns the documents count of pages
    def get_page_count(self):
        return self.page_count

    # Returns the documents default style
    def get_default_style(self):
        return self.default_style
