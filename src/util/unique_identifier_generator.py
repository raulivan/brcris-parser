import slugify
import uuid
import hashlib

from util.text_transformers import removeStopwords, replaceHtmlChars

def brcrisid_generator(*words, hashStr=True, useReplaceHtmlChars=False):
    if useReplaceHtmlChars:
        words = [replaceHtmlChars(i) for i in words if i]
    new_words = []
    sw = ''
    for w in words:
        if w:
            sw = slugify.slugify(removeStopwords(w))
            if sw:
                new_words.append(sw)
    if len(new_words) == 0:
        return None
    identifier = '---'.join(new_words)
    if hashStr:
        identifier = hashlib.md5(identifier.encode('utf-8')).hexdigest()
    return identifier


def uuid_based_identifier_generator() -> str:
        return str(uuid.uuid4())
    
