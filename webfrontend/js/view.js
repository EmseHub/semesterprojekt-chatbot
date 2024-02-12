var arrStudents, arrCourses = []
import { recognizeTextFromSpeech, speakUtteranceFromText, stopTextFromSpeechRecognition, cancelSpeechFromTextUtterances } from '/webfrontend/js/speech-service.js';

var stateIsSpeechMode = false;

//#region --------------------------- Start ---------------------------
$(document).ready(function () {

    fetch("/start", {
        method: "POST",
        body: JSON.stringify({
            message: "",
        }),
        headers: { "Content-type": "application/json; charset=UTF-8" },
    })
        .then((response) => response.json())
        .then((json) => {
            arrStudents = json.data_students;
            arrStudents = arrStudents.map(objStudent => ({ ...objStudent, letztesUpdate: new Date(objStudent.letztesUpdate) }));
            arrCourses = json.data_courses;

            init_page();

        });
});

function init_page(params) {
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
}


//#region --------------------------- Server Communication ---------------------------

function getResponse(strMessage, callback) {

    if (!strMessage) { callback([null, null, false]); return; }

    fetch("/response", {
        method: "POST",
        body: JSON.stringify({
            message: strMessage,
        }),
        headers: { "Content-type": "application/json; charset=UTF-8" },
    })
        .then((response) => response.json())
        .then((json) => {
            // console.log(json);

            // reply = {
            //     "request": "Start",
            //     "response": "",
            //     "diagnostic": {},
            //     "is_data_changed": True,
            //     "data_students": students,
            //     "data_courses": courses
            // }
            const strResponse = json.response;
            const objDiagnostic = json.diagnostic;
            const isDataChanged = json.is_data_changed;

            if (isDataChanged) {
                arrStudents = json.data_students;
                arrStudents = arrStudents.map(objStudent => ({ ...objStudent, letztesUpdate: new Date(objStudent.letztesUpdate) }));
                arrCourses = json.data_courses;
            }

            callback([strResponse, objDiagnostic, isDataChanged]);
        });
}

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
        getResponse(strMessage, (callbackValue) => {
            const [strResponse, objDiagnostic, isDataChanged] = callbackValue;

            appendMessageSystem(strResponse);
            updateDiagnostic(objDiagnostic);

            if (isDataChanged) { updateStudentCards(arrStudents, arrCourses); }
        });
    }, getRandomInt(1000, 2000));
}

export function toggleSpeechMode() {
    stateIsSpeechMode = !stateIsSpeechMode;
    const elemImgMic = document.getElementById('img-mic');
    document.getElementById('btn-speech').classList.toggle('btn-activated');
    loopAudioConversation(null, 0);

    function loopAudioConversation(objDiagnostic, countNoInputResult) {
        if (!stateIsSpeechMode) {
            // elemImgMic.src = 'webfrontend/img/mic_on.png';
            stopTextFromSpeechRecognition();
            cancelSpeechFromTextUtterances();
            return;
        }
        elemImgMic.src = 'webfrontend/img/mic_on.png';
        recognizeTextFromSpeech((cbStrMessage) => {
            if (cbStrMessage === undefined || cbStrMessage === null) {
                if (stateIsSpeechMode) { toggleSpeechMode(); }
                return;
            }
            if (cbStrMessage.trim() === '') {
                countNoInputResult++;
                if (!stateIsSpeechMode) { return; }
                if (!objDiagnostic || !objDiagnostic.runningTask || countNoInputResult > 3) {
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
                setTimeout(() => {
                    appendMessageSystem(strResponseToSpeak);
                    elemImgMic.src = 'webfrontend/img/audio_play.png';
                    speakUtteranceFromText(strResponseToSpeak, (cbEndedSuccessfully) => {
                        (cbEndedSuccessfully) ? loopAudioConversation(objDiagnostic, countNoInputResult) : toggleSpeechMode();
                    });
                }, getRandomInt(1000, 5000));
                return;
            }

            appendMessageUser(cbStrMessage);
            const [strResponse, objDiagnosticNew, isDataChanged] = getResponse(cbStrMessage);

            setTimeout(() => {
                appendMessageSystem(strResponse);
                updateDiagnostic(objDiagnosticNew);
                if (isDataChanged) { updateStudentCards(arrStudents, arrCourses); }
                if (stateIsSpeechMode) {
                    elemImgMic.src = 'webfrontend/img/audio_play.png';
                    speakUtteranceFromText(strResponse, (cbEndedSuccessfully) => {
                        (cbEndedSuccessfully) ? loopAudioConversation(objDiagnosticNew, 0) : toggleSpeechMode();
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
            + '     <img src="webfrontend/img/' + objStudent.profilbild + '" class="img-fluid rounded-start student-img" alt="' + fullname + '">'
            + '    </div>'
            + '   </div>'
            + '   <div class="col-md">'
            + '    <div class="card-body py-4">'
            + '     <h5 class="card-title student-title">' + fullname + '</h5>'
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
            + '       <th class="table-divider" scope="col" colspan="2">Prüfungen</th>'
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

    let strScore = '-';
    if (objDiagnostic.intent) {
        const hitCount = objDiagnostic?.intent?.hit_count || 0;
        const patternsCount = objDiagnostic?.intent?.patterns.length || 0;
        const wordCount = objDiagnostic?.tagged_tokens?.length || 0;
        strScore = `${hitCount}/${wordCount} ${(wordCount === 1) ? 'Wort trifft' : 'Wörter treffen'} (${(hitCount * 100 / wordCount).toFixed(0)}%) bei ${patternsCount} ${(patternsCount === 0) ? 'Pattern' : 'Patterns'}`;
    }

    let htmlTaggedTokens = '';
    if (objDiagnostic?.tagged_tokens) {
        htmlTaggedTokens += '<table>'
            + '  <tr>'
            + '    <th scrope="row">' + 'Original' + '</th>'
            + (objDiagnostic.tagged_tokens.map(t => '<td>' + (t.original || '-') + '</td>')).join('')
            + '  </tr>'
            + '  <tr>'
            + '    <th scrope="row">' + 'Korrigiert' + '</th>'
            + (objDiagnostic.tagged_tokens.map(t => '<td>' + (t.korrigiert || '-') + '</td>')).join('')
            + '  </tr>'
            + '  <tr>'
            + '    <th scrope="row">' + 'Lemmata' + '</th>'
            + (objDiagnostic.tagged_tokens.map(t => '<td>' + (t.lemma || '-') + '</td>')).join('')
            + '  </tr>'
            + '  <tr>'
            + '    <th scrope="row">' + 'PoS-Tags' + '</th>'
            + (objDiagnostic.tagged_tokens.map(t => '<td>' + (t.pos || '-') + '</td>')).join('')
            + '  </tr>'
            + '</table>'
            ;
    }
    const htmlTaskIntentScore = ''
        + '<table>'
        + '  <tr>'
        + '    <th scrope="row">' + 'Akt. Task' + '</th>'
        + '    <td>' + (objDiagnostic.state_running_task?.name || '-') + '</td>'
        + '  </tr>'
        + '  <tr>'
        + '    <th scrope="row">' + 'Intent' + '</th>'
        + '    <td>' + (objDiagnostic.intent?.tag || '-') + '</td>'
        + '  </tr>'
        + '  <tr>'
        + '    <th scrope="row">' + 'Score' + '</th>'
        + '    <td>' + strScore + '</td>'
        + '  </tr>'
        + '</table>'
        ;
    $('#container-diagnostic').html('<span>' + htmlTaggedTokens + htmlTaskIntentScore + '</span>');
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