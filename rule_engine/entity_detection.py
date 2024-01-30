import re

from rule_engine.data_service import students, courses
from rule_engine.helpers import parse_json_file, get_random_item_in_list, replace_diacritics

parsed_postal_codes = parse_json_file('rule_engine/postal-codes.json')

# Hinweis: Parameter "message_raw" bedeutet, dass der Originaltext übergeben wurde – unverändert, bis auf die Tatsache, dass jeder White Space auf ein Leerzeichen reduziert ist
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
    if (not message_processed or not message_processed.strip()):
        return result
    # Prüfen, ob Nachricht Nummern enthält
    min_length_matnr = 6
    numbers_in_message = re.findall(r'\d+', message_processed)
    if (not numbers_in_message or not any(len(nr) >= min_length_matnr for nr in numbers_in_message)):
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
    if (not matching_students):
        result["query"] = "Die angegebene Zahl stimmt mit keiner Matrikelnummer überein. Gib bitte Deine vollständige Matrikelnummer an."
        return result
    # Prüfen, ob mehrere Students gefunden wurden
    if (len(matching_students) > 1):
        result["query"] = f"Welche der {len(
            matching_students)} angegebenen Matrikelnummern gehört zu Dir? Gib sie bitte erneut an."
        return result
    # Student eindeutig ermittelt
    result["student"] = matching_students[0]
    return result


