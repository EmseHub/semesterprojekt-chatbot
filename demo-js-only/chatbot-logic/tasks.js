import { arrStudents, arrCourses } from '../js/data-service.js';

import { arrPostalCodes } from './nlp-data-service.js';
import { replaceDiacritics } from './string-editing.js';
import { getRandomItemInArray } from './logic.js';


//#region --------------------------- Daten ermitteln ---------------------------
function getStudentFromMessage(strMessageProcessed) {
    const objResult = { objStudent: null, strQuery: '' };
    if (!strMessageProcessed || !strMessageProcessed.trim()) { return objResult; }
    // Prüfen, ob Nachricht Nummern enthält
    const minLengthMatNr = 6;
    const arrNumbersInMessage = strMessageProcessed.match(/\d+/g);
    if (!arrNumbersInMessage || !arrNumbersInMessage.some(nr => nr.length >= minLengthMatNr)) {
        objResult.strQuery = getRandomItemInArray(['Ich bräuchte noch Deine Matrikelnummer.', 'Verrätst Du mir noch Deine Matrikelnummer?',]);
        return objResult;
    }
    // Prüfen, ob Nummern im Text bekannten Matrikelnummern entsprechen
    const arrMatchingStudents = arrStudents.filter(s => arrNumbersInMessage.indexOf(s.matnr) !== -1);
    if (arrMatchingStudents.length === 0) {
        objResult.strQuery = 'Die angegebene Zahl stimmt mit keiner Matrikelnummer überein. Gib bitte Deine vollständige Matrikelnummer an.';
        return objResult;
    }
    if (arrMatchingStudents.length > 1) {
        objResult.strQuery = 'Welche der angegebenen Matrikelnummern gehört zu Dir? Gib sie bitte erneut an.';
        return objResult;
    }
    // Student eindeutig ermittelt
    objResult.objStudent = arrMatchingStudents[0];
    return objResult;
}

function getCourseFromMessage(strMessageProcessed) {
    const objResult = { objCourse: null, strQuery: '' };
    if (!strMessageProcessed || !strMessageProcessed.trim()) { return objResult; }
    // Prüfen, ob Nachricht den Namen der Prüfung enthält
    const arrMatchingCourses = arrCourses.filter(c => strMessageProcessed.indexOf(replaceDiacritics(c.name.toLowerCase())) !== -1);
    if (arrMatchingCourses.length === 0) {
        objResult.strQuery = getRandomItemInArray(['Wie lautet der Name des Kurses genau?', 'Wie ist die genaue Bezeichnung des Kurses?']);
        return objResult;
    }
    // Richtigen Treffer auswählen (Wenn Eingabe "Mathe Teil 2" ist, gibt es Treffer bei den Kursen "Mathe Teil 2" und "Mathe" --> Korrekt ist immer der Kurs mit dem längsten Namen)
    objResult.objCourse = arrMatchingCourses.reduce((bestObj, curObj) => (bestObj.name.length >= curObj.name.length) ? bestObj : curObj);
    return objResult;
}

