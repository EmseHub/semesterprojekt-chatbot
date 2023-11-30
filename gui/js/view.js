import { arrStudents, arrCourses } from './data-service.js';
import { getResponse } from '../chatbot-logic/logic.js';
import { recognizeTextFromSpeech, speakUtteranceFromText, stopTextFromSpeechRecognition, cancelSpeechFromTextUtterances } from './speech-service.js';

var stateIsSpeechMode = false;


//#region --------------------------- Start ---------------------------
$(document).ready(function () {
    updateStudentCards(arrStudents, arrCourses);
    document.getElementById('container-spinner').style.display = 'none';
    document.getElementById('container-main').style.display = 'block';

    document.getElementById('input-message').focus();

    const arrWelcomeMsgs = [
        'So, dann setze mich mal auf...',
        'Ihr denkt, ich bin ein alter Hut,<br>mein Aussehen ist auch gar nicht gut.<br>Dafür bin ich der schlauste aller Hüte,<br>und ist\'s nicht wahr, so fress ich mich, du meine Güte!',
        'Alle Zylinder und schicken Kappen<br>sind gegen mich doch nur Jammerlappen!',
        'Ich weiß in Hogwarts am besten Bescheid<br>und bin für jeden Schädel bereit.',
        'Nun los, so setzt mich auf, nur Mut,<br>habt nur Vertrauen zum Sprechenden Hut!'
    ]
    appendMessageSystem(getRandomItemInArray(arrWelcomeMsgs));
});
//#endregion


//#region --------------------------- Event Handlers ---------------------------
export function handleSendMessage() {
    const elemInputMessage = document.getElementById('input-message');
    const strMessage = elemInputMessage.value;
    if (!strMessage || !strMessage.trim()) { return; }

    setTimeout(() => {
        appendMessageUser(strMessage);
        elemInputMessage.value = '';
    }, 0);

    setTimeout(() => {
        const [strResponse, objDiagnostic, isDataChanged] = getResponse(strMessage);
        appendMessageSystem(strResponse);
        updateDiagnostic(objDiagnostic);

        if (isDataChanged) { updateStudentCards(arrStudents, arrCourses); }
    }, getRandomInt(1000, 2000));
}

export function toggleSpeechMode() {
    stateIsSpeechMode = !stateIsSpeechMode;
    document.getElementById('img-mic').src = (stateIsSpeechMode) ? './img/mic_off.png' : './img/mic_on.png';
    document.getElementById('btn-speech').classList.toggle('btn-activated');
    loopAudioConversation(0);

    function loopAudioConversation(countNoInputResult) {
        if (!stateIsSpeechMode) {
            stopTextFromSpeechRecognition();
            cancelSpeechFromTextUtterances();
            return;
        }
        recognizeTextFromSpeech((cbStrMessage) => {
            if (cbStrMessage === undefined || cbStrMessage === null) {
                if (stateIsSpeechMode) { toggleSpeechMode(); }
                return;
            }
            if (cbStrMessage.trim() === '') {
                if (!stateIsSpeechMode) { return; }
                if (countNoInputResult < 1 || countNoInputResult > 3) {
                    toggleSpeechMode();
                    return;
                }
                const strResponseToSpeak = getRandomItemInArray([
                    'Bist Du noch da?',
                    'Hallo?',
                    'Ich höre Dich nicht mehr...',
                    'Noch da?',
                    'Kannst Du mich hören?',
                    'Hat es Dir die Sprache verschlagen?',
                    'Eingeschlafen?',
                    'Bist Du AFK?',
                    'Warum sagst Du nichts?'
                ]);
                appendMessageSystem(strResponseToSpeak);
                speakUtteranceFromText(strResponseToSpeak, (cbEndedSuccessfully) => {
                    countNoInputResult++;
                    (cbEndedSuccessfully) ? loopAudioConversation(countNoInputResult) : toggleSpeechMode();
                });
                return;
            }

            appendMessageUser(cbStrMessage);
            const [strResponse, objDiagnostic, isDataChanged] = getResponse(cbStrMessage);

            setTimeout(() => {
                appendMessageSystem(strResponse);
                updateDiagnostic(objDiagnostic);
                if (isDataChanged) { updateStudentCards(arrStudents, arrCourses); }
                if (stateIsSpeechMode) {
                    speakUtteranceFromText(strResponse, (cbEndedSuccessfully) => {
                        (cbEndedSuccessfully) ? loopAudioConversation(1) : toggleSpeechMode();
                    });
                }
            }, getRandomInt(1000, 2000));
        })
    }
}
//#endregion


//#region --------------------------- Manipulate DOM ---------------------------
function appendMessage(strMessage, intMessageType) { // 0 = System, 1 = User
    if (!strMessage) { return; }
    if (!(intMessageType === 0 || intMessageType === 1)) { return; }

    const htmlMessage = ''
        + '<div class="chat-row-message">'
        + '  <div class="chat-message chat-message-' + ((intMessageType === 0) ? 'system' : 'user') + '">' + strMessage + '</div>'
        + '</div>'
        ;
    $('#container-messages').append(htmlMessage);
    window.scrollTo(0, document.body.scrollHeight);
}
function appendMessageSystem(strMessage) { appendMessage(strMessage, 0); }
function appendMessageUser(strMessage) { appendMessage(strMessage, 1); }


