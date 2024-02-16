#!/usr/bin/env python
from typing import Any, Dict, List
from cirrus.lib2.process_payload import ProcessPayload
from cirrus.lib2.logging import get_task_logger
from stactask import Task


LAMBDA_TYPE = "task"


class Download(Task):
    name = "download"
    description = "Download some assets to my S3"

    def process(self, **kwargs: Any) -> List[Dict[str, Any]]:
        assert len(self.items) == 1, "Only one item should be passed to this task"
        item = self.items[0]

        assets = self.parameters["assets"]
        item = self.download_item_assets(item, assets=assets)

        item = self.upload_item_assets_to_s3(item, assets=assets)

        self.logger.info(f"Downloaded and uploaded assets {assets} from {item.id}")

        return [item.to_dict(include_self_link=True, transform_hrefs=False)]


# TODO: This seems like an unnecessary wrapper/hack.
# Will Download.handler(event, context={}) work?
def lambda_handler(event, context={}):
    payload = ProcessPayload.from_event(event)
    logger = get_task_logger(
        f"{LAMBDA_TYPE}.download",
        payload=payload,
    )
    logger.info(f"Received payload: {payload['id']}")
    return Download.handler(payload)