function getMissingStudentOrAddressFromMessage(objGivenData, strMessageRaw) {
    if (!objGivenData || !strMessageRaw || !strMessageRaw.trim()) { return { objDetectedData: { objStudent: null, objAddress: null }, strQuery: null }; }
    const objDetectedData = { ...objGivenData };
    let strQuery = '';

    // Prüfen, ob Matrikelnummer bereits angegeben und einem Student-Objekt zugeordnet wurde
    if (!objDetectedData.objStudent) {
        const strMessageProcessed = replaceDiacritics(strMessageRaw.toLowerCase());
        // ({ objStudent: objDetectedData.objStudent, strQuery: strQuery } = getStudentFromMessage(strMessageProcessed));
        const { objStudent, strQuery: strQueryStudent } = getStudentFromMessage(strMessageProcessed);
        objDetectedData.objStudent = objStudent;
        strQuery = strQueryStudent;
        // Damit etwaige Zahlenfolge der Matrikelnummer nicht irrtümlich für Hausnummer oder PLZ gehalten wird, Matrikelnummer aus Message entfernen
        // if (objStudent) { strMessageRaw = strMessageRaw.replace(objStudent.matnr, ''); }
    }

    // Prüfen, ob Adresse vollständig angegeben wurde
    const arrAddressKeys = ['strasse', 'hausnr', 'stadt', 'plz']; // Staat außen vor da erstmal nur Deutschland
    if (!objDetectedData.objAddress || arrAddressKeys.some(key => !objDetectedData.objAddress[key])) {

        const objAddress = (objDetectedData.objAddress) ? { ...objDetectedData.objAddress } : { staat: 'Deutschland' };

        // Prüfen, ob zuvor bereits Adress-Daten übermittelt worden sind
        if (!arrAddressKeys.some(key => objAddress[key])) {
            const strMessageProcessed = strMessageRaw.replaceAll(',', ' ').replace(/\s+in\s+/gi, ' ').replace(/\s+/g, ' ');
            // const regexFullAddress = /\b([a-zäöüß]{2,}(-?))*(\.?)\s+\d{1,4}([a-z]*)\s+\d{5}\s+([a-zäöüß]{2,}(-)?)*[a-zäöüß]{2,}(?![a-z0-9äöüß-])/gi;
            const regexFullAddress = /\b((([a-zäöüß]{2,}(-?))+(\s+)?(str(\.?)|straße|strasse|weg))|([a-zäöüß]{2,}(-?))*)\s+\d{1,4}([a-z]*)\s+\d{5}\s+([a-zäöüß]{2,}(-)?)*[a-zäöüß]{2,}(?![a-z0-9äöüß-])/gi;

            const arrFullAddress = strMessageProcessed.match(regexFullAddress);
            if (arrFullAddress && arrFullAddress.length !== 0) {
                // const splitFullAddress = arrFullAddress[0].split(' '); // Blastr. 8 50737 Köln oder Bla-Bla Straße 8 50737 Köln

                const strFullAddress = arrFullAddress[0]; // Blastr. 8 50737 Köln oder Bla-Bla Straße 8 50737 Köln
                const arrFullAddressSplittedByFirstNumber = strFullAddress.split(/(\d+.*)/); // Aufteilen in [0] für Straße und [1] für Rest --> [ "Bla-Bla Straße ", "8 50737 Köln", "" ]

                const strSplitPartA = arrFullAddressSplittedByFirstNumber[0].trim(); // "Bla-Bla Straße"
                const strSplitPartB = arrFullAddressSplittedByFirstNumber[1].trim(); // "8 50737 Köln"

                const arrSplitPartB = strSplitPartB.split(' ');

                if (arrSplitPartB.length > 2) {
                    objAddress.strasse = strSplitPartA;
                    objAddress.hausnr = arrSplitPartB[0];
                    objAddress.plz = arrSplitPartB[1];
                    objAddress.stadt = arrSplitPartB[2];
                }
            }
        }
        // Prüfen, ob Adresse oder Hausnummer fehlt und in aktueller Nachricht enthalten ist
        if (!objAddress.strasse || !objAddress.hausnr) { // TO DO
            const getStrasseAndHausnr = (strGivenStrasse, strGivenHausnr, strMessageRaw) => {
                // Wort(-Wort-) && WS? && str/str./straße/strasse && WS && Nr+
                // const regexStrasseAndHausnr = /\b([a-zäöüß]{2,}(-?))+(\s+)?(str(\.?)|straße|strasse|weg)\s+\d{1,4}([a-z]*)\b/gi;
                const regexStrasseAndHausnr = /\b((([a-zäöüß]{2,}(-?))+(\s+)?(str(\.?)|straße|strasse|weg))|([a-zäöüß]{2,}(-?))*)\s+\d{1,4}([a-z]*)\b/gi;
                // Wort(-Wort-) && WS? && str/str./straße/strasse am Ende
                const regexStrasse = /\b([a-zäöüß]{2,}(-?))+(\s+)?(str(\.?)|straße|strasse|weg)(?![a-z0-9äöüß-])/gi;
                // (hausnummer || hausnr) && WS && Zahl+
                // const regexDescrAndHausnr = /\b(hausnummer|hausnr(\.?))\s+\d{1,4}([a-z]*)\b/gi;
                // (hausnummer || nummer || hausnr || nr) && WS && Zahl+                
                const regexDescrAndHausnr = /\b(hausnummer|nummer|hausnr(\.?)|nr(\.?))(\s+(lautet|ist(\s+die)?))*\s+\d{1,4}([a-z]*)\b/gi;
                // (hausnummer || hausnr) && WS && Zahl+
                const regexHausnr = /\b\d{1,4}[a-z]*\b/gi;
                // Wort(-Wort-) && WS && Nr+
                const regexWordAndHausnr = /\b([a-zäöüß]{2,}(-?))+\s+\d{1,4}([a-z]*)\b/gi;

                let strStrasse = strGivenStrasse;
                let strHausnr = strGivenHausnr;

                // [Straße Hausnummer] prüfen
                if (!strStrasse && !strHausnr) {
                    const arrStrasseAndHausnr = strMessageRaw.match(regexStrasseAndHausnr);
                    if (arrStrasseAndHausnr && arrStrasseAndHausnr.length !== 0) {
                        // const splitStrasseAndHausnr = arrStrasseAndHausnr[0].split(' ');
                        const strStrasseAndHausnr = arrStrasseAndHausnr[0]; // Blastr. 8 oder Bla-Bla Straße 8
                        const arrStrasseAndHausnrSplittedByFirstNumber = strStrasseAndHausnr.split(/(\d+.*)/); // Aufteilen in [0] für Straße und [1] für Rest --> [ "Bla-Bla Straße ", "8", "" ]

                        const strSplitPartA = arrStrasseAndHausnrSplittedByFirstNumber[0].trim(); // "Bla-Bla Straße"
                        const strSplitPartB = arrStrasseAndHausnrSplittedByFirstNumber[1].trim(); // "8"

                        if (arrStrasseAndHausnrSplittedByFirstNumber.length > 1) {
                            return { strStrasse: strSplitPartA, strHausnr: strSplitPartB };
                        }
                    }
                }
                // [Straße] prüfen
                if (!strStrasse) {
                    const arrStrasse = strMessageRaw.match(regexStrasse);
                    if (arrStrasse && arrStrasse.length !== 0) { strStrasse = arrStrasse[0]; }
                }
                // [Hausnummer] prüfen
                if (!strHausnr) {
                    const arrDescrAndHausnr = strMessageRaw.match(regexDescrAndHausnr);
                    if (arrDescrAndHausnr && arrDescrAndHausnr.length !== 0) {
                        const splitDescrAndHausnr = arrDescrAndHausnr[0].trim().split(' '); // String ist etwa 'Hausnummer 3a'
                        if (splitDescrAndHausnr.length > 1) { strHausnr = splitDescrAndHausnr[splitDescrAndHausnr.length - 1]; }
                    }
                }
                // Prüfen, ob Straße und Hausnummer mittlerweile gefunden
                if (strStrasse && strHausnr) { return { strStrasse, strHausnr }; }
                // [Straße] gefunden, [Hausnummer] prüfen
                if (strStrasse) {
                    const arrHausnr = strMessageRaw.match(regexHausnr);
                    if (arrHausnr && arrHausnr.length !== 0) {
                        const hausnrMatch = arrHausnr.find(hnr => hnr.length < 5);
                        if (hausnrMatch) {
                            strHausnr = hausnrMatch;
                            return { strStrasse, strHausnr };
                        }
                    }
                }
                // [Irgendwas Hausnummer] prüfen
                const arrWordAndHausnr = strMessageRaw.match(regexWordAndHausnr);
                if (arrWordAndHausnr && arrWordAndHausnr.length !== 0) {
                    const splitWordAndHausnr = arrWordAndHausnr[0].split(' '); // String ist etwa 'Blabla 15a'
                    if (splitWordAndHausnr.length > 1) {
                        strStrasse = splitWordAndHausnr[0];
                        strHausnr = splitWordAndHausnr[1];
                    }
                }
                return { strStrasse, strHausnr };
            }
            const { strStrasse, strHausnr } = getStrasseAndHausnr(objAddress.strasse, objAddress.hausnr, strMessageRaw);
            objAddress.strasse = strStrasse;
            objAddress.hausnr = strHausnr;
        }
        // Prüfen, ob PLZ oder Stadt fehlt und in aktueller Nachricht enthalten ist
        if (!objAddress.plz || !objAddress.stadt) {
            const getStrassePlzAndStadt = (strGivenPlz, strGivenStadt, strMessageRaw) => {
                // PLZ{5} && WP && Stadt(-Stadt)
                const regexPlzAndStadt = /\b\d{5}(\,?)\s+([a-zäöüß]{2,}(-)?)*[a-zäöüß]{2,}(?![a-z0-9äöüß-])/gi;
                // PLZ{5} && !Wort/Zahl
                const regexPlz = /\b\d{5}(?![a-z0-9äöüß-])/gi;

                let strPlz = strGivenPlz;
                let strStadt = strGivenStadt;
                const strMessageProcessed = strMessageRaw.replaceAll(',', ' ').replace(/\s+/g, ' ');

                // [PLZ Stadt] prüfen
                if (!strStadt && !strPlz) {
                    const arrPlzAndStadt = strMessageProcessed.match(regexPlzAndStadt);
                    if (arrPlzAndStadt && arrPlzAndStadt.length !== 0) {
                        const splitPlzAndStadt = arrPlzAndStadt[0].split(' '); // 50737 Köln
                        if (splitPlzAndStadt.length > 1) {
                            return { strPlz: splitPlzAndStadt[0], strStadt: splitPlzAndStadt[1] };
                        }
                    }
                }
                // [PLZ] prüfen
                if (!strPlz) {
                    const arrPlz = strMessageProcessed.match(regexPlz);
                    if (arrPlz && arrPlz.length !== 0) { strPlz = arrPlz[0]; }
                }
                // [Stadt] prüfen
                if (!strStadt) {
                    if (strPlz) {
                        // Prüfen, ob Wort hinter der PLZ der Postal-Codes-DB bekannt ist
                        const splitMessage = strMessageProcessed.split(' ');
                        const indexOfPlz = splitMessage.indexOf(strPlz);
                        if (indexOfPlz !== -1 && splitMessage.length > (indexOfPlz + 1)) {
                            let strNextWord = splitMessage[indexOfPlz + 1];
                            strNextWord = replaceDiacritics(strNextWord.toLowerCase())
                            const objPostalCode = arrPostalCodes.find(pc => replaceDiacritics(pc.city.toLowerCase()) === strNextWord);
                            if (objPostalCode) {
                                strStadt = objPostalCode.city;
                                return { strPlz, strStadt };
                            }
                        }
                        // Stadt via PLZ aus Postal-Codes-DB auslesen 
                        const objPostalCode = arrPostalCodes.find(pc => pc.zipcode === strPlz);
                        if (objPostalCode) {
                            strStadt = objPostalCode.city;
                            return { strPlz, strStadt };
                        }
                    }
                }
                return { strPlz, strStadt };
            }
            const { strPlz, strStadt } = getStrassePlzAndStadt(objAddress.pls, objAddress.stadt, strMessageRaw);
            objAddress.plz = strPlz;
            objAddress.stadt = strStadt;
        }

        objDetectedData.objAddress = objAddress;
    }

    if (!arrAddressKeys.some(key => objDetectedData.objAddress[key])) {
        if (objDetectedData.objStudent) { strQuery += ' ' + `Okay ${objDetectedData.objStudent.vorname.split(' ')[0]}, danke.`; }
        strQuery += ' ' + 'Gib Deine neue Adresse gerne im folgenden Format an: Winkelgasse 93, 12345 Zauberstadt';
    }
    else {
        if (!objDetectedData.objAddress.strasse && !objDetectedData.objAddress.hausnr) { strQuery += ' ' + 'Ich benötige noch den Straßennamen und die Hausnummer.'; }
        else if (!objDetectedData.objAddress.strasse) { strQuery += ' ' + 'Es fehlt noch der Straßenname.'; }
        else if (!objDetectedData.objAddress.hausnr) { strQuery += ' ' + 'Es fehlt noch die Hausnummer.'; }

        if (!objDetectedData.objAddress.plz && !objDetectedData.objAddress.stadt) { strQuery += ' ' + 'Verrätst Du mir auch die PLZ und den Ort, in dem zukünftig residieren wirst?'; }
        else if (!objDetectedData.objAddress.plz) { strQuery += ' ' + 'Jetzt fehlt mir nur noch die PLZ Deiner neuen Anschrift.'; }
        else if (!objDetectedData.objAddress.plz) { strQuery += ' ' + 'Jetzt fehlt mir nur noch der Name des Ortes.'; }
    }
    strQuery = strQuery.trim();
    return { objDetectedData, strQuery };
}

