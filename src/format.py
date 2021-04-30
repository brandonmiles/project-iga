import zipfile
import xml.etree.ElementTree
import json

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
WORD_PROPERTIES = '{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}'


def get_style():
    """
    Returns a dictionary containing style information

    Returns
    -------
    dict
        The dictionary has multiple keys, each can be set to None to void grading for that particular aspect of the
        format.
        'font' should be a list of the allowed fonts for the paper.
        'size' is an int that represents the allowed font size.
        'line_spacing' is a float that describes the spacing between every line.
        'after_spacing' is a float that describes the spacing after every paragraph.
        'before_spacing' is a float that describes the spacing before every paragraph.
        'page_width' is a float that describes the width of the page in inches.
        'page_height' is the same as 'page_width', except for height.
        'left_margin' is a float that describes the size of the left margin in inches.
        'bottom_margin', 'top_margin', and 'right_margin' are all the same as 'left_margin'.
        'header' is a float in inches that describes the size of the header.
        'footer' and 'gutter' are the same as the 'header'.
        'indent' is a float in inches for how far indented the beginning of each paragraph should be.
    """
    return {'font': None, 'size': None, 'line_spacing': None, 'after_spacing': None, 'before_spacing': None,
            'page_width': None, 'page_height': None, 'left_margin': None, 'bottom_margin': None, 'right_margin': None,
            'top_margin': None, 'header': None, 'footer': None, 'gutter': None, 'indent': None}


def get_format_file(filepath):
    """
    Returns style for given JSON file

    Parameters
    ----------
    filepath : str
        A string describing the location of a .json file holding a style.

    Returns
    -------
    dict
        A style dictionary matching grade.get_style().

    Raises
    ------
    FileNotFoundException
        Raises an exception with a message about the missing file.
    UnicodeDecodeError
        Raised whenever the given file isn't in a readable format file.
    JSONDecodeError
        Raised when not given a JSON file.
    KeyError
        Raised whenever the JSON file is missing fields.
    """
    with open(filepath) as data:
        json_obj = json.loads(data.read())

    style = {'font': json_obj['font'], 'size': json_obj["size"], 'line_spacing': json_obj["line_spacing"],
             'after_spacing': json_obj["after_spacing"], 'before_spacing': json_obj["before_spacing"],
             'page_width': json_obj["page_width"], 'page_height': json_obj["page_height"],
             'left_margin': json_obj["left_margin"], 'bottom_margin': json_obj["bottom_margin"],
             'right_margin': json_obj["right_margin"], 'top_margin': json_obj["top_margin"],
             'header': json_obj["header"], 'footer': json_obj["footer"], 'gutter': json_obj["gutter"],
             'indent': json_obj["indent"]}
    return style


def update_format_file(filepath, style):
    """
    Updates given JSON file's style

    Parameters
    ----------
    filepath : str
        A string that specifies a .json file location

    style : dict
        The style you want to store in the file, must match grade.get_style()'s keys.

    Returns
    -------
    bool
        Will return True if the style was stored successfully.

    Raises
    ------
    PermissionError
        Raised whenever missing the correct permissions to access a file at filepath.
    KeyError
        Raised when providing an incomplete style dictionary
    """
    if set(style.keys()) != set(get_style().keys()):
        raise KeyError

    json_obj = json.dumps(style, indent=1)
    data = open(filepath, 'w')
    data.write(json_obj)
    data.close()
    return True


