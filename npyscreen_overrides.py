from npyscreen import MultiLineEdit, BoxTitle, BufferPager

class EuMultiLineEdit(MultiLineEdit):
    def t_input_isprint(self, inp):
        from unicodedata import category        
        #valamiért a self._last_get_ch_was_unicode nem működik az eredeti npycurses esetén
        if self._last_get_ch_was_unicode and inp not in '\n\t\r':
            return True
        if category(chr(inp)) != 'Cc':
            return True
        else: 
            return False
        