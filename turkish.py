# -*- coding: utf8 -*-

# Do not use this table in your application.
# This table made for library usage
# Letters with circumflex will fail if you use this table
# All letters with circumflex (şapkalı) will translated to 'e'

lcase_table = u'abcçdefgğhıijklmnoöprsştuüvyz' + u'eeeeee\xC2\xE2\xDB\xFB\xD4\xF4'
ucase_table = u'ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ' + u'\xC2\xE2\xDB\xFB\xD4\xF4EEEEEE'

#print u'\xC2\xE2\xDB\xFB\xD4\xF4'.encode('UTF-8')

def lower(data):
    return ''.join(map(_turkishtolower, data))
def upper(data):
    return ''.join(map(_turkishtoupper, data))

def _turkishtolower(char):
    try:
        i = ucase_table.index(char)
        return lcase_table[i]
    except:
        return char

def _turkishtoupper(char):
    try:
        i = lcase_table.index(char)
        return ucase_table[i]
    except:
        return char
def test():
    names = [u'böğürtlen', u'BÖĞÜRTLEN', u'bÖğÜrTlen', u'çimşir', u'ÇiMŞiR', u'ÇİMŞİR'
             ,u'ılık', u'ILIK', u"İstanbul", u'kem\xE2l']
    for name in names:
        print lower(name).encode('utf-8')
        print upper(name).encode('utf-8')

if __name__ == '__main__':
    test()
