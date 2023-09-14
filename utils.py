import nltk
import re

def remove_space_before_punctuation(sentence):
    pattern = r'\s+([^\w\s]+)'  

    updated_sentence = re.sub(pattern, r'\1', sentence)
    return updated_sentence

def capitalize_paragraph(paragraph):
    pattern = r"(^|[.!?]\s+)(\w)"

    capitalized_paragraph = re.sub(pattern, lambda m: m.group(1) + m.group(2).upper(), paragraph)
    return capitalized_paragraph

def capitalize_sentence(sentence):
    words = nltk.word_tokenize(sentence)
    tagged_words = nltk.pos_tag(words)

    excluded_tags = ['IN', 'PRP', 'DT', 'CC', 'TO', 'VB', 'VBP', 'VBZ']  # Add any POS tags you want to exclude from capitalization

    capitalized_words = []
    for word, tag in tagged_words:
        if tag not in excluded_tags:
            capitalized_words.append(word[0].upper() + word[1:])
        else:
            capitalized_words.append(word)

    updated_sentence = remove_space_before_punctuation(' '.join(capitalized_words))

    return capitalize_paragraph(updated_sentence)