function getMissingStudentOrCourseFromMessage(objGivenData, strMessageRaw) {
    if (!objGivenData || !strMessageRaw || !strMessageRaw.trim()) { return { objStudent: null, objCourse: null, strQuery: null }; }

    let strMessageProcessed = replaceDiacritics(strMessageRaw.toLowerCase());
    const objResult = { ...objGivenData, strQuery: '' };
    // Prüfen, ob Kurs bereits angegeben und zugeordnet wurde 
    if (!objResult.objCourse) {
        // Prüfen, ob Nachricht den Namen der Prüfung enthält --> Wenn nicht, Rückfrage anhängen
        const { objCourse, strQuery } = getCourseFromMessage(strMessageProcessed);
        if (objCourse) {
            objResult.objCourse = objCourse;
            // Damit etwaige Zahlenfolge im Kursnamen nicht irrtümlich für Matrikelnummer gehalten wird, Kursnamen aus Message entfernen
            // strMessageProcessed = strMessageProcessed.replace(replaceDiacritics(objCourse.name.toLowerCase()), '');
        }
        else { objResult.strQuery = strQuery; }
    }
    // Prüfen, ob Matrikelnummer bereits angegeben und einem Student-Objekt zugeordnet wurde
    if (!objResult.objStudent) {
        // Prüfen, ob Nachricht die Matrikelnummer enthält --> Wenn nicht, Rückfrage anhängen
        const { objStudent, strQuery } = getStudentFromMessage(strMessageProcessed);
        if (objStudent) { objResult.objStudent = objStudent; }
        else { objResult.strQuery = (objResult.strQuery + ' ' + strQuery).trim(); }
    }
    return objResult;
}

