from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


def format(color, style=''):
    """ return QTextCharFormat """
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


STYLES = {
    'keyword': format('darkBlue', 'bold'),
    'function': format('black', 'bold'),
    'comment': format('gray'),
    'numbers': format('green'),
}


class Highlighter (QSyntaxHighlighter):
    keywords = [
        "ox", "blank", "solidox"]

    functions = [
        "target(s)*", "exec", "temp", "swipe", "drive", "optimize_start", "optimize_stop", "mode", "title", "notes", "solid", "flow", "sleep", "private"]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        rules = []
        rules += [(r'%s' % w, 0, STYLES['keyword']) for w in Highlighter.keywords]
        rules += [(r'\b%s\b' % o, 0, STYLES['function']) for o in Highlighter.functions]

        rules += [
            (r'^[0-1]?[0-9]\b', 0, STYLES['numbers']),
            (r'#[^\n]*', 0, STYLES['comment']),
        ]

        # QRegExp fuer jedes Muster
        self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """ Apply syntax highlighting to the given block of text """

        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                index  = expression.pos(nth)
                length = expression.cap(nth).length()
                self.setFormat(index, length, format)
                index  = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