function updateStudentCards(arrStudents, arrCourses) {
    if (!arrStudents || !arrCourses) { return; }

    let htmlStudents = '';

    arrStudents.forEach(objStudent => {
        const fullname = objStudent.vorname + ' ' + objStudent.nachname;
        const address = objStudent.adresse.strasse + ' ' + objStudent.adresse.hausnr + ', ' + objStudent.adresse.plz + ' ' + objStudent.adresse.stadt;
        const arrPassedExams = objStudent.pruefungen.filter(p => p.note !== null);
        const gradeAverage = (arrPassedExams.length === 0)
            ? 'Keine bestandenen Prüfungen'
            : ((arrPassedExams.reduce(((accumulator, curVal) => roundTwoDecimals(accumulator + curVal.note)), 0)) / arrPassedExams.length).toFixed(2);

        htmlStudents += ''
            + '<div class="row">'
            + ' <div class="card student-card">'
            + '  <div class="row g-1">'
            + '   <div class="col-md-auto">'
            + '    <div class="px-2 pt-4">'
            + '     <img src="./img/' + objStudent.profilbild + '" class="img-fluid rounded-start student-img" alt="' + fullname + '">'
            + '    </div>'
            + '   </div>'
            + '   <div class="col-md">'
            + '    <div class="card-body py-4">'
            + '     <h6 class="card-title student-title">' + fullname + '</h6>'
            + '     <table class="table student-table">'
            + '      <tr>'
            + '       <th scope="row">Matrikelnummer</th>'
            + '       <td>' + objStudent.matnr + '</td>'
            + '      </tr>'
            + '      <tr class="border-0">'
            + '       <th scope="row">Adresse</th>'
            + '       <td>' + address + '</td>'
            + '      </tr>'

            + '      <tr class="border-0">'
            + '       <th class="table-divider" colspan="2">Prüfungen</th>'
            + '      </tr>'
            ;
        objStudent.pruefungen.forEach((objPruefung, index) => {
            const objKurs = arrCourses.find(c => c.id === objPruefung.kursID);
            const strStatus = ((objPruefung.note !== null)
                ? objPruefung.note.toFixed(1)
                : ((objPruefung.isAngemeldet) ? 'Angemeldet' : 'Nicht angemeldet'));
            htmlStudents += ''
                + '    <tr' + ((index + 1 === objStudent.pruefungen.length) ? ' class="border-0"' : '') + '>'
                + '     <th scope="row">' + objKurs?.name + '</th>'
                + '     <td>' + strStatus + '</td>'
                + '    </tr>'
                ;
        });
        htmlStudents += ''

            + '    <tr class="border-0">'
            + '     <th class="table-divider" scope="row">Durchschnitt</th>'
            + '     <td class="table-divider">' + gradeAverage + '</td>'
            + '    </tr>'
            + '    <tr>'
            + '     <td class="student-update" colspan="2">Letzte Aktualisierung ' + getGerDateStrWithTimeFromDateObj(objStudent.letztesUpdate) + '</td>'
            + '    </tr>'
            + '     </table>'
            + '    </div>'
            + '   </div>'
            + '  </div>'
            + ' </div>'
            + '</div>'
            ;
    });

    $('#container-students').html(htmlStudents);
}

function updateDiagnostic(objDiagnostic) {
    if (!objDiagnostic) { return; }
    const strScore = (objDiagnostic.intent)
        ? `${(objDiagnostic.intent.hitCount || 0) + ' von ' + objDiagnostic.intent.patterns.length}`
        : '-';
    const htmlDiagnostic = ''
        + '<b>Task</b>: ' + (objDiagnostic.intent?.task || '-') + ', '
        + '<b>Korrigiert</b>: ' + (objDiagnostic.spellChecked?.join(' ') || '-') + ', '
        + '<b>Lemmatisiert</b>: ' + (objDiagnostic.lemmatized?.join(' ') || '-') + ', '
        + '<b>Bereinigt</b>: ' + (objDiagnostic.processed?.join(' ') || '-') + ', '
        + '<b>Intent</b>: ' + (objDiagnostic.intent?.tag || '-') + ', '
        + '<b>Score</b>: ' + strScore
        ;
    // const htmlDiagnostic = ''
    //     + '<table>'
    //     + '    <tr>'
    //     + '        <td>Task: ' + (objDiagnostic.intent?.task || '-') + '</td>'
    //     + '        <td>Input: ' + objDiagnostic.intent?.task + '</td>'
    //     + '        <td>Korrigiert: ' + objDiagnostic.spellChecked?.join(' ') + '</td>'
    //     + '        <td>Lemmatisiert: ' + objDiagnostic.lemmatized?.join(' ') + '</td>'
    //     + '        <td>Intent: ' + objDiagnostic.intent?.tag + '</td>'
    //     + '        <td>Score: ' + strScore + '</td>'
    //     + '    </tr>'
    //     + '</table>'
    //     ;
    $('#container-diagnostic').html('<span>' + htmlDiagnostic + '</span>');
}
//#endregion


//#region --------------------------- Helpers ---------------------------
function getGerDateStrWithTimeFromDateObj(objDate) {
    if (!objDate || isNaN(objDate.getTime())) { return ''; }
    const options = {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    };
    return objDate.toLocaleString('de-DE', options); // '07.10.2023, 07:09:04'
}

function roundTwoDecimals(nr) {
    return Math.round((nr + Number.EPSILON) * 100) / 100;
    return Math.round((nr * 100) * (1 + Number.EPSILON)) / 100;
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min) + min); // inklusive min, exklusive max
}

function getRandomItemInArray(arr) {
    return (arr instanceof Array) ? arr[Math.floor(Math.random() * arr.length)] : null;
}
//#endregion