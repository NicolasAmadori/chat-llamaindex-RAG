import pandas as pd
import json, sys, os

# import from configuration module
from project_config import (
    SPEECHES_FILE_NAME,
    ACTS_FILE_NAME,
    EVAL_DATASETS_FOLDER,
)



def read_and_format_speeches():
    try:
        with open(SPEECHES_FILE_NAME, 'r') as f:
            speeches = json.load(f)["body"]["interventi"]
    except FileNotFoundError:
        print("Speeches file not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print("JSON speeches file not valid")
        sys.exit(1)

    dataset_speeches = []
    for speech in speeches:
        dataset_speeches.append({
            "id": speech["ID"]["value"],
            "speaker": f"{speech['nome']['value']} {speech['cognome']['value']}",
            "session_title": speech["titolo"]["value"],
            "date_time": speech["data"]["value"],
            "legislature": f"Legislatura {speech['legislatura']['value']}",
            "party": speech["gruppo"]["value"],
            "position": speech["incarico_governativo"]["value"],
            "transcription": speech["trascrizione"]["value"]
        })

    for speech in dataset_speeches:
        speech["formatted_data"] = (
            "-- Intervento in sessione della Camera dei Deputati --"
            f"\n{speech['legislature']} {speech['date_time']}"
            f"\nOratore: {speech['speaker']} ({speech['party']}), incarico governativo: {speech['position']}"
            f"\nTitolo della sessione: {speech['session_title']}"
            f"\nTrascrizione dell\'intervento: {speech['transcription']}"
        )

    df_formatted = pd.DataFrame(dataset_speeches)
    df_formatted.set_index('id', inplace=True)
    return df_formatted


def read_and_format_acts():
    try:
        with open(ACTS_FILE_NAME, 'r') as f:
            acts = json.load(f)["body"]["atti"]
    except FileNotFoundError:
        print("Acts file not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print("JSON acts file not valid")
        sys.exit(1)

    dataset_acts = []
    for act in acts:
        dataset_acts.append({
            "id": act["ID"]["value"],
            "title": act["titolo"]["value"],
            "initiative": act['iniziativa']['value'],
            "legislature": f"Legislatura {act['legislatura']['value']}",
            "proposal_date": act["dataProposta"]["value"],
            "approval_date": act['dataApprovazione']['value'],
            "doc_pages": act["pages"]["value"],
        })
    
    df = pd.DataFrame(dataset_acts)
    df.set_index('id', inplace=True)
    return df


def read_eval_datasets():
    datasets = []
    for filename in os.listdir(EVAL_DATASETS_FOLDER):
        if filename.endswith(".json"):
            file_path = os.path.join(EVAL_DATASETS_FOLDER, filename)
            with open(file_path, 'r') as file:
                content = json.load(file)
                datasets.append({
                    "act_id" : content["act_id"],
                    "dataset" : pd.DataFrame(content["body"]),
                })
    return datasets
