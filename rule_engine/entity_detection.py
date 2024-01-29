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


def detect_address_in_message(detected_address_temp, message_raw):

    # Falls bisher noch keine Adress-Angaben erkannt worden sind, Adresse als leeres Dictionary initialisieren
    detected_address_new = {
        **detected_address_temp
    } if detected_address_temp else {}

    result = {"address": detected_address_new, "query": ""}

    if not message_raw or not message_raw.strip():
        return result

    # Falls Adresse noch gar nicht definiert ist (auch nicht unvollständig), versuche alle Attribute auf einmal auszulesen
    if (not detected_address_new):
        # Staat der neuen Adresse mit "Deutschland" initialisieren, da der Chatbot andere Staaten erstmal nicht berücksichtigt
        detected_address_new["staat"] = "Deutschland"

        # Kommata durch Leerzeichen ersetzen
        message_processed = message_raw.replace(',', ' ')
        # Alle Varianten von "in" durch Leerzeichen ersetzen
        message_processed = re.sub(
            r"\s+in\s+", " ", message_processed, flags=re.IGNORECASE
        )
        # Jeden White Space auf ein Leerzeichen reduzieren
        message_processed = re.sub(r"\s+", " ", message_processed).strip()

        #
        regex_match = re.match(
            r"\b([a-zäöüß]{2,}(-?))*(\.?)\s+\d{1,4}([a-z]*)\s+\d{5}\s+([a-zäöüß]{2,}(-)?)*[a-zäöüß]{2,}(?![a-z0-9äöüß-])",
            message_processed,
            re.IGNORECASE
        )
        if (regex_match):
            regex_match_string = regex_match.group()
            print("regex_match_string: " + regex_match_string)

            regex_match_splitted = regex_match_string.split()
            if len(regex_match_splitted) > 3:
                detected_address_new['strasse'] = regex_match_splitted[0]
                detected_address_new['hausnr'] = regex_match_splitted[1]
                detected_address_new['plz'] = regex_match_splitted[2]
                detected_address_new['stadt'] = regex_match_splitted[3]

    print("---detected_address_new---")
    print(detected_address_new)

    # Falls Adresse oder Hausnummer fehlt, versuche gezielt diese Attribute auszulesen
    if not detected_address_new.get('strasse') or not detected_address_new.get('hausnr'):

        strasse = detected_address_new.get('strasse')
        hausnr = detected_address_new.get('hausnr')

        # Falls Straße und Hausnummer fehlen, versuche bei auf einmal auszulesen
        if not strasse and not hausnr:
            strasse_and_hausnr = regexStrasseAndHausnr.findall(strMessageRaw)
            if strasse_and_hausnr and len(strasse_and_hausnr) != 0:
                splitStrasseAndHausnr = strasse_and_hausnr[0].split(
                    ' ')
                if len(splitStrasseAndHausnr) > 1:
                    return {'strStrasse': splitStrasseAndHausnr[0], 'strHausnr': splitStrasseAndHausnr[1]}

        # Falls Straße (noch) fehlt, lies diese aus
        if not strasse:
            pass

        # Falls Hausnummer (noch) fehlt, lies diese aus
        if not hausnr:
            pass

        # ALT

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
                strasse_and_hausnr = regexStrasseAndHausnr.findall(
                    strMessageRaw)
                if strasse_and_hausnr and len(strasse_and_hausnr) != 0:
                    splitStrasseAndHausnr = strasse_and_hausnr[0].split(
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
            detected_address_new['strasse'], detected_address_new['hausnr'], message_raw
        )
        detected_address_new['strasse'] = result['strStrasse']
        detected_address_new['hausnr'] = result['strHausnr']

    if not detected_address_new['plz'] or not detected_address_new['stadt']:
        def getStrassePlzAndStadt(strGivenPlz, strGivenStadt, strMessageRaw):
            regexPlzAndStadt = re.compile(
                r'\b\d{5}(\,?)\s+([a-zäöüß]{2,}(-)?)*[a-zäöüß]{2,}(?![a-z0-9äöüß-])', re.IGNORECASE)
            regexPlz = re.compile(
                r'\b\d{5}(?![a-z0-9äöüß-])', re.IGNORECASE)

            strPlz = strGivenPlz
            strStadt = strGivenStadt
            message_processed = strMessageRaw.replace(',', ' ').strip()
            message_processed = re.sub(r"\s+", " ", message_processed)

            if not strStadt and not strPlz:
                arrPlzAndStadt = regexPlzAndStadt.findall(
                    message_processed)
                if arrPlzAndStadt and len(arrPlzAndStadt) != 0:
                    splitPlzAndStadt = arrPlzAndStadt[0].split(' ')
                    if len(splitPlzAndStadt) > 1:
                        return {'strPlz': splitPlzAndStadt[0], 'strStadt': splitPlzAndStadt[1]}

            if not strPlz:
                arrPlz = regexPlz.findall(message_processed)
                if arrPlz and len(arrPlz) != 0:
                    strPlz = arrPlz[0]

            if not strStadt and strPlz:
                splitMessage = message_processed.split(' ')
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
            detected_address_new['plz'], detected_address_new['stadt'], message_raw
        )
        detected_address_new['plz'] = result['strPlz']
        detected_address_new['stadt'] = result['strStadt']

    # Angaben, die eine Adresse aufweisen muss
    address_keys = ['strasse', 'hausnr', 'stadt', 'plz']

    # Prüfen, ob Adresse noch gar nicht oder unvollständig definiert ist
    if not detected_address_new or any(not key in detected_address_new for key in address_keys):
        pass

    if not any(detected_address_new[key] for key in address_keys):
        if detected_address_new['student']:
            query += f" Okay {detected_address_new['student']['vorname'].split(' ')[
                0]}, danke."
        query += " Gib Deine neue Adresse gerne im folgenden Format an: Winkelgasse 93, 12345 Zauberstadt"
    else:
        if not detected_address_new['strasse'] and not detected_address_new['hausnr']:
            query += " Ich benötige noch den Straßennamen und die Hausnummer."
        elif not detected_address_new['strasse']:
            query += " Es fehlt noch der Straßenname."
        elif not detected_address_new['hausnr']:
            query += " Es fehlt noch die Hausnummer."

        if not detected_address_new['plz'] and not detected_address_new['stadt']:
            query += " Verrätst Du mir auch die PLZ und den Ort, in dem zukünftig residieren wirst?"
        elif not detected_address_new['plz']:
            query += " Jetzt fehlt mir nur noch die PLZ Deiner neuen Anschrift."
        elif not detected_address_new['stadt']:
            query += " Jetzt fehlt mir nur noch der Name des Ortes."

    query = query.strip()
    # return result
    return {'address': detected_address_new, 'query': query}


# student_test_result = detect_student_in_message("1234567 1122334")
# print("---student_test_result---")
# print(student_test_result)

# course_test_result = detect_course_in_message("muggelkunde")
# print("---course_test_result---")
# print(course_test_result)


my_dictionary = {"a": 55}
print('my_dictionary.get("a")')
print(my_dictionary.get("a"))
if (my_dictionary.get("a")):
    print('jup')


# address_test_result = detect_address_in_message(
#     {"strasse": None}, "Müllerweg 5 in 41836 Htown"
# )
address_test_result = detect_address_in_message(
    None, "Müllerweg in 41836 Htown"
)
print("---address_test_result---")
print(address_test_result)
