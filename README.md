![headline](http://i.hizliresim.com/lEbkol.png)

_Turk**Suf**Fixer_ is a Python (v2.7) library for creating Turkish dynamic messages. Turkish language has a very complex derivational and inflectional morphology. Thus, it is hard to generate dynamic messages like "location + DA" because "DA" (Locative suffix) can be "de", "te", "ta", "nde" or "nda"  with respect to vowels and consonants in the noun (vowel harmony rule). This library handles these problems:

 - **Simplest way possible:** No morphological analysis, no finite state machine stuff
 - **No installation:** You don't need install anything, just take and use it

We support *"Accusative" (-i hali), "Dative" (-e hali), "Locative" (-de hali), "Ablative" (-den hali) and "Genitive" (-in)* cases. Since no morphological analysis is done, sometimes it is not possible to find correct form of suffix. Although it is rare to encounter this condition, we mentioned what it is in the scope of library and what not in further sections.  

## Some Problematic Examples
![examples](http://i.hizliresim.com/D3WOk3.png)
## Example Usages

```py
#-*- coding: UTF-8 -*-
from TurkSufFixer import SufFixer
city = raw_input("Bir şehir girin (Type a city): ").decode('utf-8')
sfx = SufFixer() #create the object
print sfx.makeDative(city) + " gidiyorum."
print sfx.makeAblative(city, apostrophe=False) + " geliyorum."
```
Or you can write the same code as follows:

```py
#-*- coding: UTF-8 -*-
from TurkSufFixer import SufFixer
city = raw_input("Bir şehir girin (Type a city): ").decode('utf-8')
sfx = SufFixer() #create the object
print "{city:'DAT} gidiyorum.".format(city=sfx(city))
print "{city:ABL} geliyorum.".format(city=sfx(city))
```
You can see *Formatting* section for further reference.

![Some Examples](http://i.hizliresim.com/lEWrzl.png)
![More Examples](http://i.hizliresim.com/RQ2z1o.png)
## Dependencies
There is no external dependencies.

## Coverage of Library

Followings are covered:

 - Nouns (Proper Nouns; City, Country, Town names; Compound Nouns)
 - Numbers (includes time and dates)
 - Exceptional words (i.e. alkol, santral) handling
 - Foreign originated words (only valid for words that in others dictionary, see Dictionaries section)
 - Words that go under vowel ellipsis (i.e. "omuz")*
 - Nouns that follow consonant harmony (i.e. “Çalışma Bakanlığı”)*
 - Words that have irregular third person singular form (i.e. “sanayii”)*
 - Abbreviations
 - Superscripts *("²" as "kare", "³" as "küp")*

Followings are **not** covered:

 - Nouns with “cik”, “lik” “ci” suffixes (Words that already in dictionary is
excluded)*
 - Nouns that already in accusative, dative, locative or ablative case (because no morphological analysis)
 - Nouns that end with punctuation mark (This causes undefined behavior)
 - Compound nouns that are formed with 3 words*
 - Nouns that contains “ki” suffix
 - Nouns that ends with consonant which repeat itself before certain
   suffixes (i.e. şık+ı -> şıkkı)

\*(Only problematic if the noun is in possessive form)

## Functions

One key note is that you should pass *name* variable as **UNICODE** type. Also, *Apostrophe* variable is a boolean variable to determine whether there will be apostrophe between word and suffix.

 - **makeAccusative(name,apostrophe)**
 - **makeDative(name,apostrophe)**
 - **makeLocative(name,apostrophe)**
 - **makeAblative(name,apostrophe)**
 - **makeGenitive(name,apostrophe)**
 - **makeInstrumental(name,apostrophe)** *(limited functionality)*
 - **makePlural(name,apostrophe)** *(limited functionality)*

There is one more function: **getSuffix**. We do not recommend to use this function in your code. However, in case you need the surface form (processed final form) the suffix only, you can use this function (check for *constructName* function for sample usage).

## Formatting

Using string formatting to generate Turkish suffix has the same functionality (even more) calling member function we introduced earlier. For example (assuming *sfx* is an instance of *SufFixer*); `"{:'DAT}".format(sfx(u'Türkçe'))` is exactly same as `sfx.makeDative(u'Türkçe')`. Let's have a closer look to its syntax.

> text_format ::= "{" [field_name] ":" [extra_chars] "suffix_name}"

> field_name ::= argument_name

> extra_chars ::= any character you want to place between name and suffix

> suffix_name ::= "ACC" | "DAT" | "LOC" | "ABL" | "GEN" | "INS" | "PLU"


In short, you can use the first three letters of cases for formatting. Also you need to call the SufFixer instance with name which you will create suffix for. Let's give more examples to make it concrete.

```py
    >>> from TurkSufFixer import SufFixer
    >>> sfx = SufFixer()
    >>> name = u'Ahmet'
    >>> "{:ACC} biliyor.".format(sfx(name))
    'Ahmeti biliyor.'
    >>> "{:DAT} gidiyor.".format(sfx(name))
    'Ahmete gidiyor.'
    >>> "{:'DAT} gidiyor.".format(sfx(name))
    "Ahmet'e gidiyor."
    >>> "{person:'DAT} gidiyor.".format(person=sfx(name))
    "Ahmet'e gidiyor."
    >>> "{person:'DAT} gidiyor.".format(person=name)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: Invalid conversion specification
    >>> "{person:DAL} gidiyor.".format(person=sfx(name))
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "TurkSufFixer.py", line 99, in __format__
        sfx = self.getSuffix(name, suffix)
      File "TurkSufFixer.py", line 241, in getSuffix
        raise NotInSuffixes
    TurkSufFixer.NotInSuffixes
```

## Test

To run test (in main directory):

> $ python -m tests/test

You can add *-v* parameter for more verbose output. Additionally, you can add more test cases to testing operation by simply editing txt files in the *tests* folder.

## Dictionaries

There are 5 dictionaries in the implementation. Here are some properties that valid for all dictionaries:

 - Dictionaries must be saved as in UTF-8 encoding.
 - There must be only one word per line.
 - Dictionaries must use UNIX line ending (\n).
 - A line shouldn’t contain any whitespace character other than new line
   character.
 - All characters should be lower case in dictionaries.

We will explain only *digerleri (others) dictionary* which is the only one developer should make changes, other dictionaries shouldn't be changed generally (if there is an error in a dictionary please report).

*digerleri dictionary* is created for especially foreign words and some abbreviations. If a word is not pronounced as written, we need to put that word and its Turkish pronunciation into the *digerleri dictionary*. For example, we use the word "server" in Turkish but we don't write it as "sörvır". Therefore, to preserve vowel harmony we need to tell to the library how to treat the word. In this case, we should put this line into the dictionary:

> server -> sörvır

With this line, the library will consider *server* as *sörvır* from now on. Consequently, locative case of "server" will be *server'da* instead of *server'de*.  

 Abbreviations should be put in *digerleri dictionary* as well. Nevertheless, unlike first example, inserting *abd -> abede* or *tdk -> tedeka* into the dictionary is redundant because if you put *"abd"* or *"tdk"* to the dictionary without indicating its pronunciation, the library will consider them as abbreviation by default and they will be treated as *"abede"* or *"tedeka"* in evaluation (Some counter examples; "kg -> kilogram "cm -> santimetre").

## License
This project is published under MIT license. Please do not forget to give credit in your project if you use this library. If you would like, we would love to publish the names of projects that use this library.  
## More...

Other implementations:

- [C# Implementation](https://github.com/TurkSufFixer/TurkSufFixer-Csharp)
- [Java Implementation](https://github.com/TurkSufFixer/TurkSufFixer-Java)
- [PHP Implementation](https://github.com/TurkSufFixer/TurkSufFixer-PHP)
