import factory

import wagtail_factories

from . import models


class MyBlockItemFactory(wagtail_factories.StructBlockFactory):
    label = "my-label"
    value = 100

    class Meta:
        model = models.MyBlockItem


class MyBlockFactory(wagtail_factories.StructBlockFactory):
    title = "my title"
    item = factory.SubFactory(MyBlockItemFactory)
    items = wagtail_factories.ListBlockFactory(MyBlockItemFactory)
    image = factory.SubFactory(wagtail_factories.ImageChooserBlockFactory)

    class Meta:
        model = models.MyBlock


class MyTestPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = models.MyTestPage


class MyStreamBlockFactory(wagtail_factories.StreamBlockFactory):

    title = "my title"
    subtitle = "my subtitle"
    item = factory.SubFactory(MyBlockItemFactory)
    items = wagtail_factories.ListBlockFactory(MyBlockItemFactory)
    image = factory.SubFactory(wagtail_factories.ImageChooserBlockFactory)

    class Meta:
        model = models.MyStreamBlock


class MyTestPageGetOrCreateFactory(wagtail_factories.PageFactory):
    class Meta:
        model = models.MyTestPage
        django_get_or_create = ["slug", "parent"]


class MyTestPageWithStreamFieldFactory(wagtail_factories.PageFactory):

    body = wagtail_factories.StreamFieldFactory(
        {
            "char_array": wagtail_factories.ListBlockFactory(
                wagtail_factories.CharBlockFactory
            ),
            "int_array": wagtail_factories.ListBlockFactory(
                wagtail_factories.IntegerBlockFactory
            ),
            "struct": MyBlockFactory,
            "image": wagtail_factories.ImageChooserBlockFactory,
            "stream_block": wagtail_factories.StreamBlockSubFactory(MyStreamBlockFactory),
        }
    )

    class Meta:
        model = models.MyTestPage
