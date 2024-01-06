import pymorphy2

from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    PER,
    NamesExtractor,

    Doc
)

morph = pymorphy2.MorphAnalyzer()

segmenter = Segmenter()
emb = NewsEmbedding()
syntax_parser = NewsSyntaxParser(emb)

debug = False

def preprocessing(text):
	process_tokens(text)

def process_tokens(text):
	doc = Doc(text)
	doc.segment(segmenter)
	doc.parse_syntax(syntax_parser)
	processed_tokens = []

	for i in range(len(doc.tokens)):
		an = morph.parse(doc.tokens[i].text)
		doc.tokens[i].text = an[0].normalized.word
		processed_tokens.append(doc.tokens[i].text)
	
	if debug:
		print(doc.tokens)
		doc.sents[0].syntax.print()

	return ' '.join(processed_tokens)