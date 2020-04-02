import logging

from mongo_adapter import MongoAdapter
from datetime import datetime as dt
LOG = logging.getLogger(__name__)

class NiptAdapter(MongoAdapter):

    def setup(self, db_name: str):
        """Setup connection to a database"""

        if self.client is None:
            raise SyntaxError("No client is available")
        self.db = self.client[db_name]
        self.db_name = db_name
        self.sample_collection = self.db.sample
        self.batch_collection = self.db.batch
        self.user_collection = self.db.user

        LOG.info("Use database %s.", db_name)

    def add_or_update_document(self, document_news: dict, collection):
        """Adds/updates a document in the database"""

        document_id = document_news['_id']

        update_result = collection.update_one({'_id': document_id}, 
                                                         {'$set': document_news}, 
                                                         upsert=True)

        if not update_result.raw_result['updatedExisting']:
            collection.update_one({'_id': document_id},
                                               {'$set': {
                                                   'added': dt.today()
                                               }})
            LOG.info("Added document %s.", document_id)
        elif update_result.modified_count:
            collection.update_one(
                {'_id': document_id}, {'$set': {
                    'updated': dt.today()
                }})
            LOG.info("Updated document %s.", document_id)
        else:
            LOG.info("No updates for document %s.", document_id)