function getReferencedPruefungFromMessage(objGivenData, strMessageRaw) {
    let objPruefung = null;
    if (!objGivenData || !strMessageRaw || !strMessageRaw.trim()) { return [objPruefung, objGivenData, null]; }
    // Prüfen, welche Angaben noch fehlen und ob sie in der aktuellen Nachricht enthalten sind    
    const { objStudent, objCourse, strQuery } = getMissingStudentOrCourseFromMessage(objGivenData, strMessageRaw);
    const objUpdatedData = { objStudent, objCourse };
    // Falls, alle notwendigen Daten vorhanden sind, Kurs in den dem User zugeordneten Prüfungen finden (wenn nicht, wird Rückfrage weitergeben)
    if (objStudent && objCourse) { objPruefung = objStudent.pruefungen.find(p => p.kursID === objCourse.id); }
    return [objPruefung, objUpdatedData, strQuery];
}
//#endregion


//#region --------------------------- Task-Funtkionen ---------------------------
function processTaskAdresseAendern(objTaskState, strMessageRaw, strIntentTag) {
    let isDataChanged = false;
    if (strIntentTag === 'ablehnung') { return [null, 'Ich breche die Adressänderung ab.', isDataChanged]; }
    if (!objTaskState || !strMessageRaw || !strMessageRaw.trim()) { return [objTaskState, null, isDataChanged]; }
    // Daten in Nachricht erkennen
    const { objDetectedData, strQuery } = getMissingStudentOrAddressFromMessage({ ...objTaskState.params }, strMessageRaw);
    objTaskState.params = objDetectedData;
    // Prüfen, ob alle Daten vorliegen
    const arrAddressKeys = ['strasse', 'hausnr', 'stadt', 'plz']; // Staat außen vor da erstmal nur Deutschland
    if (!objDetectedData.objStudent || !objDetectedData.objAddress || arrAddressKeys.some(key => !objDetectedData.objAddress[key])) {
        return [objTaskState, strQuery, isDataChanged];
    }
    // Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if (strIntentTag !== 'zustimmung') {
        const strResponse = `Nun denn, ${objDetectedData.objStudent.vorname.split(' ')[0]}, ich ändere Deine Adresse zu "${''
            + objDetectedData.objAddress.strasse + ' '
            + objDetectedData.objAddress.hausnr + ', '
            + objDetectedData.objAddress.plz + ' '
            + objDetectedData.objAddress.stadt
            }", okay?`;
        return [objTaskState, strResponse, isDataChanged];
    }
    // Vorgang bestätigt --> Daten ändern und Running Task zurücksetzen
    const objStudentLive = arrStudents.find(s => s.matnr === objDetectedData.objStudent.matnr);
    objStudentLive.adresse = { ...objDetectedData.objAddress };
    objStudentLive.letztesUpdate = new Date();
    isDataChanged = true;
    return [null, 'Vielen Dank, die Adresse wurde geändert.', isDataChanged];
}

