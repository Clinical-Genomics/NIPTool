import logging
from typing import List

from mongo_adapter import MongoAdapter
from datetime import datetime as dt
from pydantic import parse_obj_as
from NIPTool.models.database import Batch, Sample

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

        document_id = document_news.get("_id")
        if not document_id:
            document_id = collection.insert(document_news)
            LOG.info("Added document %s.", document_id)
        else:
            update_result = collection.update_one(
                {"_id": document_id}, {"$set": document_news}, upsert=True
            )
            if not update_result.raw_result["updatedExisting"]:
                collection.update_one(
                    {"_id": document_id}, {"$set": {"added": dt.today()}}
                )
                LOG.info("Added document %s.", document_id)
            elif update_result.modified_count:
                collection.update_one(
                    {"_id": document_id}, {"$set": {"updated": dt.today()}}
                )
                LOG.info("Updated document %s.", document_id)
            else:
                LOG.info("No updates for document %s.", document_id)
        return document_id

    def user(self, username: str):
        """Find user from user collection"""

        return self.user_collection.find_one({"_id": username})

    def batches(self)-> List[Batch]:
        """Return all batches from the batch collection"""

        batches = self.batch_collection.find()
        return parse_obj_as(List[Batch], batches)

    def batch(self, batch_id)-> Batch:
        """Find one batch from the batch collection"""

        batch_data: dict = self.batch_collection.find_one({"_id": batch_id})
        batch_data['batch_id']: str = batch_data.pop('_id')
        return Batch(**batch_data)

    def sample(self, sample_id)-> Sample:
        """Find one sample from the sample collection"""

        sample_data = self.sample_collection.find_one({"_id": sample_id})
        sample_data['sample_id']: str = sample_data.pop('_id')
        return Sample(**sample_data)

    def sample_aggregate(self, pipe: list)-> List[Sample]:
        """Aggregates a query pipeline on the sample collection"""

        samples =  self.sample_collection.aggregate(pipe)
        return parse_obj_as(List[Sample], samples)

    def batch_aggregate(self, pipe: list)->List[Batch]:
        """Aggregates a query pipeline on the sample collection"""

        batches = self.batch_collection.aggregate(pipe)
        return parse_obj_as(List[Batch], batches)

    def batch_samples(self, batch_id)-> List[Sample]:
        """All samples within the batch"""

        samples = self.sample_collection.find({"SampleProject": batch_id})
        return parse_obj_as(List[Sample], samples)