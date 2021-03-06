# -*- coding: UTF-8 -*-
import io
import re
import os
from collections import namedtuple
from pkg_resources import resource_string, resource_stream

MODULE_ABS_PATH = os.path.dirname(os.path.abspath(__file__))
POSS_DICT_PATH = os.path.join(MODULE_ABS_PATH, "sozluk", "iyelik.txt")
WORDS_FILE = "sozluk/kelimeler.txt"
EXCEPT_FILE = "sozluk/istisnalar.txt"
HAPL_FILE = "sozluk/unludusmesi.txt"
OTHER_FILE = "sozluk/digerleri.txt"


class Suffixer:
    vowels = u'aıuoeiüö'
    b_vowels = vowels[:4]
    f_vowels = vowels[4:]
    b_u_vowels = b_vowels[:2]
    b_r_vowels = b_vowels[2:]
    f_u_vowels = f_vowels[:2]
    f_r_vowels = f_vowels[2:]
    r_vowels = u"uüoö"
    u_vowels = u"aeıi"
    hard_consonant = u'fstkçşhp'
    H = [u'ı', u'i', u'u', u'ü']
    ones = {
        '0': u'sıfır',
        '1': u'bir',
        '2': u'iki',
        '3': u'üç',
        '4': u'dört',
        '5': u'beş',
        '6': u'altı',
        '7': u'yedi',
        '8': u'sekiz',
        '9': u'dokuz'}
    tens = {
        '1': u'on',
        '2': u'yirmi',
        '3': u'otuz',
        '4': u'kırk',
        '5': u'elli',
        '6': u'altmış',
        '7': u'yetmiş',
        '8': u'seksen',
        '9': u'doksan'}
    digits = {0: u'yüz', 3: u'bin', 6: u'milyon', 9: u'milyar', 12: u'trilyon', 15: u'katrilyon'}
    numbers = [ones, tens, digits]
    superscript = {u'\xB2': u"kare", u'\xB3': u"küp"}

    def __init__(self):
        Suffixes = namedtuple('Suffixes', ['ACC', 'DAT', 'LOC', 'ABL', 'INS', 'PLU', 'GEN'])
        self.suffixes = Suffixes(
            ACC='H',
            DAT='A',
            LOC='DA',
            ABL='DAn',
            INS='lA',
            PLU='lAr',
            GEN='Hn')
        self.s_h_pairs = [(u'ğ', u'k'), (u'g', u'k'), (u'b', u'p'), (u'c', u'ç'), (u'd', u't')]
        self.updated = set()
        self.possfile = io.open(POSS_DICT_PATH, "r+", encoding='utf-8')
        self.possessive = set(self.possfile.read().splitlines())
        self.time_pattern = re.compile(r"([01]?[0-9]|2[0-3])[.:]00")
        self.srf_to_lex_translate_table = {ord('a'): u'A', ord('e'): u'A',
                                           ord(u'ı'): u'H', ord(u'i'): u'H',
                                           ord(u'u'): u'H', ord(u'ü'): u'H'}
        
        words = resource_string(__name__, WORDS_FILE).decode("utf8").split()
        self.exceptions = set(resource_string(__name__, EXCEPT_FILE).decode("utf8").split())
        self.haplology = set(resource_string(__name__, HAPL_FILE).decode("utf8").split())
        self.dictionary = set(words) | self.exceptions | self.haplology
        pattern = re.compile(r"(?P<abbr>\w+) +-> +(?P<eqv>\w+)", re.UNICODE)
        try:
            with resource_stream(__name__, OTHER_FILE) as otherfile:
                self.others = {}
                for line in otherfile:
                    line = line.decode("utf8")
                    l = turkishSanitize(line.strip())
                    ret = pattern.search(l)
                    if ret is None:
                        self.others[l] = l + ('a' if l.endswith('k') else 'e')
                    else:
                        self.others[ret.group('abbr')] = ret.group('eqv')
        except IOError:
            raise DictionaryNotFound

    def _readNumber(self, number):
        """Reads number and returns last word of it
           Example:
                1920    -> yirmi
                1993    -> üç
                bordo61 -> bir
        """

        time_match = self.time_pattern.match(number)
        if time_match:
            number = time_match.groups()[0]

        for i, letter in [(i, letter) for i, letter in enumerate(number[::-1])
                          if letter != u'0' and letter.isnumeric()]:
            if i < 2:
                return self.numbers[i][letter]
            else:
                i = (i / 3) * 3
                i = i if i < 15 else 15
                return self.numbers[2][i]
        return u'sıfır'

    def _divideWord(self, name, suffix):
        """Divides words to two words which are present in dictionary"""
        realsuffix = name[-len(suffix):]
        name = name[:-len(suffix)] if len(suffix) > 0 else name
        if name in self.dictionary or self._checkConsonantHarmony(name, suffix):
            yield [name]
        else:
            realword = self._checkEllipsisAffix(name, realsuffix)
            if realword:
                yield [realword]
        # ikiden başlıyoruz çünkü tek harfli kelime yok varsayıyoruz
        for i in range(2, len(name) - 1):
            firstWord = name[:i]
            secondWord = name[i:]
            if firstWord in self.dictionary:
                # check whether second word in dictionary or affected by consonant harmony rule
                if secondWord in self.dictionary or self._checkConsonantHarmony(secondWord, suffix):
                    yield firstWord, secondWord
                else:
                    secondWord = self._checkEllipsisAffix(secondWord, realsuffix)
                    if secondWord:
                        yield firstWord, secondWord

    def _checkEllipsisAffix(self, name, realsuffix):
        """Checks ellipsis affixation rule
           if the word fits the word returns root of word
           otherwise returns empty string"""
        if realsuffix not in self.H:
            return ""
        name = (name[:-1] + realsuffix + name[-1])
        return name if name in self.haplology else ""

    def _checkConsonantHarmony(self, name, suffix):
        """Checks consonant harmony rule """
        if suffix == 'H':
            for lastletter, replacement in self.s_h_pairs:
                if name.endswith(lastletter) and (name[:-1] + replacement) in self.dictionary:
                    return True
        return False

    def _checkVowelHarmony(self, name, suffix):
        """Checks vowel harmony"""
        l_vowel_name = ''
        is_f_vowel = False
        if name in self.exceptions:
            is_f_vowel = True
        l_vowel_name = next(letter for letter in name[::-1] if letter in self.vowels)
        f_vowel_sfx = next(letter for letter in suffix if letter in self.vowels)
        # first we check for frontness ('e' follow 'eiüö')
        # then we check for roundness because for example 'ü' can't follow 'i'
        frontness = ((l_vowel_name in self.f_vowels) or is_f_vowel) == (f_vowel_sfx in self.f_vowels)
        roundness = (l_vowel_name in self.r_vowels) == (f_vowel_sfx in self.r_vowels)
        return (frontness and (roundness or (f_vowel_sfx not in self.H)))  # for e.g. karayolları

    def _surfacetolex(self, suffix):
        """Turns given suffix to lex form"""
        return suffix.translate(self.srf_to_lex_translate_table)

    def _checkCompoundNoun(self, name):
        """Checks if given name is a compound noun or not"""
        if name[-4:] == u"oğlu":
            return True
        probablesuff = {self._surfacetolex(name[i:]): name[i:]
                        for i in range(-1, -5, -1) if len(name[:i]) > 0}
        possessivesuff = {'lArH', 'H', 'yH', 'sH', u'lHğH'}
        # olabilecek ekler içinde yukardakilerin hangisi varsa dön
        for posssuff in probablesuff.viewkeys() & possessivesuff:
            wordpairs = self._divideWord(name, posssuff)  # [["gümüş,"su"]] olarak dönecek
            for wordpair in wordpairs:
                if self._checkVowelHarmony(wordpair[-1], probablesuff[posssuff]):
                    self.updated.add(name)
                    self.possessive.add(name)
                    return True
        return False

    def _checkExceptionalWord(self, name):
        """Checks if second word of compound noun is in exception lists"""
        return any(word[-1] in self.exceptions
                   for word in self._divideWord(name, "") if word[-1])

    def makeAccusative(self, name, apostrophe=True):
        return self.constructName(name, self.suffixes.ACC, apostrophe)

    def makeDative(self, name, apostrophe=True):
        return self.constructName(name, self.suffixes.DAT, apostrophe)

    def makeLocative(self, name, apostrophe=True):
        return self.constructName(name, self.suffixes.LOC, apostrophe)

    def makeAblative(self, name, apostrophe=True):
        return self.constructName(name, self.suffixes.ABL, apostrophe)

    def makeGenitive(self, name, apostrophe=True):
        return self.constructName(name, self.suffixes.GEN, apostrophe)

    def makeInstrumental(self, name, apostrophe=True):
        return self.constructName(name, self.suffixes.INS, apostrophe)

    def makePlural(self, name, apostrophe=True):
        return self.constructName(name, self.suffixes.PLU, apostrophe)

    def constructName(self, name, suffix, apostrophe=True):
        return u"{name}{aps}{suffix}".format(
            name=name.strip(), aps="'" if apostrophe else "", suffix=self.getSuffix(name, suffix))

    def getSuffix(self, name, suffix):
        """Adds suffix to given name"""
        name = name.strip()
        if len(name) == 0:
            raise NotValidString
        if not isinstance(name, unicode):
            raise NotUnicode
        if suffix not in self.suffixes:
            raise NotInSuffixes
        rawsuffix = suffix
        soft = False
        split = name.split(' ')
        wordNumber = len(split)
        name = turkishSanitize(split[-1])
        # TODO: least recently use functool decoratorünü kullan python 3.5 e geçince
        # if the raw suffix doesn't start with 'l' letter which means
        # the suffix is not plural or instrumental. So we can add 'n' buffer letter if appropiate
        if (name[-1] in self.H and rawsuffix[0] != "l" and
                (wordNumber > 1 or name not in self.dictionary) and
                (name in self.possessive or self._checkCompoundNoun(name))):
            suffix = 'n' + suffix
        elif name[-1] in "0123456789":
            # if last character of string contains number then take it whole string as
            # number and read it
            name = self._readNumber(name)
        elif name in self.exceptions or  \
                (name not in self.dictionary and self._checkExceptionalWord(name)):
            soft = True
        elif name in self.others:
            name = self.others[name]
        elif name[-1] in self.superscript:
            name = self.superscript[name[-1]]

        vowels = (letter for letter in name[::-1] if letter in self.vowels)
        try:
            lastVowel = next(vowels)
        except StopIteration:
            lastVowel = 'a' if name.endswith('k') else 'e'
            name = name + lastVowel

        if 'H' in suffix:
            # if the given name is not soft and it ends with backvowels
            # we can replace H with appropiate surface form
            # however on the 3rd line we use rounded vowels
            # the reason behind that we check whether the last vowel is back vowel
            # or the given name is not soft. Therefore, we left with the last vowel
            # can be front vowels or name can be soft. To determine 'H' surf form,
            # we only need to lookup the last vowels roundness.
            replacement = (u'u' if not soft and lastVowel in self.b_r_vowels else
                           u'ı' if not soft and lastVowel in self.b_u_vowels else
                           u'ü' if lastVowel in self.r_vowels else
                           u'i'
                           )

            suffix = suffix.replace('H', replacement)
        else:
            if lastVowel in self.f_vowels or soft:
                suffix = suffix.replace('A', 'e')
            else:
                suffix = suffix.replace('A', 'a')

            if name[-1] in self.hard_consonant:
                suffix = suffix.replace('D', 't')
            else:
                suffix = suffix.replace('D', 'd')
        # and finally add buffer letter, unless it is added previously
        # buffer letter "y" will be added if noun ends with vowel and suffix begins with vowel
        # for instrumental case, it will add "y" if name ends with vowel
        # for genitive case, "n" will be added
        if name[-1] in self.vowels:
            if (suffix[0] in self.vowels) or (rawsuffix == self.suffixes.INS):
                suffix = u"{buf}{suf}".format(
                    suf=suffix, buf='y' if rawsuffix != self.suffixes.GEN else 'n')

        return suffix

    def __del__(self):
        if self.updated:
            for news in self.updated:
                self.possfile.write(news + "\n")
        self.possfile.close()

