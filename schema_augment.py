import json

data_file = 'result/1week_data.txt_part_1.json'

# region load data files

with open(data_file) as f:
    data = []
    for line in f.readlines():
        content = json.loads(line)
        if len(content["event_triggers"]) > 0 and len(content["entity_mentions"]) > 0:
            data.append(json.loads(line))

with open('assets/entity_event_corpus.json') as f:
    entity_event_corpus = json.load(f)

with open('assets/synonym_dict.json') as f:
    synonym_dict = json.load(f)

# end region

# region logic

import random

for content in data:
    entity_id_type_map = dict()
    entity_id_text_map = dict()
    trigger_id_type_map = dict()
    trigger_id_text_map = dict()
    for entity in content["entity_mentions"]:
        entity_id_type_map[entity["entity_id"]] = entity["entity_type"]
        entity_id_text_map[entity["entity_id"]] = entity["text"]

    for trigger in content["event_triggers"]:
        trigger_id_type_map[trigger["trigger_id"]] = trigger["event_type"]
        trigger_id_text_map[trigger["trigger_id"]] = trigger["text"]

    for arg in content["event_arguments"]:
        entity_type, trigger_type, role_type = (
            entity_id_type_map[arg["entity_id"]],
            trigger_id_type_map[arg["trigger_id"]],
            arg["role_type"],
        )
        orig_trigger = trigger_id_text_map[arg["trigger_id"]]
        orig_entity = entity_id_text_map[arg["entity_id"]]

        corpus_by_trigger = entity_event_corpus["event"][trigger_type]
        if role_type not in corpus_by_trigger["entity"] or entity_type not in corpus_by_trigger["entity"][role_type]:
            continue

        print("<%s, %s, %s>" % (entity_type, trigger_type, role_type))
        print(
            "Original Trigger: %s" % orig_trigger,
            "---",
            "Alternative Trigger: %s" % random.choice(corpus_by_trigger["text"])
        )
        print(
            "Original Entity: %s" % orig_entity,
            "---",
            "Alternative Entity: %s" % random.choice(corpus_by_trigger["entity"][role_type][entity_type])
        )
        # TODO: replace `trigger` & `entity` with `alternative trigger` & `alternative entity` in the original record -> new record

        # Can use GenAI to generate new sentence based on schema, using the prompt like
        # Cho một Schema đầu vào dạng <Entity type, Event Trigger type, Role>, hãy sử dụng schema này để tạo ra một câu với độ dài vừa đủ, phục vụ cho nhiệm vụ Event Extraction. 
        # Không tạo ra thừa Entity hoặc Trigger. 
        # Đầu ra là một JSON dạng {"text" : <câu đầu ra>}
        # <MONEY, Transfer-ownership, Price> Trigger: trả giá --- Entity: 10.872 tỷ đồng

    print("\n#################\n")

# end region
