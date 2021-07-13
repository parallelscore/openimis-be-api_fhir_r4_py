from enum import Enum


class BundleType(Enum):
    DOCUMENT = "document"
    MESSAGE = "message"
    TRANSACTION = "transaction"
    TRANSACTION_RESPONSE = "transaction-response"
    BATCH = "batch"
    BATCH_RESPONSE = "batch-response"
    HISTORY = "history"
    SEARCHSET = "searchset"
    COLLECTION = "collection"


class BundleLinkRelation(Enum):
    SELF = "self"
    NEXT = "next"
    PREVIOUS = "previous"
    LAST = "last"
    FIRST = "first"