function processTaskPruefungAnmelden(objTaskState, strMessageRaw, strIntentTag) {
    let isDataChanged = false;
    if (strIntentTag === 'ablehnung') { return [null, 'Ich breche die Prüfungsanmeldung ab.', isDataChanged]; }
    if (!objTaskState || !strMessageRaw || !strMessageRaw.trim()) { return [objTaskState, null, isDataChanged]; }
    // Prüfen, ob Anhand der Nachricht und ggf. bisheriger Angaben die referenzierte Prüfung ermittelt werden kann
    const [objExistingPruefung, objTaskStateParams, strQuery] = getReferencedPruefungFromMessage({ ...objTaskState.params }, strMessageRaw);
    objTaskState.params = objTaskStateParams;
    const { objStudent, objCourse } = objTaskStateParams;
    // Prüfen, ob die notwendigen Daten zu User und Kurs vorliegen
    if (!objStudent || !objCourse) {
        return [objTaskState, strQuery, isDataChanged];
    }
    // Prüfen, ob Kurs dem User bereits zugeordnet ist, und wenn ja, ob die Prüfung noch nicht bestanden und nocht nicht angemeldet ist
    if (objExistingPruefung) {
        if (objExistingPruefung.note !== null) {
            const strResponse = `${objStudent.vorname.split(' ')[0]}, Du hast die Prüfung im Fach "${objCourse.name}" bereits mit der Note ${objExistingPruefung.note.toFixed(1)} bestanden.`;
            return [null, strResponse, isDataChanged];
        }
        if (objExistingPruefung.isAngemeldet) {
            const strResponse = `${objStudent.vorname.split(' ')[0]}, die Prüfung im Fach "${objCourse.name}" ist bereits angemeldet.`;
            return [null, strResponse, isDataChanged];
        }
    }
    // Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if (strIntentTag !== 'zustimmung') {
        const strResponse = `Okay ${objStudent.vorname.split(' ')[0]}, möchtest Du die Prüfung im Fach "${objCourse.name}" bei ${objCourse.lehrperson} verbindlich anmelden?`;
        return [objTaskState, strResponse, isDataChanged];
    }
    // Vorgang bestätigt --> Daten ändern und Running Task zurücksetzen
    const objStudentLive = arrStudents.find(s => s.matnr === objStudent.matnr);
    if (objExistingPruefung) {
        objStudentLive.pruefungen.find(p => p.kursID === objCourse.id).isAngemeldet = true;
    }
    else {
        const objNewPruefung = { "kursID": objCourse.id, "isAngemeldet": true, "note": null };
        objStudentLive.pruefungen.push(objNewPruefung);
    }
    objStudentLive.letztesUpdate = new Date();
    isDataChanged = true;
    return [null, 'Die Prüfung wurde erfolgreich angemeldet.', isDataChanged];
}