def detect_course_in_message(message_processed):
    result = {"course": None, "query": ""}
    if (not message_processed or not message_processed.strip()):
        return result
    # Prüfen, ob die Nachricht den Namen des Kurses enthält
    matching_courses = [
        course for course in courses if replace_diacritics(course["name"].lower()) in message_processed
    ]
    # Prüfen, ob ein oder mehrere Kurse gefunden wurden
    if (not matching_courses):
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

    if (not message_raw or not message_raw.strip()):
        return {"address": detected_address_new, "query": ""}

    # Kommata durch Leerzeichen ersetzen
    message_processed = message_raw.replace(',', ' ')
    # Alle Varianten von "in" durch Leerzeichen ersetzen
    message_processed = re.sub(
        r"\s+in\s+", " ", message_processed, flags=re.IGNORECASE
    )
    # Jeden White Space auf ein Leerzeichen reduzieren
    message_processed = re.sub(r"\s+", " ", message_processed).strip()

    # Adress-Attribute initialiseren mit bereits erkannten Werten oder None
    strasse = detected_address_new.get("strasse")
    hausnr = detected_address_new.get("hausnr")
    plz = detected_address_new.get("plz")
    stadt = detected_address_new.get("stadt")

    # Falls Adresse noch gar nicht definiert ist (auch nicht unvollständig), versuche alle Attribute auf einmal auszulesen
    if (not detected_address_new):
        # Staat der neuen Adresse mit "Deutschland" initialisieren, da der Chatbot andere Staaten erstmal nicht berücksichtigt
        detected_address_new["staat"] = "Deutschland"
        # Mit RegEx Adressen-Syntax erkennen (Musterstr. 55 12345 Musterstadt)
        regex_match = re.search(
            r"\b((([a-zäöüß]{2,}(-?))+(\s+)?(str(\.?)|straße|strasse|weg))|([a-zäöüß]{2,}(-?))*)\s+\d{1,4}([a-z]*)\s+\d{5}\s+([a-zäöüß]{2,}(-)?)*[a-zäöüß]{2,}(?![a-z0-9äöüß-])",
            message_processed,
            re.IGNORECASE
        )
        if (regex_match):
            regex_match_string = regex_match.group()
            # "Ein-Beispiel Weg 55 12345 Musterstadt" an der ersten Ziffer in zwei Substrings aufteilen, damit Leerzeichen im Straßennamen nicht als Trenner dient
            regex_match_string_splitted_by_1st_digit = re.split(
                r'(\d+.*)',
                regex_match_string
            )
            # ["Ein-Beispiel Weg ", "55 12345 Musterstadt", ""]
            regex_match_string_before_1st_digit = regex_match_string_splitted_by_1st_digit[0]
            # "Ein-Beispiel Weg " verwendet für Straße
            regex_match_string_from_1st_digit = regex_match_string_splitted_by_1st_digit[1]
            regex_match_string_from_1st_digit_splitted = regex_match_string_from_1st_digit.strip().split()
            # ["55", "12345", "Musterstadt"] verwendet für Rest
            if (len(regex_match_string_from_1st_digit_splitted) > 2):
                # Erkannte Adress-Angaben zuweisen
                strasse = regex_match_string_before_1st_digit.strip()
                hausnr = regex_match_string_from_1st_digit_splitted[0]
                plz = regex_match_string_from_1st_digit_splitted[1]
                stadt = regex_match_string_from_1st_digit_splitted[2]

    # Falls Straße und Hausnummer fehlen, versuche gezielt beide auf einmal auszulesen
    if (not strasse and not hausnr):
        # Mit RegEx Straße-Hausnummer-Syntax erkennen (Musterstr. 55)
        regex_match = re.search(
            r"\b((([a-zäöüß]{2,}(-?))+(\s+)?(str(\.?)|straße|strasse|weg))|([a-zäöüß]{2,}(-?))*)\s+\d{1,4}([a-z]*)\b",
            message_processed,
            re.IGNORECASE
        )
        if (regex_match):
            regex_match_string = regex_match.group()
            # "Ein-Beispiel Weg 55" an der ersten Ziffer in zwei Substrings aufteilen, damit Leerzeichen im Straßennamen nicht als Trenner dient
            regex_match_string_splitted_by_1st_digit = re.split(
                r'(\d+.*)',
                regex_match_string
            )
            # ["Ein-Beispiel Weg ", "55", ""]
            regex_match_string_before_1st_digit = regex_match_string_splitted_by_1st_digit[0]
            # "Ein-Beispiel Weg " verwendet für Straße
            regex_match_string_from_1st_digit = regex_match_string_splitted_by_1st_digit[1]
            # "55" verwendet für Hausnummer
            if (len(regex_match_string_splitted_by_1st_digit) > 1):
                # Erkannte Adress-Angaben zuweisen
                strasse = regex_match_string_splitted_by_1st_digit[0].strip()
                hausnr = regex_match_string_splitted_by_1st_digit[1].strip()

    # Falls Straße noch fehlt, versuche diese gezielt auszulesen
    if (not strasse):
        # Mit RegEx Straßen-Syntax erkennen (Musterstr. 55)
        regex_match = re.search(
            r"\b([a-zäöüß]{2,}(-?))+(\s+)?(str(\.?)|straße|strasse|weg)(?![a-z0-9äöüß-])",
            message_processed,
            re.IGNORECASE
        )
        if (regex_match):
            regex_match_string = regex_match.group()
            strasse = regex_match_string.strip()

    # Falls Hausnummer noch fehlt, versuche diese gezielt auszulesen
    if (not hausnr):
        # Mit RegEx Hausnummer-Syntax erkennen (Meine Hausnummer ist 55)
        regex_match = re.search(
            r"\b(hausnummer|nummer|hausnr(\.?)|nr(\.?))(\s+(lautet|ist(\s+die)?))*\s+\d{1,4}([a-z]*)\b",
            message_processed,
            re.IGNORECASE
        )
        if (regex_match):
            regex_match_string = regex_match.group()
            regex_match_splitted = regex_match_string.strip().split()
            if len(regex_match_splitted) > 1:
                hausnr = regex_match_splitted[-1]

    # Falls Hausnummer immer noch fehlt, aber bereits eine Strasse angegeben wurde, versuche eine passende Ziffern-/Zeichenfolge auszulesen
    if (strasse and not hausnr):
        # Mit RegEx Hausnummer-Syntax erkennen (Bla bla 55a)
        regex_match = re.search(
            r"\b\d{1,4}[a-z]*\b",
            message_processed,
            re.IGNORECASE
        )
        if (regex_match):
            regex_match_string = regex_match.group()
            if (regex_match_string):
                hausnr = regex_match_string.strip()

    # Falls PLZ und Stadt fehlen, versuche gezielt beide auf einmal auszulesen
    if (not plz and not stadt):
        # Mit RegEx PLZ-Stadt-Syntax erkennen (12345 Musterstadt)
        regex_match = re.search(
            r"\b\d{5}(\,?)\s+([a-zäöüß]{2,}(-)?)*[a-zäöüß]{2,}(?![a-z0-9äöüß-])",
            message_processed,
            re.IGNORECASE
        )
        if (regex_match):
            regex_match_string = regex_match.group()
            # "12345 Musterstadt"
            regex_match_string_splitted = regex_match_string.split()
            # ["12345", "Musterstadt"]
            if (len(regex_match_string_splitted) > 1):
                # Erkannte Adress-Angaben zuweisen
                plz = regex_match_string_splitted[0].strip()
                stadt = regex_match_string_splitted[1].strip()

    # Falls PLZ noch fehlt, versuche diese gezielt auszulesen
    if (not plz):
        # Mit RegEx PLZ-Syntax erkennen (12345)
        regex_match = re.search(
            r"\b\d{5}(?![a-z0-9äöüß-])",
            message_processed,
            re.IGNORECASE
        )
        if (regex_match):
            regex_match_string = regex_match.group()
            plz = regex_match_string.strip()

    # Falls Stadt noch fehlt, aber eine PLZ vorhanden ist, versuche anhand der DB die Stadt aus der PLZ abzuleiten
    if (plz and not stadt):
        # PLZ in DB suchen
        stadt_in_data = next(
            (postal_code for postal_code in parsed_postal_codes if postal_code["zipcode"] == plz), None
        )
        if (stadt_in_data):
            stadt = stadt_in_data["city"]

    # Falls Stadt und PLZ noch fehlen, versuche einen Stadtnamen aus der DB zu erkennen
    if (not plz and not stadt):
        # Roh-Nachricht vergleichbar machen
        message_processed = replace_diacritics(message_raw.lower())
        # "Meine" ist eine Stadt, die hier außen vor gelassen wird und nur mit PLZ gefunden werden kann
        message_processed = re.sub(r"\bmeine", "", message_processed)
        message_processed = re.sub(r"\s+", " ", message_processed).strip()
        # Überschneidungen mit Stadtnamen aus DB finden
        matches_in_data = [
            postal_code for postal_code in parsed_postal_codes if (replace_diacritics(postal_code["city"].lower()) in message_processed)
        ]
        if (matches_in_data):
            # Überschneidung mit größter Zeichenzahl wählen
            best_match = max(
                matches_in_data, key=lambda match: len(match["city"])
            )
            plz = best_match["zipcode"].strip()
            stadt = best_match["city"].strip()

    # Prüfen, welche Adress-Angaben fehlen, und entsprechende Rückfrage (query) ausgeben
    query = ""

    if (not strasse and not hausnr and not plz and not stadt):
        query += "Gib Deine neue Adresse gerne im folgenden Format an: Winkelgasse 93, 12345 Zauberstadt."
    else:
        if (not strasse and not hausnr):
            query += "Ich benötige noch den Straßennamen und die Hausnummer."
        elif (not strasse):
            query += "Es fehlt noch der Straßenname."
        elif (not hausnr):
            query += "Es fehlt noch die Hausnummer."

        query += " "

        if (not plz and not stadt):
            query += "Verrätst Du mir auch die PLZ und den Ort, in dem Du zukünftig residieren wirst?"
        elif (not plz):
            query += "Jetzt fehlt mir nur noch die PLZ Deiner neuen Anschrift."
        elif (not stadt):
            query += "Jetzt fehlt mir nur noch der Name des Ortes."

    query = query.strip()
    detected_address_new["strasse"] = strasse
    detected_address_new["hausnr"] = hausnr
    detected_address_new["stadt"] = stadt
    detected_address_new["plz"] = plz

    return {"address": detected_address_new, "query": query}