class Format:
    """
    The Format class handles all of the .doc and .docx XML decompiling to generate a dictionary of the document's
    currently used fonts, sizes, and other formatting.

    Parameters
    ----------
    filepath : str
        This should be a filepath to the docx that you want to read. Giving it any other type of file will produce
        an error.

    Raises
    ------
    FileNotFoundError
        The given filepath doesn't exist.
    PermissionError
        The given file cannot be read.
    BadZipFile
        The given file cannot be unzipped.
    KeyError
        The file cannot be read correctly, most likey due to being broken.
    """
    __slots__ = ('__document', '__font', '__word_count', '__page_count', '__default_style')

    def __init__(self, filepath):
        # Opening up the needed xml documents
        file_tree = zipfile.ZipFile(filepath)
        self.__document = xml.etree.ElementTree.XML(file_tree.read('word/document.xml'))
        self.__font = xml.etree.ElementTree.XML(file_tree.read('word/fontTable.xml'))
        general = xml.etree.ElementTree.XML(file_tree.read('docProps/app.xml'))
        style = xml.etree.ElementTree.XML(file_tree.read('word/styles.xml'))

        # Saving these values for later so we don't need to keep general
        self.__word_count = int(general.find(WORD_PROPERTIES + 'Words').text)
        self.__page_count = int(general.find(WORD_PROPERTIES + 'Pages').text)

        # Need to get the default style now
        rPr = style.find(WORD_NAMESPACE + 'docDefaults').find(WORD_NAMESPACE + 'rPrDefault') \
            .find(WORD_NAMESPACE + 'rPr')
        pPr = style.find(WORD_NAMESPACE + 'docDefaults').find(WORD_NAMESPACE + 'pPrDefault') \
            .find(WORD_NAMESPACE + 'pPr')
        secPr = self.__document.find(WORD_NAMESPACE + 'body').find(WORD_NAMESPACE + 'sectPr')

        font = ''
        size = '24'
        line = '240'
        after = '160'
        before = '0'
        if rPr is not None:
            rFonts = rPr.find(WORD_NAMESPACE + 'rFonts')
            if WORD_NAMESPACE + 'ascii' in rFonts.keys():
                font = rFonts.attrib[WORD_NAMESPACE + 'ascii']
            else:
                if WORD_NAMESPACE + 'asciiTheme' in rFonts.keys():
                    font = rFonts.attrib[WORD_NAMESPACE + 'asciiTheme']
            if WORD_NAMESPACE + 'val' in rPr.keys():
                size = rPr.find(WORD_NAMESPACE + 'sz').attrib[WORD_NAMESPACE + 'val']
        if pPr is not None:
            if WORD_NAMESPACE + 'line' in pPr.keys():
                line = pPr.find(WORD_NAMESPACE + 'spacing').attrib[WORD_NAMESPACE + 'line']
            if WORD_NAMESPACE + 'after' in pPr.keys():
                after = pPr.find(WORD_NAMESPACE + 'spacing').attrib[WORD_NAMESPACE + 'after']
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
        self.__default_style = {'font': font, 'size': int(size) / 2, 'line_spacing': int(line) / 240,
                                'after_spacing': int(after) / 20, 'before_spacing': int(before) / 20,
                                'page_width': int(pgSzW) / 1440, 'page_height': int(pgSzH) / 1440,
                                'left_margin': int(pgMarLeft) / 1440, 'bottom_margin': int(pgMarBottom) / 1440,
                                'right_margin': int(pgMarRight) / 1440, 'top_margin': int(pgMarTop) / 1440,
                                'header': int(header) / 1440, 'footer': int(footer) / 1440,
                                'gutter': int(gutter) / 1440}

    def get_font_table(self):
        """
        Returns the font table provided by the XML document. By default, the table will always include Times
        New Roman, Calibri and Calibri Light.

        Returns
        -------
        list of str
            A list of fonts.
        """
        a = []

        for f in self.__font.iter(WORD_NAMESPACE + 'font'):
            a.append(f.attrib[WORD_NAMESPACE + 'name'])

        return a

    def get_font(self):
        """
        Returns all fonts used in the document, as well as their respective sizes

        Returns
        -------
        list of tuples
            A list of pairs, where each pair is a pair of the font name and the associated size used, followed by the
            number of times the set of fonts and sizes is used.
        """
        fonts = []

        paragraphs = self.__document.find(WORD_NAMESPACE + 'body')

        # Checking every paragraph
        for p in paragraphs.iter(WORD_NAMESPACE + 'p'):
            # Checking every sentence break-up
            for r in p.iter(WORD_NAMESPACE + 'r'):
                f = self.__default_style['font']
                s = 2 * self.__default_style['size']

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

    def get_spacing(self):
        """
        Returns line and paragraph spacings used in the document

        Returns
        -------
        list
            A list of the three floats, the first being the line spacing, followed by the after paragraph and before
            paragraph spacings.
        """
        spacing_list = []

        paragraphs = self.__document.find(WORD_NAMESPACE + 'body')

        # Check every paragraph
        for p in paragraphs.iter(WORD_NAMESPACE + 'p'):
            dl = 240 * self.__default_style['line_spacing']
            da = 20 * self.__default_style['after_spacing']
            db = 20 * self.__default_style['before_spacing']
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

    def get_indentation(self):
        """
        Returns score between 0 and 1 based on the document's indentation, where 0 indicates lack of indentation
        and 1 indicates an exclusive use of indentation

        Returns
        -------
        float
            A float, where 0 is no indents, 1 is all indented, and getting close to 0.5 means either inconsistent
            indentation or non-standard indentation, either way bad.
        """
        indent = 0
        paragraph_number = 0

        paragraphs = self.__document.find(WORD_NAMESPACE + 'body')

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

    def get_margin(self):
        """
        Returns a score between 0 and 3 based on the margins, where 0 indicates consistent margins and
        higher scores are increasingly inconsistent margins

        Returns
        -------
        float
            A float between 0.0 and 2.0 describing the margins consistency.
        """
        margin = 0
        paragraph_number = 0

        paragraphs = self.__document.find(WORD_NAMESPACE + 'body')

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
                    if WORD_NAMESPACE + 'hanging' in ind.keys():
                        if int(ind.attrib[WORD_NAMESPACE + 'hanging']) != 0:
                            margin += 1

        return margin / paragraph_number

    def get_text(self):
        """
        Returns
        -------
        str
            A string containing the all of the document's text.
        """
        text = ""
        paragraphs = self.__document.find(WORD_NAMESPACE + 'body')

        # Checking every paragraph
        for p in paragraphs.iter(WORD_NAMESPACE + 'p'):
            # Checking every sentence break-up
            for r in p.iter(WORD_NAMESPACE + 'r'):
                t = r.find(WORD_NAMESPACE + 't')
                # Attempt to get any text
                if t is not None:
                    text += t.text

        return text

    def get_word_count(self):
        """
        Returns
        -------
        int
            An integer describing the word count.
        """
        return self.__word_count

    def get_page_count(self):
        """
        Returns
        -------
        int
            An integer describing the number of pages in the document.
        """
        return self.__page_count

    def get_default_style(self):
        """
        Returns
        -------
        dict
            The default style used by the document.
        """
        return self.__default_style
