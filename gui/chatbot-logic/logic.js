import { arrIntents } from './nlp-data-service.js';
import { replaceDiacritics, getProcessedWords } from './string-editing.js';
import tasks from './tasks.js';

var stateObjRunningTask = null;

export function getResponse(strMessage) {

    // 1. Rechtschreibprüfung/Autokorrektur
    // 2. Tokenization (Wörter und Satzzeichen)
    // 3. Stop Words Removal (halt, so, ziemlich etc.) --> https://github.com/stopwords-iso/stopwords-de
    // 4. Part-Of-Speech-Tagging (Nomen, Verben, Adjektive, Adverben etc.)
    // 5. Named Entity Recognition (Orte, Personen, Kurse)
    // 6. Lemmatization (Zurückführung auf Infinitive etc.), dann Stemming (Abschneiden von Endungen/Suffixen)
    // 7. Intent zuordnen (inkl. Ersetzung von Umlauten)
    // 8. Task abarbeiten

    if (!strMessage || !strMessage.trim()) { return ['Die Empfangene Nachricht konnte leider nicht verarbeitet werden.', null, false]; }
    strMessage = strMessage.trim().replace(/\s+/g, ' '); // Jeden Whitespace (Space/Tab/Newline) beliebiger Länge reduzieren auf ein Leerzeichen (' ')

    let strResponse = '';
    const [arrWords, objDiagnostic] = getProcessedWords(strMessage);
    let isDataChanged = false;

    const objIntent = getIntent(arrWords);
    console.log('---Gefundener Intent---', objIntent, `\n\n${(objIntent?.hitCount || 0) + ' von ' + arrWords.length + ' Wörtern treffen'}`);
    objDiagnostic.intent = objIntent;

    if (stateObjRunningTask || objIntent?.task) {
        if (!stateObjRunningTask) {
            stateObjRunningTask = { name: objIntent.task, params: {} };
        }
        const strRunningTaskName = stateObjRunningTask.name;
        strResponse = `Für die Aufgabe "${strRunningTaskName}" ist leider noch kein Ablauf definiert...`;
        const strIntentTag = objIntent?.tag;

        [stateObjRunningTask, strResponse, isDataChanged] = (function () {
            switch (strRunningTaskName) {
                case 'adresse_aendern': return tasks.processTaskAdresseAendern(stateObjRunningTask, strMessage, strIntentTag);
                case 'pruefung_anmelden': return tasks.processTaskPruefungAnmelden(stateObjRunningTask, strMessage, strIntentTag);
                case 'pruefung_abmelden': return tasks.processTaskPruefungAbmelden(stateObjRunningTask, strMessage, strIntentTag);
                case 'pruefung_status': return tasks.processTaskPruefungStatus(stateObjRunningTask, strMessage, strIntentTag);
            }
            return [null, strResponse, isDataChanged];
        })();

        // Task abgeschlossen oder -brochen --> Anschlussfrage ergänzen 
        if (!stateObjRunningTask) {
            strResponse += ' ' + getRandomItemInArray([
                'Kann ich sonst noch etwas für Dich tun?',
                'Darf es sonst noch etwas sein?',
                'Hast Du weitere Anliegen?'
            ]);
        }
    }
    else {
        strResponse = getRandomItemInArray(objIntent?.responses || arrIntents.find(i => i.tag === 'trefferlos').responses);
    }
    
    objDiagnostic.runningTask = stateObjRunningTask;
    return [strResponse, objDiagnostic, isDataChanged];
}

function getIntent(arrWords) {
    if (!arrWords || arrWords.length === 0) { return null; }

    const arrWordsNoDiacritics = arrWords.map(w => replaceDiacritics(w.toLowerCase()));
    const totalWords = arrWordsNoDiacritics.length;
    const arrPossibleIntents = [];

    for (let i = 0; i < arrIntents.length; i++) {
        const objIntent = arrIntents[i];
        let hitCount = 0;
        for (let y = 0; y < objIntent.patterns.length; y++) {
            const strPattern = objIntent.patterns[y];
            if (arrWordsNoDiacritics.indexOf(strPattern) !== -1) { hitCount++; }
        }
        if (hitCount < objIntent.minHits) { continue; }
        // const score = Math.round(((hitCount / totalWords) + Number.EPSILON) * 100) / 100;
        if (hitCount >= totalWords) {
            return { ...objIntent, hitCount };
        }
        if (hitCount > 0) {
            arrPossibleIntents.push({ ...objIntent, hitCount });
        }
    }
    if (arrPossibleIntents.length === 0) { return null; }
    console.log('Mögliche Intents', arrPossibleIntents);
    return arrPossibleIntents.reduce((bestObj, curObj) => (bestObj.hitCount >= curObj.hitCount) ? bestObj : curObj);
}


export function getRandomItemInArray(arr) {
    return (arr instanceof Array) ? arr[Math.floor(Math.random() * arr.length)] : null;
}