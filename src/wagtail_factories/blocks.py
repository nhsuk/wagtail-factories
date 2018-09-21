from collections import defaultdict

import factory
from factory.declarations import ParameteredAttribute

try:
    from wagtail.wagtailcore import blocks
    from wagtail.wagtailimages.blocks import ImageChooserBlock
except ImportError:
    from wagtail.core import blocks
    from wagtail.images.blocks import ImageChooserBlock

from wagtail_factories.factories import ImageFactory

__all__ = [
    'CharBlockFactory',
    'IntegerBlockFactory',
    'StreamFieldFactory',
    'ListBlockFactory',
    'StructBlockFactory',
    'ImageChooserBlockFactory',
]


class StreamFieldFactory(ParameteredAttribute):
    """
        Syntax:
            <streamfield>__<index>__<block_name>__<key>='foo',

    """
    def __init__(self, field_definition, factories, **kwargs):
        super(StreamFieldFactory, self).__init__(**kwargs)
        self.factories = {block_type: factory for block_type, factory in factories}
        self.field_definition = field_definition

    def generate(self, step, params):
        result = []

        streamdata = params.get('streamdata', [])
        for block_type, value in streamdata:
            # Look for the block factory from the block type
            try:
                block_factory = self.factories[block_type]
            except KeyError:
                continue

            if isinstance(value, dict):
                block_value = block_factory(**value)
            elif isinstance(value, list):
                block_value = block_factory(items=value)
            else:
                block_value = block_factory(value=value)

            result.append({'type': block_type, 'value': block_value})

        stream_block = self.field_definition.field.stream_block
        return blocks.StreamValue(stream_block, result, is_lazy=True)


class ListBlockFactory(factory.SubFactory):
    def __call__(self, **kwargs):
        return self.generate(None, kwargs)

    def generate(self, step, params):
        subfactory = self.get_factory()

        result = []
        items = params.get('items', [])
        for value in items:
            if isinstance(value, dict):
                block_value = subfactory(**value)
            elif isinstance(value, list):
                block_value = subfactory(items=value)
            else:
                block_value = subfactory(value=value)

            result.append(block_value)

        return result


class BlockFactory(factory.Factory):
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, value):
        return model_class().clean(value)

    @classmethod
    def _create(cls, model_class, value):
        return model_class().clean(value)


class CharBlockFactory(BlockFactory):
    class Meta:
        model = blocks.CharBlock


class IntegerBlockFactory(BlockFactory):
    class Meta:
        model = blocks.IntegerBlock


class ChooserBlockFactory(BlockFactory):
    pass


class ImageChooserBlockFactory(ChooserBlockFactory):

    value = factory.SubFactory(ImageFactory)

    class Meta:
        model = ImageChooserBlock

    @classmethod
    def _build(cls, model_class, value):
        return cls._create(cls, model_class, value)

    @classmethod
    def _create(cls, model_class, value):
        return model_class().get_prep_value(model_class().clean(value))


class StructBlockFactory(factory.Factory):

    class Meta:
        model = blocks.StructBlock

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        result = {}
        block = model_class()

        for name, child_block in block.child_blocks.items():
            subfactory = getattr(cls, name, None)
            try:
                block_args = kwargs[name]
                # If block_args are actually defined as None, skip over this block
                if block_args == None:
                    continue
            except KeyError:
                block_args = None

            # If a subfactory is defined, use the block arguments to get a value
            if subfactory and isinstance(subfactory, factory.SubFactory):
                if isinstance(block_args, dict):
                    value = subfactory.get_factory()(**block_args)
                elif isinstance(block_args, list):
                    value = subfactory(items=block_args)
                else:
                    value = subfactory.get_factory()(value=block_args)
            else:
                # If the subfactory isn't an isntance of subfactory, it must be
                # a plain value to use as a default.
                default_value = subfactory
                value = block_args or default_value

            result[name] = value

        return result

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)
