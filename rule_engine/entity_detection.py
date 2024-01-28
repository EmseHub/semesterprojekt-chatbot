import re

from data_service import students, courses
from helpers import get_random_item_in_list


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


def get_student_from_message(message_processed):
    obj_result = {"student": None, "query": ""}

    if not message_processed or not message_processed.strip():
        return obj_result

    # Prüfen, ob Nachricht Nummern enthält
    min_length_matnr = 6
    numbers_in_message = re.findall(r'\d+', message_processed)

    if not numbers_in_message or not any(len(nr) >= min_length_matnr for nr in numbers_in_message):
        obj_result["query"] = get_random_item_in_list(
            [
                'Ich bräuchte noch Deine Matrikelnummer.',
                'Verrätst Du mir noch Deine Matrikelnummer?'
            ]
        )
        return obj_result

    # Prüfen, ob Nummern im Text bekannten Matrikelnummern entsprechen
    matching_students = [
        s for s in students if (s["matnr"] in numbers_in_message)
    ]

    if not matching_students:
        obj_result["query"] = 'Die angegebene Zahl stimmt mit keiner Matrikelnummer überein. Gib bitte Deine vollständige Matrikelnummer an.'
        return obj_result

    if len(matching_students) > 1:
        obj_result["query"] = 'Welche der angegebenen Matrikelnummern gehört zu Dir? Gib sie bitte erneut an.'
        return obj_result

    # Student eindeutig zugeordnet
    obj_result["student"] = matching_students[0]
    return obj_result


test_result = get_student_from_message('1234567 1122334')
print('---test_result---')
print(test_result)
