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
    'StreamBlockFactory',
    'StreamBlockSubFactory',
]


class StreamFieldFactory(ParameteredAttribute):
    """
        Syntax:
            <streamfield>__<index>__<block_name>__<key>='foo',

    """
    def __init__(self, factories, **kwargs):
        super(StreamFieldFactory, self).__init__(**kwargs)
        self.factories = factories

    def generate(self, step, params):

        result = defaultdict(lambda: defaultdict(lambda: defaultdict()))

        for key, value in params.items():
            try:
                index, block_name, param = key.split('__', 2)
            except ValueError:
                continue
            if not index.isdigit():
                continue

            index = int(index)
            result[index][block_name][param] = value

        retval = []
        for index, block_items in sorted(result.items()):
            for block_name, block_params in block_items.items():
                try:
                    block_factory = self.factories[block_name]
                except KeyError:
                    raise ValueError(
                        "No factory defined for block `%s`" % block_name)

                value = block_factory(**block_params)
                retval.append((block_name, value))
        print("\nRETVAL\n", retval)
        return retval


class ListBlockFactory(factory.SubFactory):
    def __call__(self, **kwargs):
        return self.generate(None, kwargs)

    def generate(self, step, params):
        subfactory = self.get_factory()

        result = defaultdict(dict)
        for key, value in params.items():
            if key.isdigit():
                result[int(key)]['value'] = value
            else:
                prefix, label = key.split('__', 2)
                if prefix and prefix.isdigit():
                    result[int(prefix)][label] = value

        retval = []
        for index, index_params in sorted(result.items()):
            item = subfactory(**index_params)
            retval.append(item)

        return retval


class StreamBlockSubFactory(factory.SubFactory):

    class Meta:
        model = blocks.StreamBlock

    def __call__(self, **kwargs):
        return self.generate(None, kwargs)

    def generate(self, step, params):
        subfactory = self.get_factory()
        result = defaultdict(dict)
        for key, value in params.items():
            index, block_name = key.split('__', 1)
            result[int(index)] = (block_name, value)

        _retval = []
        for index, (block_name, value) in sorted(result.items()):
            value = subfactory(block_name=block_name, value=value)
            _retval.append((block_name, value))

        return blocks.StreamValue(subfactory._meta.model(), _retval)


class StreamBlockFactory(factory.Factory):

    @classmethod
    def _build(cls, model_class, block_name, value, *args, **kwargs):
        block = model_class()
        child_block = block.child_blocks[block_name]
        return child_block.to_python(value)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)


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

    image = factory.SubFactory(ImageFactory)

    class Meta:
        model = ImageChooserBlock

    @classmethod
    def _build(cls, model_class, image):
        return image

    @classmethod
    def _create(cls, model_class, image):
        return image


class StructBlockFactory(factory.Factory):

    class Meta:
        model = blocks.StructBlock

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        block = model_class()
        return blocks.StructValue(block, [
            (
                name,
                (kwargs[name] if name in kwargs else child_block.get_default())
            )
            for name, child_block in block.child_blocks.items()
        ])

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)
