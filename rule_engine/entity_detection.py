import re

from rule_engine.data_service import students, courses
from rule_engine.helpers import get_random_item_in_list, replace_diacritics

# Hinweis: Parameter "message_processed" bedeutet, dass Umlaute ersetzt wurden und Text in Lower Case ist

test_a = [
    {'original': 'Das', 'korrigiert': 'Das', 'lemma': 'der', 'pos': 'PDS'},
    {'original': 'ist', 'korrigiert': 'ist',
        'lemma': 'sein', 'pos': 'VA(FIN)'},
    {'original': 'eine', 'korrigiert': 'eine', 'lemma': 'ein', 'pos': 'ART'},
    {'original': 'Beispiel-Nachricht', 'korrigiert': 'Beispiel-Nachricht',
        'lemma': 'Beispiel-nachricht', 'pos': 'NN'},
    {'original': 'Aber', 'korrigiert': 'Aber', 'lemma': 'aber', 'pos': 'ADV'},
    {'original': 'mit', 'korrigiert': 'mit', 'lemma': 'mit', 'pos': 'APPR'},
    {'original': 'Fehlren', 'korrigiert': 'Fehlern', 'lemma': 'Fehler', 'pos': 'NN'},
    {'original': 'und', 'korrigiert': 'und', 'lemma': 'und', 'pos': 'KON'},
    {'original': 'Leerzeichen', 'korrigiert': 'Leerzeichen',
        'lemma': 'Leerzeichen', 'pos': 'NN'},
    {'original': 'Sie', 'korrigiert': 'Sie', 'lemma': 'sie', 'pos': 'PPER'},
    {'original': 'wurde', 'korrigiert': 'wurde',
        'lemma': 'werden', 'pos': 'VA(FIN)'},
    {'original': 'z.B.', 'korrigiert': 'z.B.', 'lemma': 'Z.b.', 'pos': 'NE'},
    {'original': 'verfasst', 'korrigiert': 'verfasst',
        'lemma': 'verfasst', 'pos': 'ADJ(D)'},
    {'original': 'von', 'korrigiert': 'von', 'lemma': 'von', 'pos': 'APPR'},
    {'original': 'Dr.', 'korrigiert': 'Dr.', 'lemma': 'Dr.', 'pos': 'NN'},
    {'original': 'House', 'korrigiert': 'Hose', 'lemma': 'Hose', 'pos': 'NN'},
    {'original': 'und', 'korrigiert': 'und', 'lemma': 'und', 'pos': 'KON'},
    {'original': 'Mr', 'korrigiert': 'Mr', 'lemma': 'mr', 'pos': 'XY'},
    {'original': 'während', 'korrigiert': 'während',
        'lemma': 'während', 'pos': 'APPR'},
    {'original': 'der', 'korrigiert': 'der', 'lemma': 'der', 'pos': 'ART'},
    {'original': 'Hg.', 'korrigiert': 'Hg.', 'lemma': 'Hg.', 'pos': 'NE'},
    {'original': 'Homer', 'korrigiert': 'Homer', 'lemma': 'Homer', 'pos': 'NE'},
    {'original': 'ist', 'korrigiert': 'ist', 'lemma': 'sein', 'pos': 'VA(FIN)'}
]


def detect_student_in_message(message_processed):
    result = {"student": None, "query": ""}
    if not message_processed or not message_processed.strip():
        return result
    # Prüfen, ob Nachricht Nummern enthält
    min_length_matnr = 6
    numbers_in_message = re.findall(r'\d+', message_processed)
    if not numbers_in_message or not any(len(nr) >= min_length_matnr for nr in numbers_in_message):
        result["query"] = get_random_item_in_list([
            "Ich bräuchte noch Deine Matrikelnummer.",
            "Verrätst Du mir noch Deine Matrikelnummer?"
        ])
        return result
    # Prüfen, ob Nummern im Text bekannten Matrikelnummern entsprechen
    matching_students = [
        student for student in students if (student["matnr"] in numbers_in_message)
    ]
    # Prüfen, ob ein oder mehrere Students gefunden wurden
    if not matching_students:
        result["query"] = "Die angegebene Zahl stimmt mit keiner Matrikelnummer überein. Gib bitte Deine vollständige Matrikelnummer an."
        return result
    # Prüfen, ob mehrere Students gefunden wurden
    if len(matching_students) > 1:
        result["query"] = f"Welche der {len(
            matching_students)} angegebenen Matrikelnummern gehört zu Dir? Gib sie bitte erneut an."
        return result
    # Student eindeutig ermittelt
    result["student"] = matching_students[0]
    return result


