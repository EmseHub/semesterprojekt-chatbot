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

    if not matching_students:
        result["query"] = "Die angegebene Zahl stimmt mit keiner Matrikelnummer überein. Gib bitte Deine vollständige Matrikelnummer an."
        return result

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


student_test_result = detect_student_in_message("1234567 1122334")
print("---student_test_result---")
print(student_test_result)

course_test_result = detect_course_in_message("muggelkunde")
print("---course_test_result---")
print(course_test_result)
