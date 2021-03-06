"""Override of Oscar's Catalogue app Models."""

from urllib import pathname2url as to_url

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from oscar.apps.catalogue import abstract_models
from oscar.apps.catalogue.abstract_models import AbstractCategory, AbstractProductCategory

from django.utils.encoding import python_2_unicode_compatible
from marine_parts.apps.catalogue.abstract_models \
    import AbstractReplacementProduct


class Category(AbstractCategory):
    """Override of Category Model."""

    name = models.CharField(_('Name'), max_length=900, db_index=True)
    description = models.TextField(_('Description'), blank=True)
    slug = models.fields.SlugField(_('Slug'), max_length=900, db_index=True)

    diagram_image = models.ImageField(
        _('Diagram'),
        upload_to='categories',
        blank=True,
        null=True,
        max_length=255,
        help_text=_("Parts Diagram. Only upload a diagram image if "
                    "you are creating a Leaf Category (Component).")
    )

    def get_absolute_url(self):
        """Building the url that points to the search of the category."""
        url = reverse('search:search') + '?var=category:' + \
            to_url(self.full_slug)
        return url

    def get_search_url(self):
        """Build part of the url that points to the search of the category."""
        return 'category:' + to_url(self.full_slug)


@python_2_unicode_compatible
class ProductCategory(AbstractProductCategory):
    """Override to include diagram numbers."""

    diagram_number = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        verbose_name=_("Diagram number"),
        help_text=_("Number associated with part diagram.")
    )

    # Document this feature and erase this code when it was done.
    def __repr__(self):
        return u'%s' % self.category.full_name

    def __str__(self):
        return u'%s' % self.category.full_name


# @python_2_unicode_compatible
class Product(abstract_models.AbstractProduct):
    """Override to include replacement and recommended products."""

    replacement_products = models.ManyToManyField(
        'Product', through='ReplacementProduct', blank=True,
        related_name='replacements',
        verbose_name=_("Replacement products"),
        through_fields=('primary', 'replacement'),
        help_text=_("These are products that are designated to replace "
                    "main product."))

    recommended_products = models.ManyToManyField(
        'Product', through='ProductRecommendation', blank=True,
        related_name='recommendations',
        verbose_name=_("Recommended products"),
        through_fields=('primary', 'recommendation'),
        help_text=_("These are products that are recommended to accompany the "
                    "main product."))


class ReplacementProduct(AbstractReplacementProduct):
    pass


class Cat():
    """Auxiliar Category structure for search view."""

    pass

from oscar.apps.catalogue.models import *  # noqa isort:skip
