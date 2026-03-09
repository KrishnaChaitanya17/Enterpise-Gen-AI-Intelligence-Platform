from bson import ObjectId

def serialize_mongo(doc):
    if not doc:
        return doc

    # If list of documents
    if isinstance(doc, list):
        return [serialize_mongo(d) for d in doc]

    # If single document
    if isinstance(doc, dict):
        new_doc = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                new_doc[key] = str(value)
            else:
                new_doc[key] = value
        return new_doc

    return doc