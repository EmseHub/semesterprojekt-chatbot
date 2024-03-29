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
        strResponse = getRandomItemInArray(objIntent?.responses);
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
    if (arrPossibleIntents.length === 0) {
        // return null; 
        return { ...arrIntents.find(i => i.tag === 'trefferlos'), hitCount: 0 };
    }
    console.log('Mögliche Intents', arrPossibleIntents);
    return arrPossibleIntents.reduce((bestObj, curObj) => (bestObj.hitCount >= curObj.hitCount) ? bestObj : curObj);
}


export function getRandomItemInArray(arr) {
    return (arr instanceof Array) ? arr[Math.floor(Math.random() * arr.length)] : null;
}

// ---- PATTERNS IN LOWER CASE UMWANDELN ----
// for (let i = 0; i < arrIntents.length; i++) {
//     for (let y = 0; y < arrIntents[i].patterns.length; y++) {
//         arrIntents[i].patterns[y] = arrIntents[i].patterns[y].toLowerCase();
//     }
// }
// console.log(arrIntents);


// ---- UMLAUTE AUS ARRAY ENTFERNEN ----
// console.log(arrStopwordsGer.map(x => replaceDiacritics(x)));


// ---- TEST-DOWNLOAD ----
// function downloadJSON() {
//     const blob = new Blob([JSON.stringify(arrLemmaMapping, null, null)], { type: 'application/json' });
//     const url = URL.createObjectURL(blob);
//     const a = document.createElement("a");
//     a.href = url;
//     a.download = 'download.json';

//     a.click();
//     a.remove();
//     URL.revokeObjectURL(url);
// };

// ---- UMLAUTE UND ß BILDEN ----
// function createDiacritics(strText) {
//     if (!strText || !strText.trim()) { return strText; }
//     const diacriticsMap = [
//         { replacement: "Ae", original: "Ä" },
//         { replacement: "Oe", original: "Ö" },
//         { replacement: "Ue", original: "Ü" },
//         { replacement: "ae", original: "ä" },
//         { replacement: "oe", original: "ö" },
//         { replacement: "ue", original: "ü" },
//         { replacement: "ss", original: "ß" },
//     ];
//     for (let i = 0; i < diacriticsMap.length; i++) { strText = strText.replaceAll(diacriticsMap[i].replacement, diacriticsMap[i].original); }
//     return strText;
// }
// function logIntentsWithDiacritics(intents) {
//     for (let i = 0; i < intents.length; i++) {
//         const intent = intents[i];
//         for (let y = 0; y < intent.patterns.length; y++) {
//             intent.patterns[y] = createDiacritics(intent.patterns[y])
//         }
    
//     }
//     // console.log(JSON.stringify(intents, null, 2));
//     console.log(intents);
// }
// logIntentsWithDiacritics(intents)