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

class Suffix:
    suffixes = ['H','A','DA','DAn','lA','lAr']
    vowels = u'aıuoeiüö'
    backvowels = vowels[:4]
    frontvowels = vowels[4:]
    backunrounded = backvowels[:2]
    backrounded = backvowels[2:]
    frontunrounded = frontvowels[:2]
    frontrounded = frontvowels[2:]
    hardconsonant = u'fstkçşhp'
    H = [u'ı',u'i',u'u',u'ü']
    ones = {'0':u'sıfır', '1':u'bir','2':u'iki','3':u'üç','4':u'dört', '5':u'beş','6':u'altı','7':u'yedi','8':u'sekiz','9':u'dokuz'}
    tens =    {'1':u'on','2':u'yirmi','3':u'otuz','4':u'kırk','5':u'elli','6':u'altmış','7':u'yetmiş','8':u'seksen','9':u'doksan'}
    digits =  {0:u'yüz',3:u'bin',6:u'milyon', 9:u'milyar',12:u'trilyon',15:u'katrilyon'}
    numbers = [ones, tens, digits]
    superscript = {u'\xB2':u"kare",u'\xB3':u"küp"}
    def __init__(self, dictpath="sozluk/kelimeler.txt", exceptions="sozluk/istisnalar.txt",
                 haplopath="sozluk/unludusmesi.txt", poss="sozluk/iyelik.txt", othpath = "sozluk/digerleri.txt"):
        self.update = False
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
                         ret = pattern.search(line)
                         if ret == None:
                             l = line.strip().lower()
                             self.others[l] = l + 'e'
                         else:
                             self.others[ret.group('abbr').lower()] = ret.group('eqv').lower()
        except IOError:
            raise DictionaryNotFound

    def _readNumber(self, number):
        """Reads number and returns last word of it
           Example:
                1920    -> yirmi
                1993    -> üç
                bordo61 -> bir
        """
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
        else:
            lastVowelOfName = [letter for letter in reversed(name) if letter in self.vowels][0]
        firstVowelofSuffix = [letter for letter in suffix if letter in self.vowels][0]
        return ((lastVowelOfName in self.frontvowels) or isFrontVowel) == (firstVowelofSuffix in self.frontvowels)
    def _surfacetolex(self, suffix):
        """Turns given suffix to lex form"""
        translate_table = [('ae','A'),(u'ıiuü','H')]
        for surface,lex in translate_table:
            for letter in surface:
                suffix = suffix.replace(letter,lex)
        return suffix
    def _checkCompoundNoun(self, name):
        """Checks if given name is a compound noun or not"""
        probablesuff = {self._surfacetolex(name[i:]):name[i:] for i in range(-1,-5,-1)}
        possessivesuff = {'lArH','H','yH','sH'}
        for posssuff in probablesuff.viewkeys() & possessivesuff: # olabilecek ekler içinde yukardakilerin hangisi varsa dön
            wordpairs = self._divideWord(name, posssuff) # [["gümüş,"su"]] olarak dönecek
            for wordpair in wordpairs:
                if self._checkVowelHarmony(wordpair[-1], probablesuff[posssuff]): #if it is not empty
                    self.update = True
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
    def makeInstrumental(self, name, apostrophe=True):
        return self.constructName(name,Suffixes.INS,apostrophe)
    def makePlural(self, name, apostrophe=True):
        return self.constructName(name,Suffixes.PLU,apostrophe)
    def constructName(self, name, suffix, apostrophe=True):
        return u"{name}{aps}{suffix}".format(name=name,aps= "'" if apostrophe else "", suffix=self.getSuffix(name,suffix))
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
        # TODO: eğer iki versiyon yaparsan bunu notlarına ekle
        # TODO: daha fazla case ekle
        # TODO: C++ ve ruby'de yaz

        if ((rawsuffix != Suffixes.INS and rawsuffix != Suffixes.PLU) and name[-1] in self.H and
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

        vowels = [letter for letter in reversed(name) if letter in self.vowels]
        if not vowels:
            lastVowel = 'e'
            name = name + 'e'
        else:
            lastVowel = vowels[0]

        if suffix[-1] == 'H':
            replacement = ( u'ü' if lastVowel in self.frontrounded   or (soft and lastVowel in self.backrounded)   else
                            u'i' if lastVowel in self.frontunrounded or (soft and lastVowel in self.backunrounded) else
                            u'u' if lastVowel in self.backrounded   else
                            u'ı'
                            )
            suffix = suffix.replace('H', replacement)
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
        if ((name[-1] in self.vowels and suffix[0] in self.vowels)
            or (rawsuffix == Suffixes.INS and name[-1] in self.vowels)):
            suffix = 'y' + suffix

        return suffix

    def __del__(self):
        #TODO: birden çok instance'ta patlayacak
        if self.update:
            self.possfile.seek(0)
            for item in self.possessive:
                if item:
                    self.possfile.write(item + '\n')

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

lcase_table = u'abcçdefgğhıijklmnoöprsştuüvyz' + u'eeüüöö\xC2\xE2\xDB\xFB\xD4\xF4'
ucase_table = u'ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ' + u'\xC2\xE2\xDB\xFB\xD4\xF4EEÜÜÖÖ'

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
    import sys
    if len(sys.argv) > 1:
        ekle = Suffix()
        name = unicode(sys.argv[1].decode('utf8'))
        if len(sys.argv) == 2:
            for sf in ekle.suffixes:
                ek = ekle.addSuffix(name,sf)
                print "{name}'{suffix}".format(name=name.encode('utf8'),suffix=ek.encode('utf8'))
        elif len(sys.argv) == 3:
            ek = ekle.addSuffix(name,sys.argv[2])
            print "{name}'{suffix}".format(name=name.encode('utf8'),suffix=ek.encode('utf8'))