def detect_new_surname_in_message(student, tagged_tokens, message_raw):
    result = {"surname": None, "query": ""}
    if (not student or not tagged_tokens or not message_raw or not message_raw.strip()):
        return result

    # Nachricht bereinigen
    message_processed = message_raw
    # "jetzt" entfernen
    message_processed = re.sub(
        r"\bjetzt\b", " ", message_processed, flags=re.IGNORECASE
    )
    # Jeden White Space auf ein Leerzeichen reduzieren
    message_processed = re.sub(r"\s+", " ", message_processed).strip()

    # Wert, der als Nachname in Frage kommt
    potential_surname = None

    # Prüfen, ob Nachricht einen Doppelpunkt enthält
    if (":" in message_processed):
        # Substring ab dem letzten Doppelpunkt bis zum nächste Satzzeichen als neuen Nachnamen auslesen
        message_processed_splitted_by_colon = message_processed.split(":")
        message_processed_after_colon = message_processed_splitted_by_colon[-1]
        message_processed_after_colon_splitted_by_punctuationmarks = re.split(
            r'([^A-Za-zÄÖÜäöüß\s-])+', message_processed_after_colon
        )
        potential_surname = message_processed_after_colon_splitted_by_punctuationmarks[0].strip(
        )
        # Falls ein Name gefunden wurde, prüfen, ob der Vorname enthalten und Nachname wirklich neu ist
        if (potential_surname):
            # Ggf. Vornamen entfernen
            potential_surname = potential_surname.replace(
                student["vorname"], ""
            ).strip()

    # Falls kein Nachname gefunden wurde, prüfe, ob die Nachricht den Vornamen mit einem anderen Nachnamen als dem bisherigen enthält
    if (not potential_surname and student["vorname"] in message_processed):
        message_processed_splitted_at_vorname = message_processed.split(
            student["vorname"]
        )
        if (len(message_processed_splitted_at_vorname) > 1):
            # Text, der direkt auf den Vornamen folgt, extrahieren
            message_after_vorname = message_processed_splitted_at_vorname[-1].strip(
            )
            # Prüfen, ob der Text mit einem Großbuchstaben anfängt und ggf. das erste Wort als Nachnamen übernehmen
            if (message_after_vorname and message_after_vorname[0].isupper()):
                potential_surname = message_after_vorname.split()[0]
                # Satzzeichen entfernen
                potential_surname = re.sub(
                    r"[^A-Za-zÄÖÜäöüß\s-]", "", potential_surname
                ).strip()

    # Falls kein Nachname gefunden wurde, prüfe, ob die Nachricht eine Namensanhabe in RegEx-Syntax enthält (erkennt nur Namen ohne Leerzeichen)
    if (not potential_surname):
        regex_match = re.search(
            r"\b((ist|lautet|heißt|heisst|heisse|heiße|in|zu))\s+([A-ZÄÖÜ][a-zäöüß]+(-?))+",
            message_processed,
            re.IGNORECASE
        )
        if (regex_match):
            regex_match_string = regex_match.group()

            print("----regex_match_string----")
            print(regex_match_string)

            regex_match_splitted = regex_match_string.strip().split()
            if len(regex_match_splitted) > 1:
                potential_surname = regex_match_splitted[-1]

    # Falls kein Nachname gefunden wurde, prüfe, ob es ein Token mit dem POS-Tag "NE" gibt, der nicht den bisherigen Namen entspricht
    if (not potential_surname):
        surname_from_token = next(
            (tagged_token for tagged_token in tagged_tokens if (
                tagged_token["pos"] == "NE"
                and replace_diacritics(tagged_token["original"].lower()) != replace_diacritics(student["vorname"].lower().split()[0])
                and replace_diacritics(tagged_token["original"].lower()) != replace_diacritics(student["nachname"].lower())
            )),
            None
        )
        if (surname_from_token):
            potential_surname = surname_from_token["original"]

    # Falls kein Nachname gefunden wurde, prüfe, ob es nur einen Token gibt, der angegeben wurde
    if (not potential_surname and len(tagged_tokens) == 1):
        potential_surname = tagged_tokens[0]["original"]

    # Prüfen, ob der gefundene Nachname gültig und auch wirklich neu ist
    if (potential_surname and len(potential_surname) > 1 and replace_diacritics(potential_surname.lower()) != replace_diacritics(student["nachname"].lower()) and potential_surname[0].isupper()):
        # Satzzeichen entfernen
        potential_surname = re.sub(
            r"[^A-Za-zÄÖÜäöüß\s-]", "", potential_surname
        ).strip()
        result["surname"] = potential_surname
    else:
        result["query"] = get_random_item_in_list([
            "Wie genau lautet Dein neuer Nachname?",
            "Könntest Du nur Deinen Nachnamen bitte erneut angeben?",
            'Gib Deinen neuen Nachnamen gerne in folgender Form an: "Mein neuer Nachname lautet: Beispielname"'
        ])

    return result


