# -*- coding: UTF-8 -*-
import io
import re
class Suffixes:
    ACC = "H"
    DAT = "A"
    LOC = "DA"
    ABL = "DAn"
    INS = "lA"
    PLU = "lAr"
    GEN = "Hn"

class SufFixer:
    suffixes = [Suffixes.ACC,Suffixes.DAT,Suffixes.LOC,Suffixes.ABL,
                Suffixes.INS,Suffixes.PLU,Suffixes.GEN]
    vowels = u'aıuoeiüö'
    backvowels = vowels[:4]
    frontvowels = vowels[4:]
    backunrounded = backvowels[:2]
    backrounded = backvowels[2:]
    frontunrounded = frontvowels[:2]
    frontrounded = frontvowels[2:]
    roundedvowels   = u"uüoö"
    unroundedvowels = u"aeıi"
    hardconsonant = u'fstkçşhp'
    H = [u'ı',u'i',u'u',u'ü']
    ones = {'0':u'sıfır', '1':u'bir','2':u'iki','3':u'üç','4':u'dört', '5':u'beş','6':u'altı','7':u'yedi','8':u'sekiz','9':u'dokuz'}
    tens =    {'1':u'on','2':u'yirmi','3':u'otuz','4':u'kırk','5':u'elli','6':u'altmış','7':u'yetmiş','8':u'seksen','9':u'doksan'}
    digits =  {0:u'yüz',3:u'bin',6:u'milyon', 9:u'milyar',12:u'trilyon',15:u'katrilyon'}
    numbers = [ones, tens, digits]
    superscript = {u'\xB2':u"kare",u'\xB3':u"küp"}
    def __init__(self, dictpath="sozluk/kelimeler.txt", exceptions="sozluk/istisnalar.txt",
                 haplopath="sozluk/unludusmesi.txt", poss="sozluk/iyelik.txt", othpath = "sozluk/digerleri.txt"):
        self.updated = set()
        self.possfile   = io.open(poss, "r+" , encoding='utf-8')
        self.possessive = set(self.possfile.read().splitlines())
        pattern = re.compile(r"(?P<abbr>\w+) +-> +(?P<eqv>\w+)", re.UNICODE)
        try:
            with io.open(dictpath,  "r",encoding='utf-8') as dictfile,  \
                 io.open(exceptions,"r",encoding='utf-8') as exceptfile, \
                 io.open(haplopath, "r",encoding='utf-8') as haplofile,   \
                 io.open(othpath,   "r",encoding="utf-8") as otherfile:
                     self.exceptions = set(exceptfile.read().splitlines())
                     self.haplology  = set(haplofile.read().splitlines())
                     self.dictionary = set(dictfile.read().splitlines()) | self.exceptions | self.haplology
                     self.others = {}
                     for line in otherfile:
                         l = turkishLower(line.strip())
                         ret = pattern.search(l)
                         if ret == None:
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
        time1 = number.rfind(":")
        time2 = number.rfind(".")
        time = time1 if time1 != -1 else time2
        if time != -1 and len(number) == 5 and number[time+1:] == "00":
            number = number[:time]
        for i, letter in [(i,letter) for i,letter in enumerate(reversed(number))
                          if letter != u'0' and letter.isnumeric()]:
            if i < 2:
                return self.numbers[i][letter]
            else:
                i = (i / 3) * 3
                i = i if i < 15 else 15
                return self.numbers[2][i]
        return u'sıfır'

    def _divideWord(self,name, suffix):
        """Divides words to two words which are present in dictionary"""
        realsuffix = name[-len(suffix):]
        name = name[:-len(suffix)] if len(suffix) > 0 else name
        if name in self.dictionary or self._checkConsonantHarmony(name,suffix):
            yield [name]
        else:
            realword = self._checkEllipsisAffix(name,realsuffix)
            if realword: yield [realword]
        for i in range(2, len(name)-1): #ikiden başlıyoruz çünkü tek harfli kelime yok varsayıyoruz
            firstWord = name[:i]; secondWord = name[i:]
            if firstWord in self.dictionary:
                #check whether second word in dictionary or affected by consonant harmony rule
                if secondWord in self.dictionary or self._checkConsonantHarmony(secondWord,suffix):
                     yield firstWord,secondWord
                else:
                    secondWord = self._checkEllipsisAffix(secondWord,realsuffix)
                    if secondWord: yield firstWord,secondWord
    def _checkEllipsisAffix(self, name, realsuffix):
        """Checks ellipsis affixation rule
           if the word fits the word returns root of word
           otherwise returns empty string"""
        if realsuffix not in self.H: return ""
        name = (name[:-1] + realsuffix + name[-1])
        return name if name in self.haplology else ""
    def _checkConsonantHarmony(self, name, suffix):
        """Checks consonant harmony rule """
        return suffix == 'H' and any(name.endswith(lastletter) and (name[:-1] + replacement) in self.dictionary
                                     for lastletter,replacement in [(u'ğ',u'k'),(u'g',u'k'),(u'b',u'p'),(u'c',u'ç'),(u'd',u't')])

    def _checkVowelHarmony(self, name, suffix):
        """Checks vowel harmony"""
        lastVowelOfName = ''
        isFrontVowel = False
        if name in self.exceptions:
            isFrontVowel = True
        lastVowelOfName = [letter for letter in reversed(name) if letter in self.vowels][0]
        firstVowelofSuffix = [letter for letter in suffix if letter in self.vowels][0]
        return (((lastVowelOfName in self.frontvowels) or isFrontVowel) == (firstVowelofSuffix in self.frontvowels)
                and (firstVowelofSuffix not in self.H or (lastVowelOfName in self.roundedvowels) == (firstVowelofSuffix in self.roundedvowels)))
    def _surfacetolex(self, suffix):
        """Turns given suffix to lex form"""
        translate_table = [('ae','A'),(u'ıiuü','H')]
        for surface,lex in translate_table:
            for letter in surface:
                suffix = suffix.replace(letter,lex)
        return suffix
    def _checkCompoundNoun(self, name):
        """Checks if given name is a compound noun or not"""
        probablesuff = {self._surfacetolex(name[i:]):name[i:] for i in range(-1,-5,-1) if len(name[:i]) > 0}
        possessivesuff = {'lArH','H','yH','sH'}
        for posssuff in probablesuff.viewkeys() & possessivesuff: # olabilecek ekler içinde yukardakilerin hangisi varsa dön
            wordpairs = self._divideWord(name, posssuff) # [["gümüş,"su"]] olarak dönecek
            for wordpair in wordpairs:
                if self._checkVowelHarmony(wordpair[-1], probablesuff[posssuff]): #if it is not empty
                    self.updated.add(name)
                    self.possessive.add(name)
                    return True
        return False
    def _checkExceptionalWord(self, name):
        """Checks if second word of compound noun is in exception lists"""
        return any(word[-1] in self.exceptions for word in self._divideWord(name,"")
                                               if  word[-1])
    def makeAccusative(self, name, apostrophe=True):
        return self.constructName(name,Suffixes.ACC,apostrophe)
    def makeDative(self, name, apostrophe=True):
        return self.constructName(name,Suffixes.DAT,apostrophe)
    def makeLocative(self, name, apostrophe=True):
        return self.constructName(name,Suffixes.LOC,apostrophe)
    def makeAblative(self, name, apostrophe=True):
        return self.constructName(name,Suffixes.ABL,apostrophe)
    def makeGenitive(self, name, apostrophe=True):
        return self.constructName(name,Suffixes.GEN,apostrophe)
    def makeInstrumental(self, name, apostrophe=True):
        return self.constructName(name,Suffixes.INS,apostrophe)
    def makePlural(self, name, apostrophe=True):
        return self.constructName(name,Suffixes.PLU,apostrophe)
    def constructName(self, name, suffix, apostrophe=True):
        return u"{name}{aps}{suffix}".format(name=name.strip(),aps= "'" if apostrophe else "", suffix=self.getSuffix(name,suffix))
    def getSuffix(self, name, suffix):
        """Adds suffix to given name"""
        name = name.strip()
        if len(name) == 0:
            raise NotValidString
        if not isinstance(name,unicode):
            raise NotUnicode
        if suffix not in self.suffixes:
            raise NotInSuffixes
        rawsuffix = suffix
        soft = False
        split = name.split(' ')
        wordNumber = len(split)
        name = turkishLower(split[-1])
        # TODO: least recently use functool decoratorünü kullan python 3.5 e geçince
        if (name[-1] in self.H and rawsuffix[0] != "l" and
           (wordNumber > 1 or name not in self.dictionary) and (name in self.possessive or self._checkCompoundNoun(name))):
                suffix = 'n' + suffix
        elif name[-1] in "0123456789":
            name = self._readNumber(name)  # if last character of string contains number then take it whole string as number and read it
        elif name in self.exceptions or  \
            (name not in self.dictionary and self._checkExceptionalWord(name)):
            soft = True
        elif name in self.others:
            name = self.others[name]
        elif name[-1] in self.superscript:
            name = self.superscript[name[-1]]

        vowels = (letter for letter in reversed(name) if letter in self.vowels)
        try:
            lastVowel = next(vowels)
        except StopIteration:
            lastVowel = 'a' if name.endswith('k') else 'e'
            name = name + lastVowel

        if 'H' in suffix:
            replacement = ( u'ü' if lastVowel in self.frontrounded   or (soft and lastVowel in self.backrounded)   else
                            u'i' if lastVowel in self.frontunrounded or (soft and lastVowel in self.backunrounded) else
                            u'u' if lastVowel in self.backrounded   else
                            u'ı'
                            )
            suffix = suffix.replace('H', replacement)
            if  rawsuffix == Suffixes.GEN and suffix[0] != 'n' and name[-1] in self.vowels:
                suffix = 'n' + suffix
        else:
            if lastVowel in self.frontvowels or soft:
                suffix = suffix.replace('A', 'e')
            else:
                suffix = suffix.replace('A', 'a')

            if name[-1] in self.hardconsonant:
                suffix = suffix.replace('D','t')
            else:
                suffix = suffix.replace('D','d')
        # and finally add buffer letter, if we added n buffer letter before this code will be discarded
        # for instrumental case, it will add "y" if name ends with vowel
        if (name[-1] in self.vowels and
		   ((suffix[0] in self.vowels) or (rawsuffix == Suffixes.INS))):
            suffix = 'y' + suffix

        return suffix

    def __del__(self):
        if self.updated:
            for news in self.updated:
                self.possfile.write(news + "\n")
        self.possfile.close()

