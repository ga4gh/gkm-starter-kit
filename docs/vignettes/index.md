# Vignettes

Vignettes are the third pillar of the Starter Kit: real community use cases, each told as one story about who, what problem, and what GKS unlocks, with the actual data and tools. The common thread is always the same: *what a group needs the standards for, and the standards delivering it.*

Some vignettes build on the other two pillars: [Data Bundles](../data/index.md) for packaged, shareable knowledge and the [Python Package](../library/index.md) for loading and working with it. Others do not, such as reclassifying a variant within a single resource as its evidence base changes. Both kinds belong here; the point is the use case, not which parts of the toolkit it happens to use.

{% set vignettes = list_vignettes() %}

{% if vignettes | length == 0 %}

_No vignettes yet. Be the first to [contribute one](../contribute.md)._

{% else %}

## Browse vignettes

**By product:** {% for product in vignettes | map(attribute='products') | sum(start=[]) | map(attribute='name') | unique | sort %}[{{ product }}](by-product/{{ product | lower | replace(' ', '-') | replace('/', '-') }}/index.md){.gks-chip} {% endfor %}

{% set patterns = pattern_labels() %}
**By pattern:** {% for pattern in vignettes | map(attribute='pattern') | unique | sort %}[{{ patterns.get(pattern, pattern) }}](by-pattern/{{ pattern | lower | replace(' ', '-') | replace('/', '-') }}/index.md){.gks-chip} {% endfor %}

**By implementer:** {% for impl in vignettes | map(attribute='implementer') | unique | sort %}[{{ impl }}](by-implementer/{{ impl | lower | replace(' ', '-') | replace('/', '-') }}/index.md){.gks-chip} {% endfor %}

## All vignettes

{% for v in vignettes %}

### [{{ v.title }}]({{ v._path }}) <span class="gks-status gks-status--{{ v.status }}">{{ v.status }}</span>

**{{ v.implementer }}** · {% for p in v.products %}{{ p.name }}{% if p.version %} {{ p.version }}{% endif %}{% if not loop.last %}, {% endif %}{% endfor %} · _{{ patterns.get(v.pattern, v.pattern) }}_

{{ v.summary }}

[Read →]({{ v._path }})

---

{% endfor %}

{% endif %}