def detect_course_in_message(message_processed):
    result = {"course": None, "query": ""}
    if not message_processed or not message_processed.strip():
        return result
    # Prüfen, ob die Nachricht den Namen des Kurses enthält
    matching_courses = [
        course for course in courses if replace_diacritics(course["name"].lower()) in message_processed
    ]
    # Prüfen, ob ein oder mehrere Kurse gefunden wurden
    if not matching_courses:
        result["query"] = get_random_item_in_list([
            "Wie lautet der Name des Kurses genau?",
            "Wie ist die genaue Bezeichnung des Kurses?"
        ])
        return result
    # Richtigen Treffer auswählen (Wenn Eingabe "Mathe Teil 2" ist, gibt es Treffer bei den Kursen "Mathe Teil 2" und "Mathe" --> Korrekt ist immer der Kurs mit dem längsten Namen)
    result["course"] = max(
        matching_courses, key=lambda course: len(course["name"])
    )
    return result


def detect_address_in_message(detected_arguments, message_raw):
    if not detected_arguments or not message_raw or not message_raw.strip():
        return {'objDetectedData': {'objStudent': None, 'objAddress': None}, 'strQuery': None}

    tmp_detected_arguments = detected_arguments.copy()
    strQuery = ''

    # Prüfen, ob Matrikelnummer bereits angegeben und einem Student-Objekt zugeordnet wurde
    if not tmp_detected_arguments['objStudent']:
        strMessageProcessed = replace_diacritics(message_raw.lower())
        objStudent, strQueryStudent = getStudentFromMessage(
            strMessageProcessed)
        tmp_detected_arguments['objStudent'] = objStudent
        strQuery = strQueryStudent

    # Prüfen, ob Adresse vollständig angegeben wurde
    arrAddressKeys = ['strasse', 'hausnr', 'stadt', 'plz']
    if not tmp_detected_arguments['objAddress'] or any(not tmp_detected_arguments['objAddress'][key] for key in arrAddressKeys):
        objAddress = tmp_detected_arguments['objAddress'].copy(
        ) if tmp_detected_arguments['objAddress'] else {'staat': 'Deutschland'}

        # Prüfen, ob zuvor bereits Adress-Daten übermittelt worden sind
        if not any(objAddress[key] for key in arrAddressKeys):
            strMessageProcessed = message_raw.replace(
                ',', ' ').replace('\s+', ' ').strip()
            regexFullAddress = re.compile(
                r'\b([a-zäöüß]{2,}(-?))*(\.?)\s+\d{1,4}([a-z]*)\s+\d{5}\s+([a-zäöüß]{2,}(-)?)*[a-zäöüß]{2,}(?![a-z0-9äöüß-])', re.IGNORECASE)

            arrFullAddress = regexFullAddress.findall(strMessageProcessed)
            if arrFullAddress and len(arrFullAddress) != 0:
                splitFullAddress = arrFullAddress[0].split(' ')
                if len(splitFullAddress) > 3:
                    objAddress['strasse'] = splitFullAddress[0]
                    objAddress['hausnr'] = splitFullAddress[1]
                    objAddress['plz'] = splitFullAddress[2]
                    objAddress['stadt'] = splitFullAddress[3]

        # Prüfen, ob Adresse oder Hausnummer fehlt und in aktueller Nachricht enthalten ist
        if not objAddress['strasse'] or not objAddress['hausnr']:
            def getStrasseAndHausnr(strGivenStrasse, strGivenHausnr, strMessageRaw):
                regexStrasseAndHausnr = re.compile(
                    r'\b([a-zäöüß]{2,}(-?))+(\s+)?(str(\.?)|straße|strasse)\s+\d{1,4}([a-z]*)\b', re.IGNORECASE)
                regexStrasse = re.compile(
                    r'\b([a-zäöüß]{2,}(-?))+(\s+)?(str(\.?)|straße|strasse)(?![a-z0-9äöüß-])', re.IGNORECASE)
                regexDescrAndHausnr = re.compile(
                    r'\b(hausnummer|hausnr(\.?))\s+\d{1,4}([a-z]*)\b', re.IGNORECASE)
                regexHausnr = re.compile(r'\b\d{1,4}[a-z]*\b', re.IGNORECASE)
                regexWordAndHausnr = re.compile(
                    r'\b([a-zäöüß]{2,}(-?))+\s+\d{1,4}([a-z]*)\b', re.IGNORECASE)

                strStrasse = strGivenStrasse
                strHausnr = strGivenHausnr

                if not strStrasse and not strHausnr:
                    arrStrasseAndHausnr = regexStrasseAndHausnr.findall(
                        strMessageRaw)
                    if arrStrasseAndHausnr and len(arrStrasseAndHausnr) != 0:
                        splitStrasseAndHausnr = arrStrasseAndHausnr[0].split(
                            ' ')
                        if len(splitStrasseAndHausnr) > 1:
                            return {'strStrasse': splitStrasseAndHausnr[0], 'strHausnr': splitStrasseAndHausnr[1]}

                if not strStrasse:
                    arrStrasse = regexStrasse.findall(strMessageRaw)
                    if arrStrasse and len(arrStrasse) != 0:
                        strStrasse = arrStrasse[0]

                if not strHausnr:
                    arrDescrAndHausnr = regexDescrAndHausnr.findall(
                        strMessageRaw)
                    if arrDescrAndHausnr and len(arrDescrAndHausnr) != 0:
                        splitDescrAndHausnr = arrDescrAndHausnr[0].split(' ')
                        if len(splitDescrAndHausnr) > 1:
                            strHausnr = splitDescrAndHausnr[1]

                if strStrasse and strHausnr:
                    return {'strStrasse': strStrasse, 'strHausnr': strHausnr}

                if strStrasse:
                    arrHausnr = regexHausnr.findall(strMessageRaw)
                    if arrHausnr and len(arrHausnr) != 0:
                        hausnrMatch = next(
                            (hnr for hnr in arrHausnr if len(hnr) < 5), None)
                        if hausnrMatch:
                            strHausnr = hausnrMatch
                            return {'strStrasse': strStrasse, 'strHausnr': strHausnr}

                arrWordAndHausnr = regexWordAndHausnr.findall(strMessageRaw)
                if arrWordAndHausnr and len(arrWordAndHausnr) != 0:
                    splitWordAndHausnr = arrWordAndHausnr[0].split(' ')
                    if len(splitWordAndHausnr) > 1:
                        strStrasse = splitWordAndHausnr[0]
                        strHausnr = splitWordAndHausnr[1]

                return {'strStrasse': strStrasse, 'strHausnr': strHausnr}

            result = getStrasseAndHausnr(
                objAddress['strasse'], objAddress['hausnr'], message_raw)
            objAddress['strasse'] = result['strStrasse']
            objAddress['hausnr'] = result['strHausnr']

        if not objAddress['plz'] or not objAddress['stadt']:
            def getStrassePlzAndStadt(strGivenPlz, strGivenStadt, strMessageRaw):
                regexPlzAndStadt = re.compile(
                    r'\b\d{5}(\,?)\s+([a-zäöüß]{2,}(-)?)*[a-zäöüß]{2,}(?![a-z0-9äöüß-])', re.IGNORECASE)
                regexPlz = re.compile(
                    r'\b\d{5}(?![a-z0-9äöüß-])', re.IGNORECASE)

                strPlz = strGivenPlz
                strStadt = strGivenStadt
                strMessageProcessed = strMessageRaw.replace(
                    ',', ' ').replace('\s+', ' ')

                if not strStadt and not strPlz:
                    arrPlzAndStadt = regexPlzAndStadt.findall(
                        strMessageProcessed)
                    if arrPlzAndStadt and len(arrPlzAndStadt) != 0:
                        splitPlzAndStadt = arrPlzAndStadt[0].split(' ')
                        if len(splitPlzAndStadt) > 1:
                            return {'strPlz': splitPlzAndStadt[0], 'strStadt': splitPlzAndStadt[1]}

                if not strPlz:
                    arrPlz = regexPlz.findall(strMessageProcessed)
                    if arrPlz and len(arrPlz) != 0:
                        strPlz = arrPlz[0]

                if not strStadt and strPlz:
                    splitMessage = strMessageProcessed.split(' ')
                    indexOfPlz = splitMessage.index(strPlz)
                    if indexOfPlz != -1 and len(splitMessage) > (indexOfPlz + 1):
                        strNextWord = splitMessage[indexOfPlz + 1]
                        strNextWord = replace_diacritics(strNextWord.lower())
                        objPostalCode = next((pc for pc in arrPostalCodes if replace_diacritics(
                            pc['city'].lower()) == strNextWord), None)
                        if objPostalCode:
                            strStadt = objPostalCode['city']
                            return {'strPlz': strPlz, 'strStadt': strStadt}

                        objPostalCode = next(
                            (pc for pc in arrPostalCodes if pc['zipcode'] == strPlz), None)
                        if objPostalCode:
                            strStadt = objPostalCode['city']
                            return {'strPlz': strPlz, 'strStadt': strStadt}

                return {'strPlz': strPlz, 'strStadt': strStadt}

            result = getStrassePlzAndStadt(
                objAddress['plz'], objAddress['stadt'], message_raw)
            objAddress['plz'] = result['strPlz']
            objAddress['stadt'] = result['strStadt']

        tmp_detected_arguments['objAddress'] = objAddress

    if not any(tmp_detected_arguments['objAddress'][key] for key in arrAddressKeys):
        if tmp_detected_arguments['objStudent']:
            strQuery += f" Okay {tmp_detected_arguments['objStudent']['vorname'].split(' ')[
                0]}, danke."
        strQuery += " Gib Deine neue Adresse gerne im folgenden Format an: Winkelgasse 93, 12345 Zauberstadt"
    else:
        if not tmp_detected_arguments['objAddress']['strasse'] and not tmp_detected_arguments['objAddress']['hausnr']:
            strQuery += " Ich benötige noch den Straßennamen und die Hausnummer."
        elif not tmp_detected_arguments['objAddress']['strasse']:
            strQuery += " Es fehlt noch der Straßenname."
        elif not tmp_detected_arguments['objAddress']['hausnr']:
            strQuery += " Es fehlt noch die Hausnummer."

        if not tmp_detected_arguments['objAddress']['plz'] and not tmp_detected_arguments['objAddress']['stadt']:
            strQuery += " Verrätst Du mir auch die PLZ und den Ort, in dem zukünftig residieren wirst?"
        elif not tmp_detected_arguments['objAddress']['plz']:
            strQuery += " Jetzt fehlt mir nur noch die PLZ Deiner neuen Anschrift."
        elif not tmp_detected_arguments['objAddress']['stadt']:
            strQuery += " Jetzt fehlt mir nur noch der Name des Ortes."

    strQuery = strQuery.strip()
    return {'objDetectedData': tmp_detected_arguments, 'strQuery': strQuery}


student_test_result = detect_student_in_message("1234567 1122334")
print("---student_test_result---")
print(student_test_result)

course_test_result = detect_course_in_message("muggelkunde")
print("---course_test_result---")
print(course_test_result)
