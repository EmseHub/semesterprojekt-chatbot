import { arrCourses } from '/js/data.js';
import { arrStudents } from '/js/data.js';

import { getReply } from '/js/chatbot-logic.js';



//#region --------------------------- Start ---------------------------
$(document).ready(function () {
    // Daten visualisieren
    updateStudentCards(arrStudents, arrCourses);
    document.getElementById('container-spinner').style.display = 'none';
    document.getElementById('container-main').style.display = 'block';


    document.getElementById('input-message').focus();

    appendMessageSystem('Hallo, was kann ich für Dich tun?');
});
//#endregion


//#region --------------------------- Event Handlers ---------------------------
export function handleSendMessage() {
    const elemInputMessage = document.getElementById('input-message');
    const strMessage = elemInputMessage.value;
    if (!strMessage || !strMessage.trim()) { return; }
    appendMessageUser(strMessage);
    elemInputMessage.value = '';


    const [strReply, objDiagnostic] = getReply(strMessage);
    appendMessageSystem(strReply);
    console.log(objDiagnostic);
    updateDiagnostic(objDiagnostic);

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
            + ' <div class="card student-card" style="max-width: 540px;">'
            + '  <div class="row g-1">'
            + '   <div class="col-md-auto">'
            + '    <div class="px-2 py-4">'
            + '     <img src="/img/' + objStudent.profilbild + '" class="img-fluid rounded-start student-img" alt="' + fullname + '">'
            + '    </div>'
            + '   </div>'
            + '   <div class="col-md">'
            + '    <div class="card-body py-4">'
            + '     <h6 class="card-title student-title">' + fullname + '</h6>'
            + '     <table class="table student-table">'
            + '      <tbody>'
            + '       <tr>'
            + '        <th scope="row">Adresse</th>'
            + '        <td>' + address + '</td>'
            + '       </tr>'
            ;
        objStudent.pruefungen.forEach(objPruefung => {
            const objKurs = arrCourses.find(c => c.id === objPruefung.kursID);
            const strStatus = ((objPruefung.note !== null)
                ? objPruefung.note.toFixed(1)
                : ((objPruefung.isAngemeldet) ? 'Angemeldet' : 'Nicht angemeldet'));
            htmlStudents += ''
                + '   <tr>'
                + '    <th scope="row">' + objKurs?.name + '</th>'
                + '    <td>' + strStatus + '</td>'
                + '   </tr>'
                ;
        });
        htmlStudents += ''
            + '      </tbody>'
            + '     </table>'
            + '     <p class="card-text">Notendurchschnitt: ' + gradeAverage + '</p>'
            + '     <p class="card-text"><small class="text-body-secondary student-small">Letzte Aktualisierung: ' + getGerDateStrWithTimeFromDateObj(objStudent.letztesUpdate) + '</small></p>'
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
        + '<b>Bereinigt</b>: ' + (objDiagnostic.cleaned?.join(' ') || '-') + ', '
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
//#endregion





// arrStudents[0].pruefungen[1].note = 1.9;
// arrStudents[0].letztesUpdate = new Date();
// updateStudentCards(arrStudents, arrCourses);