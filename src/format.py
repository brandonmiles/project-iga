import zipfile
import xml.etree.ElementTree

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
WORD_PROPERTIES = '{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}'


class Format:

    # Open the docx as a series of xml files
    def __init__(self, file_name):
        try:
            self.file_tree = zipfile.ZipFile(file_name)
            self.document = xml.etree.ElementTree.XML(self.file_tree.read('word/document.xml'))
            self.font = xml.etree.ElementTree.XML(self.file_tree.read('word/fontTable.xml'))
            self.general = xml.etree.ElementTree.XML(self.file_tree.read('docProps/app.xml'))
            self.style = xml.etree.ElementTree.XML(self.file_tree.read('word/styles.xml'))

            # Need to get the default style now
            font_info = self.style.find(WORD_NAMESPACE + 'docDefaults').find(WORD_NAMESPACE + 'rPrDefault') \
                .find(WORD_NAMESPACE + 'rPr')

            font = font_info.find(WORD_NAMESPACE + 'rFonts').attrib[WORD_NAMESPACE + 'ascii']
            size = font_info.find(WORD_NAMESPACE + 'sz').attrib[WORD_NAMESPACE + 'val']

            self.default_style = {'font': font, 'size': size}
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

        for p in paragraphs.iter(WORD_NAMESPACE + 'p'):
            for r in p.iter(WORD_NAMESPACE + 'r'):
                f = self.default_style['font']
                s = self.default_style['size']

                rPr = r.find(WORD_NAMESPACE + 'rPr')
                # Attempt to grab the font and size, otherwise assume default is used
                if rPr is not None:
                    rFonts = rPr.find(WORD_NAMESPACE+'rFonts')
                    if rFonts is not None:
                        if WORD_NAMESPACE+'ascii' in rFonts.keys():
                            f = rFonts.attrib[WORD_NAMESPACE+'ascii']
                        else:
                            if WORD_NAMESPACE+'asciiTheme' in rFonts.keys():
                                f = rFonts.attrib[WORD_NAMESPACE+'asciiTheme']
                    sz = rPr.find(WORD_NAMESPACE+'sz')
                    if sz is not None:
                        s = sz.attrib[WORD_NAMESPACE+'val']
                # Note that for whatever reason, font sizes are stored twice the actual pt size
                if (f, int(s)/2) not in fonts:
                    fonts.append((f, int(s)/2))

        return fonts

    # Returns the documents count of words
    def get_word_count(self):
        return self.general.find(WORD_PROPERTIES + 'Words').text

    # Returns the documents count of pages
    def get_page_count(self):
        return self.general.find(WORD_PROPERTIES + 'Pages').text

    # Returns the documents default style
    def get_default_style(self):
        return self.default_style