class TurkSuffixerException(Exception):
    pass


class NotInSuffixes(TurkSuffixerException):
    pass


class NotUnicode(TurkSuffixerException):
    pass


class NotValidString(TurkSuffixerException):
    pass


class DictionaryNotFound(TurkSuffixerException):
    pass


lcase_table = u'abcçdefgğhıijklmnoöprsştuüvyz\u00E2\u00EE\u00FB\u00F4'
ucase_table = u'ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ\u00C2\u00CE\u00DB\u00D4'
convert_accent_table = {ord(f_c): t_c for f_c, t_c in zip(u'\u00E2\u00EE\u00FB\u00F4', u'eiüö')}
low_translate_table = {ord(f_c): t_c for f_c, t_c in zip(ucase_table, lcase_table)}


def turkishLower(data):
    return data.translate(low_translate_table)


def turkishSanitize(data):
    lowered = turkishLower(data)
    return lowered.translate(convert_accent_table)


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(prog="TurkSufFixer",
                                     description="If you don't give any parameter, the program prints all noun cases.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("word", nargs='?', help="Input word")
    group.add_argument('input_file', nargs='?', type=argparse.FileType(
        'r'), default=sys.stdin, help="Default is the standart input")
    parser.add_argument("-a", "--acc", action="store_true", help="Print Accusative Case")
    parser.add_argument("-d", "--dat", action="store_true", help="Print Dative Case")
    parser.add_argument("-l", "--loc", action="store_true", help="Print Locative Case")
    parser.add_argument("-b", "--abl", action="store_true", help="Print Ablative Case")
    parser.add_argument("-g", "--gen", action="store_true", help="Print Genitive Case")
    parser.add_argument("-i", "--ins", action="store_true", help="Print Instrumental Case")
    parser.add_argument("-p", "--plu", action="store_true", help="Print Plural Case")
    parser.add_argument("-s", "--getSuffix", action="store_true",
                        help="Print suffixes without input word")
    parser.add_argument("-n", "--noapostrophe", action="store_true",
                        help="Don't put apostrophe between the word and suffix")
    args = parser.parse_args()
    parse_list = [args.acc, args.dat, args.loc, args.abl, args.ins, args.plu, args.gen]
    if not any(parse_list):
        parse_list = [True for _, _ in enumerate(parse_list)]
    sfx = Suffixer()
    cmd_suffix = zip(parse_list, sfx.suffixes)
    noapostrophe = args.noapostrophe
    lines = args.input_file.readlines() if args.word is None else [args.word]
    for line in lines:
        name = line.decode("utf8").strip()
        for cond, suff in [(cond, suff) for cond, suff in cmd_suffix if cond]:
            if args.getSuffix:
                print sfx.getSuffix(name, suff).encode("utf8")
            else:
                print u"{}{}{}".format(name, "" if noapostrophe else "'", sfx.getSuffix(name, suff)).encode("utf8")