class NotInSuffixes(Exception):
    pass
class NotUnicode(Exception):
    pass
class NotValidString(Exception):
    pass
class DictionaryNotFound(Exception):
    pass


# Do not use this table in your application.
# This table made for library usage
# Letters with circumflex will fail if you use this table
# All letters with circumflex (şapkalı) will translated to correspondence front vowels

lcase_table = u'abcçdefgğhıijklmnoöprsştuüvyz' + u'eeiiüüöö\xC2\xE2\xDB\xFB\xD4\xF4'
ucase_table = u'ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ' + u'\xC2\xE2\xCE\xEE\xDB\xFB\xD4\xF4EEÜÜÖÖ'

def turkishLower(data):
    return ''.join(map(_turkishtolower, data))
def turkishUpper(data):
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


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(prog = "TurkSufFixer", \
                                     description = "If you don't give any parameter, the program prints all the noun cases.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("word", nargs = '?',help = "Input word")
    group.add_argument('infile', nargs = '?', type=argparse.FileType('r'), default=sys.stdin, help = "Default is the standart input")
    parser.add_argument("-a", "--acc", action = "store_true", help = "Print Accusative Case")
    parser.add_argument("-d", "--dat", action = "store_true", help = "Print Dative Case")
    parser.add_argument("-l", "--loc", action = "store_true", help = "Print Locative Case")
    parser.add_argument("-b", "--abl", action = "store_true", help = "Print Ablative Case")
    parser.add_argument("-g", "--gen", action = "store_true", help = "Print Genitive Case")
    parser.add_argument("-i", "--ins", action = "store_true", help = "Print Instrumental Case")
    parser.add_argument("-p", "--plu", action = "store_true", help = "Print Plural Case")
    parser.add_argument("-s", "--getSuffix", action = "store_true", help = "Print suffixes without input word")
    parser.add_argument("-n", "--noapostrophe", action = "store_true", help = "Don't put apostrophe between the word and suffix")
    args = parser.parse_args()
    parse_list = [args.acc,args.dat,args.loc,args.abl,args.ins,args.plu,args.gen]
    if not any(parse_list): parse_list = [True for _, _ in enumerate(parse_list)]
    cmd_suffix = zip(parse_list, SufFixer.suffixes)
    noapostrophe = args.noapostrophe
    lines = args.infile.readlines() if args.word == None else [args.word]
    sfx = SufFixer()
    for line in lines:
        name = line.decode("utf8").strip()
        for cond, suff in [(cond, suff) for cond, suff in cmd_suffix if cond]:
            if args.getSuffix:
                print sfx.getSuffix(name,suff).encode("utf8")
            else:
                print u"{}{}{}".format(name, "" if noapostrophe else "'", sfx.getSuffix(name,suff)).encode("utf8")