# student_test_result = detect_student_in_message("1234567 1122334")
# print("---student_test_result---")
# print(student_test_result)


# course_test_result = detect_course_in_message("muggelkunde")
# print("---course_test_result---")
# print(course_test_result)


# address_test_result = detect_address_in_message(None, "Müllerweg 5 in 50737")
# print("---address_test_result---")
# print(address_test_result)


test_tokens = [
    {'original': 'Fehlren', 'korrigiert': 'Fehlern', 'lemma': 'Fehler', 'pos': 'NN'},
    {'original': 'House', 'korrigiert': 'Hose', 'lemma': 'Hose', 'pos': 'NN'},
    {'original': 'Homer', 'korrigiert': 'Homer', 'lemma': 'Homer', 'pos': 'NE'},
    {'original': 'Potter', 'korrigiert': 'Potter', 'lemma': 'Potter', 'pos': 'NE'}
]
test_tokens = [
    {'original': 'Plotter', 'korrigiert': 'Fehlern', 'lemma': 'Fehler', 'pos': 'NN'}
]
new_surname_test_result = detect_new_surname_in_message(
    students[0],
    test_tokens,
    "Ich heiße nicht mehr Harry James Potter, sondern mein Name ist jetzt Harry James Wattsefak"
)
print("---new_surname_test_result---")
print(new_surname_test_result)
