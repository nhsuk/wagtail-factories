from collections import OrderedDict

import pytest
try:
    from wagtail.wagtailcore.blocks import StreamValue
    from wagtail.wagtailimages.models import Image
except ImportError:
    from wagtail.core.blocks import StreamValue
    from wagtail.images.models import Image

import wagtail_factories
from tests.testapp.factories import MyBlockFactory, MyBlockItemFactory, MyTestPageWithStreamFieldFactory


@pytest.mark.django_db
def test_list_block_factory():
    factory = wagtail_factories.ListBlockFactory(wagtail_factories.CharBlockFactory)
    value = factory(items=["A", "B", "C"])
    assert value == ["A", "B", "C"]


@pytest.mark.django_db
def test_struct_inside_list_block_factory():
    factory = wagtail_factories.ListBlockFactory(MyBlockItemFactory)
    value = factory(
        items=[{
            'label': 'List Block Test 1',
            'value': 123,
        },{
            'label': 'List Block Test 2',
            # Do not specify value, it should use the default
        }, {
            # empty dict, to test the default values of label and value
        }]
    )
    assert value == [{
        'label': 'List Block Test 1',
        'value': 123,
    },{
        'label': 'List Block Test 2',
        'value': 100,
    },{
        'label': 'my-label',
        'value': 100,
    }]


@pytest.mark.django_db
def test_struct_block_factory():
    value = MyBlockFactory(
        title="My test title",
        item={'label':"My test item label"},
        items=[{}],
        image=None,
    )
    assert value == {
        'title': "My test title",
        'item': {
            'label': "My test item label",
            'value': 100,
        },
        'items':[{
            'label': "my-label",
            'value': 100,
        }],
    }


@pytest.mark.django_db
def test_image_block_factory():
    assert Image.objects.count() == 0
    value = wagtail_factories.ImageChooserBlockFactory()
    assert Image.objects.count() == 1
    image = Image.objects.first()
    assert value == image.id


@pytest.mark.django_db
def test_image_inside_struct_factory():
    assert Image.objects.count() == 0
    value = MyBlockFactory(
        # Don't bother with the other block types
        title=None,
        item=None,
        items=None,
    )
    assert Image.objects.count() == 1
    assert value == {
        'image': Image.objects.first().id,
    }


@pytest.mark.django_db
def test_page_with_streamfield():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = MyTestPageWithStreamFieldFactory(
        parent=root_page,
        body__streamdata=[
            ('struct', {}),
            ('int_array', [1, 2, 3]),
            ('char_array', ["A", "B", "C"]),
            ('image', {}),
        ]
    )
    assert isinstance(page.body, StreamValue)
    print(page.body)

    assert 'class="block-struct"' in str(page.body)
    assert 'class="block-int_array"' in str(page.body)
    assert 'class="block-char_array"' in str(page.body)
    assert 'class="block-image"' in str(page.body)


@pytest.mark.django_db
def test_page_with_streamfield_repeating():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = MyTestPageWithStreamFieldFactory(
        parent=root_page,
        body__streamdata=[
            ('struct', {}),
            ('struct', {}),
            ('struct', {}),
        ]
    )

    assert len(page.body) == 3
