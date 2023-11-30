import spellCheckIgnore from './nlp-json/spell-check-ignore.json' assert { type: 'json' };
import stopwords from './nlp-json/stopwords.json' assert { type: 'json' };
import lemmaMapping from './nlp-json/IWNLP.Lemmatizer_20181001.min.json' assert { type: 'json' };

import intents from './nlp-json/intents.json' assert { type: 'json' };

import postalCodes from './nlp-json/postal-codes.json' assert { type: 'json' };



// --- BESSER ABER WEGEN PROMISES NICHT VERWENDET ---
// fetch('/chatbot-logic/nlp-json/spell-check-ignore.json')
//     .then(response => response.json())
//     .then(json => console.log(json));


export const arrSpellCheckIgnore = spellCheckIgnore;
export const arrStopwords = stopwords;
export const arrLemmaMapping = lemmaMapping;
export const arrIntents = intents;
export const arrPostalCodes = postalCodes;