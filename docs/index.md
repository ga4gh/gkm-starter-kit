---
title: Genomic Knowledge Model (GKM) Starter Kit
---

# <span class="gks-home-title-full">Genomic Knowledge Model (GKM) Starter Kit</span><span class="gks-home-title-short">GKM Starter Kit</span>

Genomic knowledge is hard to share when every resource describes it
differently. The **[GA4GH Genomic Knowledge Model
(GKM)](about.md#what-is-gkm)** defines standards for representing genomic
knowledge consistently, and the **[Starter
Kit](about.md#the-three-pillars)** helps communities put those standards
to work with real data, software, and use cases. Together, they make genomic
knowledge from different resources easier to compare, combine, and apply.

The Starter Kit is organized around three pillars. **Data** covers how genomic
knowledge is accessed, packaged, and delivered in GKM-standard ways. **Tooling**
is the GKM toolkit used to validate and work with data in GKM-standard formats.
**User stories** gather live production and pre-production implementations of
GKM, explaining the value each project gained by adopting it.

<figure class="gks-explainer" role="group" aria-label="How the GKM Starter Kit fits together">
<svg class="wb wb--wide" viewBox="0 0 680 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Three cards - Data, Tooling and User stories - standing side by side on a workbench labelled 'Built on GKM standards'. The same three coloured blocks appear in each card: loose in a parts bin under Data, worked by a wrench and screwdriver under Tooling, and assembled with a verified badge under User stories.">
<title>How the GKM Starter Kit fits together</title>
<text class="wb-kicker" x="340.0" y="24" text-anchor="middle">GKM STARTER KIT</text>
<text class="wb-h1" x="340.0" y="58" text-anchor="middle">Three pillars, one shared foundation</text>
<text class="wb-sub" x="340.0" y="82" text-anchor="middle">So genomic knowledge can be compared, combined, and applied.</text>
<line class="wb-thread" x1="223.66666666666666" y1="160" x2="231.66666666666666" y2="160"/>
<line class="wb-thread" x1="448.3333333333333" y1="160" x2="456.3333333333333" y2="160"/>
<rect class="wb-card" x="10.0" y="104" width="210.66666666666666" height="164" rx="13"/><path class="wb-cap1" d="M 23.0 105 H 207.66666666666666 A 12 12 0 0 1 219.66666666666666 117 V 110 H 11.0 V 117 A 12 12 0 0 1 23.0 105 Z"/><rect class="wb-cap1" x="11.0" y="105" width="208.66666666666666" height="6"/>
<g transform="translate(115.33333333333333,160) scale(0.72)"><path class="wb-p1s" d="M -64 -41 L -64 27 A 14 14 0 0 0 -50 41 L 50 41 A 14 14 0 0 0 64 27 L 64 -41"/><rect class="wb-p1" x="-50" y="5" width="32" height="32" rx="7"/><rect class="wb-p2" x="-16" y="5" width="32" height="32" rx="7"/><rect class="wb-p3" x="18" y="5" width="32" height="32" rx="7"/></g>
<text class="wb-title" x="115.33333333333333" y="216" text-anchor="middle">Data</text>
<text class="wb-desc" x="115.33333333333333" y="244" text-anchor="middle">Package &amp; deliver</text>
<rect class="wb-card" x="234.66666666666666" y="104" width="210.66666666666666" height="164" rx="13"/><path class="wb-cap2" d="M 247.66666666666666 105 H 432.3333333333333 A 12 12 0 0 1 444.3333333333333 117 V 110 H 235.66666666666666 V 117 A 12 12 0 0 1 247.66666666666666 105 Z"/><rect class="wb-cap2" x="235.66666666666666" y="105" width="208.66666666666666" height="6"/>
<g transform="translate(340.0,160) scale(0.72)"><g transform="translate(-22,13) rotate(-32)"><rect class="wb-p2" x="-6" y="-20" width="12" height="52" rx="6"/><circle class="wb-p2s" cx="0" cy="-32" r="17"/><polygon class="wb-knock" points="-10,-58 10,-58 0,-34"/></g><g transform="translate(24,13) rotate(32)"><rect class="wb-p1" x="-9" y="-2" width="18" height="34" rx="7"/><rect class="wb-p3" x="-4" y="-34" width="8" height="34"/><rect class="wb-p3" x="-6" y="-40" width="12" height="8" rx="2"/></g></g>
<text class="wb-title" x="340.0" y="216" text-anchor="middle">Tooling</text>
<text class="wb-desc" x="340.0" y="244" text-anchor="middle">Validate &amp; use</text>
<rect class="wb-card" x="459.3333333333333" y="104" width="210.66666666666666" height="164" rx="13"/><path class="wb-cap3" d="M 472.3333333333333 105 H 657.0 A 12 12 0 0 1 669.0 117 V 110 H 460.3333333333333 V 117 A 12 12 0 0 1 472.3333333333333 105 Z"/><rect class="wb-cap3" x="460.3333333333333" y="105" width="208.66666666666666" height="6"/>
<g transform="translate(564.6666666666666,160) scale(0.72)"><rect class="wb-p1" x="-40" y="5" width="36" height="36" rx="8"/><rect class="wb-p2" x="4" y="5" width="36" height="36" rx="8"/><rect class="wb-p3" x="-18" y="-31" width="36" height="36" rx="8"/><circle class="wb-p3 wb-badge" cx="44" cy="-21" r="20"/><path class="wb-check" d="M 36 -21 l 6 6 l 11 -12"/></g>
<text class="wb-title" x="564.6666666666666" y="216" text-anchor="middle">User stories</text>
<text class="wb-desc" x="564.6666666666666" y="244" text-anchor="middle">Prove the value</text>
<rect class="wb-bench" x="4" y="268" width="672" height="40" rx="8"/>
<rect class="wb-bench" x="4" y="298" width="672" height="10"/>
<rect class="wb-apron" x="18" y="308" width="644" height="10" rx="5"/>
<rect class="wb-apron" x="18" y="308" width="644" height="8"/>
<text class="wb-bench-txt" x="340.0" y="293" text-anchor="middle">Built on GKM standards &#8212; one shared way to represent genomic knowledge</text>
<rect class="wb-apron" x="92" y="318" width="44" height="26" rx="5"/>
<rect class="wb-apron" x="92" y="318" width="44" height="10"/>
<rect class="wb-apron" x="544" y="318" width="44" height="26" rx="5"/>
<rect class="wb-apron" x="544" y="318" width="44" height="10"/>
</svg>
<svg class="wb wb--narrow" viewBox="0 0 460 648" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Three cards - Data, Tooling and User stories - standing side by side on a workbench labelled 'Built on GKM standards'. The same three coloured blocks appear in each card: loose in a parts bin under Data, worked by a wrench and screwdriver under Tooling, and assembled with a verified badge under User stories.">
<title>How the GKM Starter Kit fits together</title>
<text class="wb-kicker" x="230.0" y="26" text-anchor="middle">GKM STARTER KIT</text>
<text class="wb-h1 wb-h1--sm" x="230.0" y="60" text-anchor="middle">Three pillars,</text>
<text class="wb-h1 wb-h1--sm" x="230.0" y="90" text-anchor="middle">one shared foundation</text>
<text class="wb-sub wb-sub--sm" x="230.0" y="116" text-anchor="middle">So genomic knowledge can be compared,</text>
<text class="wb-sub wb-sub--sm" x="230.0" y="136" text-anchor="middle">combined, and applied.</text>
<rect class="wb-card" x="16" y="156" width="428" height="116" rx="13"/><path class="wb-cap1" d="M 29 157 H 431 A 12 12 0 0 1 443 169 V 162 H 17 V 169 A 12 12 0 0 1 29 157 Z"/><rect class="wb-cap1" x="17" y="157" width="426" height="6"/>
<g transform="translate(86,214) scale(0.86)"><path class="wb-p1s" d="M -64 -41 L -64 27 A 14 14 0 0 0 -50 41 L 50 41 A 14 14 0 0 0 64 27 L 64 -41"/><rect class="wb-p1" x="-50" y="5" width="32" height="32" rx="7"/><rect class="wb-p2" x="-16" y="5" width="32" height="32" rx="7"/><rect class="wb-p3" x="18" y="5" width="32" height="32" rx="7"/></g>
<text class="wb-title wb-title--sm" x="152" y="208">Data</text>
<text class="wb-desc wb-desc--sm" x="152" y="236">Package &amp; deliver</text>
<line class="wb-thread" x1="86" y1="275" x2="86" y2="283"/>
<rect class="wb-card" x="16" y="286" width="428" height="116" rx="13"/><path class="wb-cap2" d="M 29 287 H 431 A 12 12 0 0 1 443 299 V 292 H 17 V 299 A 12 12 0 0 1 29 287 Z"/><rect class="wb-cap2" x="17" y="287" width="426" height="6"/>
<g transform="translate(86,344) scale(0.86)"><g transform="translate(-22,13) rotate(-32)"><rect class="wb-p2" x="-6" y="-20" width="12" height="52" rx="6"/><circle class="wb-p2s" cx="0" cy="-32" r="17"/><polygon class="wb-knock" points="-10,-58 10,-58 0,-34"/></g><g transform="translate(24,13) rotate(32)"><rect class="wb-p1" x="-9" y="-2" width="18" height="34" rx="7"/><rect class="wb-p3" x="-4" y="-34" width="8" height="34"/><rect class="wb-p3" x="-6" y="-40" width="12" height="8" rx="2"/></g></g>
<text class="wb-title wb-title--sm" x="152" y="338">Tooling</text>
<text class="wb-desc wb-desc--sm" x="152" y="366">Validate &amp; use</text>
<line class="wb-thread" x1="86" y1="405" x2="86" y2="413"/>
<rect class="wb-card" x="16" y="416" width="428" height="116" rx="13"/><path class="wb-cap3" d="M 29 417 H 431 A 12 12 0 0 1 443 429 V 422 H 17 V 429 A 12 12 0 0 1 29 417 Z"/><rect class="wb-cap3" x="17" y="417" width="426" height="6"/>
<g transform="translate(86,474) scale(0.86)"><rect class="wb-p1" x="-40" y="5" width="36" height="36" rx="8"/><rect class="wb-p2" x="4" y="5" width="36" height="36" rx="8"/><rect class="wb-p3" x="-18" y="-31" width="36" height="36" rx="8"/><circle class="wb-p3 wb-badge" cx="44" cy="-21" r="20"/><path class="wb-check" d="M 36 -21 l 6 6 l 11 -12"/></g>
<text class="wb-title wb-title--sm" x="152" y="468">User stories</text>
<text class="wb-desc wb-desc--sm" x="152" y="496">Prove the value</text>
<rect class="wb-bench" x="8" y="532" width="444" height="62" rx="8"/>
<rect class="wb-bench" x="8" y="584" width="444" height="10"/>
<rect class="wb-apron" x="22" y="594" width="416" height="10" rx="5"/>
<rect class="wb-apron" x="22" y="594" width="416" height="8"/>
<text class="wb-bench-txt wb-bench-txt--sm" x="230.0" y="558" text-anchor="middle">Built on GKM standards</text>
<text class="wb-bench-sub" x="230.0" y="580" text-anchor="middle">one shared way to represent genomic knowledge</text>
<rect class="wb-apron" x="50" y="604" width="46" height="26" rx="5"/>
<rect class="wb-apron" x="50" y="604" width="46" height="10"/>
<rect class="wb-apron" x="364" y="604" width="46" height="26" rx="5"/>
<rect class="wb-apron" x="364" y="604" width="46" height="10"/>
</svg>
</figure>

## What do you want to do?

<div class="grid cards" markdown>

- :material-database: **I have data to share**

    Package your GKM data so others can use it with the Starter Kit.

    [Explore data →](data/index.md)

- :material-code-braces: **I want to build**

    Load bundles, explore their contents, and follow relationships.

    [Explore the GKM toolkit →](library/index.md)

- :material-rocket-launch: **I have a project**

    See how live and pre-production projects adopted GKM and the value they gained.

    [Browse the user stories →](vignettes/index.md)

</div>
