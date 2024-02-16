# Run this as: python batch_reproject.py run <path/to/input/payload>

from stactask import Task


class Reproject(Task):
    name = "reproject"
    description = "Reproject some assets to a new CRS"

    def process(self, **kwargs):
        assert len(self.items) == 1, "Only one item should be passed to this task"
        item = self.items[0]

        item = self.reproject_item(item, **self.parameters)

        self.logger.info(f"Reprojected {item.id}")

        return [item.to_dict(include_self_link=True, transform_hrefs=False)]

    def reproject_item(self, item, assets, crs): ...


Reproject.cli()
