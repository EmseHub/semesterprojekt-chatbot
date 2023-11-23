import { arrCourses } from '/js/data.js';
import { arrStudents } from '/js/data.js';
import arrIntents from '/nlp/intents.json' assert { type: 'json' };

// console.log(arrIntents);
// console.log(arrStopwords);

import { replaceDiacritics, getCleanWords } from '/js/string-editing.js';


var objRunningTask = null;

export function getReply(strMessage) { 

    // 1. Rechtschreibprüfung/Autokorrektur
    // 2. Tokenization (Wörter und Satzzeichen)
    // 3. Stop Words Removal (halt, so, ziemlich etc.) --> https://github.com/stopwords-iso/stopwords-de
    // 4. Part-Of-Speech-Tagging (Nomen, Verben, Adjektive, Adverben etc.)
    // 5. Named Entity Recognition (Orte, Personen, Kurse)
    // 6. Lemmatization (Zurückführung auf Infinitive etc.), dann Stemming (Abschneiden von Endungen/Suffixen)
    // 7. Intent zuordnen (inkl. Ersetzung von Umlauten)
    // 8. Aufgabe abarbeiten

    if (!strMessage || !strMessage.trim()) { return ['Die Empfangene Nachricht konnte leider nicht verarbeitet werden.', null]; }
    const [arrWords, objDiagnostic] = getCleanWords(strMessage);

    const objIntent = getIntent(arrWords);
    console.log('---Gefundener Intent---', objIntent, `\n${objIntent?.hitCount || 0 + ' von ' + arrWords.length + ' Treffern'}`);
    objDiagnostic.intent = objIntent;


    if (objRunningTask || objIntent?.task) {

        if (!objRunningTask) {
            objRunningTask = { name: objIntent.task, params: {} };
        }

        const taskName = objRunningTask.name;
        let strReplyTask = 'Für diese Aufgabe ist leider noch kein Ablauf definiert...';

        if (taskName === 'pruefung_anmelden') { strReplyTask = runTaskPruefungAnmelden(strMessage, arrWords); }

        // TO DO 

        return [strReplyTask, objDiagnostic];
    }

    if (objIntent) {
        return [getRandomItem(objIntent.responses), objDiagnostic];
    }


    const strReply = getRandomItem(
        [
            'Tut mir leid, ich verstehe die Anfrage nicht. Könntest Du sie umformulieren?',
            'Mit dieser Nachricht kann ich leider nichts anfangen.',
            'Check ich nicht.',
            'Könntest Du die Aussage konkretisieren?'
        ]
    );
    return [strReply, objDiagnostic];
}

function runTaskPruefungAnmelden(strMessageOrg, arrWordsCleaned) {
    if (!strMessageOrg || !strMessageOrg.trim()) { return null; }
    const strMessageOrgClean = replaceDiacritics(strMessageOrg.toLowerCase());

    // Prüfen, ob Originalnachricht bereits den Namen der Prüfung enthält
    if (!objRunningTask.params.course) {
        objRunningTask.params.course = arrCourses.find(c => strMessageOrgClean.indexOf(replaceDiacritics(c.name.toLowerCase())) !== -1);
        if (!objRunningTask.params.course) {
            return 'Wie lautet der Name des Kurses genau?';
        }
    }

    // Prüfen, ob in Originalnachricht/bereinigten Wörtern ein Ausdruck für Matrikelnummer sowie die Nr. selbst enthalten ist 
    if (!objRunningTask.params.student) {
        if (!objRunningTask.params.course) {
            const hasWord4MatNr = ['matrikelnummer', 'matrikelnr', 'matrnr', 'matrnummer', 'matnummer', 'matnr'].some(word4mat => (
                strMessageOrgClean.replaceAll('-', '').indexOf(word4mat) !== -1)
                || arrWordsCleaned.some(word => replaceDiacritics(word.replaceAll('-', '').toLowerCase()) === word4mat)
            );
            if (!hasWord4MatNr) {
                return 'Wie lautet Deine Matrikelnummer? Wenn Du das Wort "Matrikelnummer" oder "MatNr" davor schreibt, erkenne ich sie besser.';
            }
        }


        const strNumbersInMessage = strMessageOrg.replace(/\D+/g, ' ').replace(/\s+/g, ' ').trim();
        const arrNumbersInMessage = (strNumbersInMessage) ? strNumbersInMessage.split(' ') : null;
        if (!arrNumbersInMessage) {
            return 'Dann bräuchte ich noch Deine Matrikelnummer.';
        }


        objRunningTask.params.student = arrStudents.find(s => arrNumbersInMessage.indexOf(s.matnr.toString()) !== -1);
        if (!objRunningTask.params.student) {
            return 'Die angegebene Matrikelnummer konnte nicht gefunden werden. Bitte korrigieren.';
        }
    }


    if(!objRunningTask.isConfirmed) {
        // intent prüfen 
    }




    if (objRunningTask.params.course && objRunningTask.params.student && !objRunningTask.isConfirmed) {
        return `Möchtest Du, ${objRunningTask.params.student.vorname}, die Prüfung im Fach "${objRunningTask.params.course.name}" bei ${objRunningTask.params.course.lehrperson} verbindlich anmelden?`;
    }

    if (objRunningTask.params.course && objRunningTask.params.student && !objRunningTask.isConfirmed) {
        return 'Die Prüfung wurde erfolgreich angemeldet.';
        // TO DO --> task zurücksetzen
        // TO DO --> Daten update
    }

    console.log('KEIN ERGEBNIS', objRunningTask);
    return null;
}





function getIntent(arrWords) {
    if (!arrWords || arrWords.length === 0) { return null; }

    const arrWordsClean = arrWords.map(w => replaceDiacritics(w.toLowerCase()));
    const totalWords = arrWordsClean.length;
    const arrPossibleIntents = [];

    for (let i = 0; i < arrIntents.length; i++) {
        const objIntent = arrIntents[i];
        let hitCount = 0;
        for (let y = 0; y < objIntent.patterns.length; y++) {
            const strPattern = objIntent.patterns[y];
            if (arrWordsClean.indexOf(strPattern) !== -1) { hitCount++; }
        }
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
    return arrPossibleIntents.reduce((best, current) => (best && best.hitCount > current.hitCount) ? best : current);

    // if (!strOptimizedMessage || !strOptimizedMessage.trim()) { return null; }
    // strOptimizedMessage = strOptimizedMessage.toLowerCase();
    // const arrPossibleIntents = [];
    // arrIntents.forEach(objIntent => {
    //     let score = 0;
    //     objIntent.patterns.forEach(expression => {
    //         if (strOptimizedMessage.indexOf(expression) > -1) { score++; }
    //     });

    //     if (score > 0) {
    //         arrPossibleIntents.push({ ...objIntent, score });
    //         console.log(arrPossibleIntents);
    //     }
    // });

    // if (arrPossibleIntents.length === 0) { return null; }
    // return arrPossibleIntents.reduce((best, current) => (best && best.score > current.score) ? best : current);
}


function getRandomItem(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}



//#region --------------------------- TO DO ---------------------------

//#endregion


// ---- PATTERNS IN LOWER CASE UMWANDELN ----
// for (let i = 0; i < arrIntents.length; i++) {
//     for (let y = 0; y < arrIntents[i].patterns.length; y++) {
//         arrIntents[i].patterns[y] = arrIntents[i].patterns[y].toLowerCase();
//     }
// }
// console.log(arrIntents);