function processTaskPruefungAbmelden(objTaskState, strMessageRaw, strIntentTag) {
    let isDataChanged = false;
    if (strIntentTag === 'ablehnung') { return [null, 'Ich stoppe die Abmeldung der Prüfung.', isDataChanged]; }
    if (!objTaskState || !strMessageRaw || !strMessageRaw.trim()) { return [objTaskState, null, isDataChanged]; }
    // Prüfen, ob Anhand der Nachricht und ggf. bisheriger Angaben die referenzierte Prüfung ermittelt werden kann
    const [objExistingPruefung, objTaskStateParams, strQuery] = getReferencedPruefungFromMessage({ ...objTaskState.params }, strMessageRaw);
    objTaskState.params = objTaskStateParams;
    const { objStudent, objCourse } = objTaskStateParams;
    // Prüfen, ob die notwendigen Daten zu User und Kurs vorliegen
    if (!objStudent || !objCourse) {
        return [objTaskState, strQuery, isDataChanged];
    }
    // Prüfen, ob der Kurs dem User zugeordnet und die Prüfung angemeldet ist
    if (!objExistingPruefung || !objExistingPruefung.isAngemeldet) {
        const strResponse = `${objStudent.vorname.split(' ')[0]}, Du kannst die Prüfung im Fach "${objCourse.name}" nicht abmelden, da Du gar nicht angemeldet bist.`;
        return [null, strResponse, isDataChanged];
    }
    // Prüfen, ob der Kurs noch nicht bestanden ist
    if (objExistingPruefung.note !== null) {
        const strResponse = `${objStudent.vorname.split(' ')[0]}, Du kannst die Prüfung im Fach "${objCourse.name}" nicht abmelden, da Du sie bereits mit der Note ${objExistingPruefung.note.toFixed(1)} bestanden hast.`;
        return [null, strResponse, isDataChanged];
    }
    // Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if (strIntentTag !== 'zustimmung') {
        const strResponse = `Okay ${objStudent.vorname.split(' ')[0]}, möchtest Du die Prüfung im Fach "${objCourse.name}" bei ${objCourse.lehrperson} wirklich abmelden?`;
        return [objTaskState, strResponse, isDataChanged];
    }
    // Vorgang bestätigt --> Daten ändern und Running Task zurücksetzen
    const objStudentLive = arrStudents.find(s => s.matnr === objStudent.matnr);
    objStudentLive.pruefungen.find(p => p.kursID === objCourse.id).isAngemeldet = false;
    objStudentLive.letztesUpdate = new Date();
    isDataChanged = true;
    return [null, 'Die Prüfung wurde erfolgreich abgemeldet.', isDataChanged];
}

