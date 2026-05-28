# Vignettes

Real-world walk-throughs of high-value GKS uses. Each vignette tells one story: who, what problem, what GKS unlocks, with the actual data and tools.

{% set vignettes = list_vignettes() %}

{% if vignettes | length == 0 %}

_No vignettes yet. Be the first to [contribute one](../contribute.md)._

{% else %}

## Filter

**By product:** {% for product in vignettes | map(attribute='products') | sum(start=[]) | map(attribute='name') | unique | sort %}[{{ product }}](by-product/{{ product | lower | replace(' ', '-') | replace('/', '-') }}/){.gks-chip} {% endfor %}

**By pattern:** {% for pattern in vignettes | map(attribute='pattern') | unique | sort %}[{{ pattern }}](by-pattern/{{ pattern | lower | replace(' ', '-') | replace('/', '-') }}/){.gks-chip} {% endfor %}

**By implementer:** {% for impl in vignettes | map(attribute='implementer') | unique | sort %}[{{ impl }}](by-implementer/{{ impl | lower | replace(' ', '-') | replace('/', '-') }}/){.gks-chip} {% endfor %}

## Catalog

{% for v in vignettes %}

### [{{ v.title }}]({{ v._path }}) <span class="gks-status gks-status--{{ v.status }}">{{ v.status }}</span>

**{{ v.implementer }}** · {% for p in v.products %}{{ p.name }}{% if p.version %} {{ p.version }}{% endif %}{% if not loop.last %}, {% endif %}{% endfor %} · _{{ v.pattern }}_

{{ v.summary }}

[Read →]({{ v._path }})

---

{% endfor %}

{% endif %}
