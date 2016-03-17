# -*- coding: UTF-8 -*-
import turkish
import io


class Suffix:
    suffixes = ['H','A','DA','DAn']
    vowels = u'aıuoeiüö'
    backvowels = vowels[:4]
    frontvowels = vowels[4:]
    backunrounded = backvowels[:2]
    backrounded = backvowels[2:]
    frontunrounded = frontvowels[:2]
    frontrounded = frontvowels[2:]
    hardconsonant = u'fstkçşhp'
    H = [u'ı',u'i',u'u',u'ü']
    numbers = {'0':u'sıfır', '1':u'bir','2':u'iki','3':u'üç','4':u'dört', '5':u'beş','6':u'altı','7':u'yedi','8':u'sekiz','9':u'dokuz'}
    tens =    {'1':u'on','2':u'yirmi','3':u'otuz','4':u'kırk','5':u'elli','6':u'altmış','7':u'yetmiş','8':u'seksen','9':u'doksan'}
    digits =  {2:u'yüz',3:u'bin',6:u'milyon', 9:u'milyar',12:u'trilyon',15:u'katrilyon'}

    def __init__(self, dictpath="sozluk/isim.itu", exceptions="sozluk/istisna.itu", haplopath="sozluk/unludus.itu", poss="sozluk/ihali.itu"):
        self.possfile   = io.open(poss,      "r+",encoding='utf-8')
        self.possessive = set(self.possfile.read().split('\n'))
        with io.open(dictpath,  "r+",encoding='utf-8') as dictfile,  \
             io.open(exceptions,"r+",encoding='utf-8') as exceptfile, \
             io.open(haplopath, "r+",encoding='utf-8') as haplofile:

            self.exceptions = set(exceptfile.read().split('\n'))
            self.haplology  = set(haplofile.read().split('\n'))
            self.dictionary = set(dictfile.read().split('\n')) | self.exceptions | self.haplology

    def _readNumber(self, number):
        if len(number) == 1 and number[-1] == '0': return u'sıfır'
        for i, letter in enumerate(reversed(number)):
            if letter != u'0':
                if i == 0:
                    return self.numbers[letter]
                if i == 1:
                    return self.tens[letter]
                else:
                    i = (3  if 3  < i < 6  else
                         6  if 6  < i < 9  else
                         9  if 9  < i < 12 else
                         12 if 12 < i < 15 else
                         15 if 15 < i      else
                         i)
                    return self.digits[i]

        return u'sıfır'

    def _divideWord(self,name, suffix=''):
        # TODO: üçe bölmeyi yap
        realsuffix = name[-len(suffix):]
        name = name[:-len(suffix)] if len(suffix) > 0 else name
        result = []
        if name in self.dictionary or \
           (suffix == 'H' and self._checkConsonantHarmony(name)):
            result.append([name])

        for i in range(2, len(name)-1): #ikiden başlıyoruz çünkü tek harfli kelime yok varsayıyoruz
            firstWord = name[:i]; secondWord = name[i:]
            #print firstWord.encode('utf8'), secondWord.encode('utf8')
            if firstWord in self.dictionary:
                if secondWord in self.dictionary or \
                   (suffix == 'H' and self._checkConsonantHarmony(secondWord)):
                     result.append([firstWord,secondWord])
                elif suffix == 'H':
                    secondWord = self._checkEllipsisAffix(secondWord,realsuffix)
                    if secondWord != "": result.append([firstWord,secondWord])
        return result
    def _checkEllipsisAffix(self, name, suffix):
        name = (name[:-1] + suffix + name[-1])
        return name if name in self.haplology else ""
    def _checkConsonantHarmony(self, name):
        return ((name.endswith(u'ğ') or name.endswith(u'g'))
                 and (name[:-1] + 'k') in self.dictionary)
    def _checkVowelHarmony(self, name, suffix):
        # TODO: doğruluğunu kontrol et
        lastVowelOfName = ''
        isFrontVowel = False
        if name in self.exceptions:
            isFrontVowel = True
        else:
            lastVowelOfName = [letter for letter in reversed(name) if letter in self.vowels][0]

        firstVowelofSuffix = [letter for letter in suffix if letter in self.vowels][0]
        return ((lastVowelOfName in self.frontvowels) or isFrontVowel) == (firstVowelofSuffix in self.frontvowels)
    def _surfacetolex(self, suffix):
        #TODO: gereksiz yere yavaş çalışıyor düzelt
        suffix = list(suffix)
        for i,letter in enumerate(suffix):
            if letter in ['a','e']:
                suffix[i] = 'A'
            elif letter in [u'ı','i','u',u'ü']:
                suffix[i] = 'H'
        return ''.join(suffix)
    def _checkCompoundNoun(self, name):
        probablesuff = {self._surfacetolex(name[i:]):name[i:] for i in range(-1,-5,-1)}
        possessivesuff = ['lArH','H','yH','sH']
        #return any(self._checkvowelharmony(result[-1], probablesuff[posssuff]) for posssuff in possessivesuff if posssuff in probablesuff.keys()
        #                                                                       for result in self._divideWord(name,posssuff))
        for posssuff in [x for x in possessivesuff if x in probablesuff.keys()]: # olabilecek ekler içinde yukardakilerin hangisi varsa dön
            results = self._divideWord(name, posssuff) # [["gümüş,"su"]] olarak dönecek
            for result in results:
                if self._checkVowelHarmony(result[-1], probablesuff[posssuff]): #if it is not empty
                    # TODO: kelimeyi i hali sözlüğüne ekle flag i true yap yazarken codeclerde \n sorunu falan var
                    return True
        return False
    def _checkExceptionalWord(self, name):
        return any(word[-1] in self.exceptions for word in self._divideWord(name)
                                               if  word[-1] != '')
        #check if second word is in exception lists
    def addSuffix(self, name, suffix):
        if len(name) == 0:
            raise NotValidString
        if not isinstance(name,unicode):
            raise NotUnicode
        if suffix not in self.suffixes:
            raise NotInSuffixes

        soft = False
        name = turkish.lower(name.strip().split(' ')[-1])
        # TODO: iki kere bölme yapıyoruz bunu düzelt
        if (name[-1] in self.H and name not in self.dictionary and
           (name in self.possessive or self._checkCompoundNoun(name))):
                suffix = 'n' + suffix
        elif name[-1].isnumeric():
            name = self._readNumber(name)         # if last character of string contains number then take it whole string as number and read it
        elif name in self.exceptions or  \
            (name not in self.dictionary and self._checkExceptionalWord(name)):
            soft = True
        lastVowel = [letter for letter in reversed(name) if letter in self.vowels][0]
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
        # and finally add buffer letter, if we added n buffer letter before this code will discarded
        if name[-1] in self.vowels and suffix[0] in self.vowels:
            suffix = 'y' + suffix

        return suffix

    def __del__(self):
        self.possfile.close()

class NotInSuffixes(Exception):
    pass
class NotUnicode(Exception):
    pass
class NotValidString(Exception):
    pass

def test():
    suffixes = ['H','A','DA','DAn']
    names = io.open("testcases",'r',encoding='utf-8').read().split('\n')
    ekle = Suffix();
    for name in names[:-1]:
        print name.encode("UTF-8")
        for suf in suffixes:
            suffix = ekle.addSuffix(name, suf)
            print "{}'{}".format(name.encode("utf-8"),suffix.encode("utf8"))
        print "-----------"

if __name__ == "__main__":
    test()