function processTaskPruefungStatus(objTaskState, strMessageRaw, strIntentTag) {
    const isDataChanged = false;
    if (strIntentTag === 'ablehnung') { return [null, 'Ich stoppe die Statusabfrage der Prüfung.', isDataChanged]; }
    if (!objTaskState || !strMessageRaw || !strMessageRaw.trim()) { return [objTaskState, null, isDataChanged]; }
    // Prüfen, ob Anhand der Nachricht und ggf. bisheriger Angaben die referenzierte Prüfung ermittelt werden kann
    const [objExistingPruefung, objTaskStateParams, strQuery] = getReferencedPruefungFromMessage({ ...objTaskState.params }, strMessageRaw);
    objTaskState.params = objTaskStateParams;
    const { objStudent, objCourse } = objTaskStateParams;
    // Prüfen, ob die notwendigen Daten zu User und Kurs vorliegen
    if (!objStudent || !objCourse) { return [objTaskState, strQuery, isDataChanged]; }
    // Annahme, dass der Kurs angemeldet ist
    let strResponse = `${objStudent.vorname.split(' ')[0]}, die Prüfung im Fach "${objCourse.name}" ist angemeldet und noch nicht bestanden.`;
    // Prüfen, ob der Kurs wirklich dem User zugeordnet und die Prüfung angemeldet ist
    if (!objExistingPruefung || !objExistingPruefung.isAngemeldet) {
        strResponse = `${objStudent.vorname.split(' ')[0]}, die Prüfung im Fach "${objCourse.name}" ist weder angemeldet noch bestanden.`;
    }
    // Prüfen, ob der Kurs bestanden ist
    else if (objExistingPruefung.note !== null) {
        strResponse = `Glückwunsch ${objStudent.vorname.split(' ')[0]}, Du hast die Prüfung im Fach "${objCourse.name}" mit der Note ${objExistingPruefung.note.toFixed(1)} bestanden.`;
    }
    return [null, strResponse, isDataChanged];
}
//#endregion

export default {
    processTaskAdresseAendern,
    processTaskPruefungAnmelden,
    processTaskPruefungAbmelden,
    processTaskPruefungStatus,
};