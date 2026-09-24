---
title: "Making personal genomic knowledge auditable so AI can be trusted, not just believed"
slug: auditable-personal-genomic-knowledge
summary: "Individual-Centric Genomics Platform JPN uses VRS, Cat-VRS, and VA-Spec to make personal genomic knowledge traceable and auditable for people and AI tools."
products:
  - name: VRS
    version: "2.0"
  - name: Cat-VRS
    version: "1.0"
  - name: VA-Spec
    version: "1.0"
pattern: clinical-evidence-sharing
implementer: "Individual-Centric Genomics Platform JPN"
status: proposal
last_updated: 2026-07-01
---

# Making personal genomic knowledge auditable so AI can be trusted, not just believed

**Why this matters**

As individuals increasingly own their genomic data, that data can often reach them as flat, fragmented files such as raw VCFs, CSV spreadsheets, and prose reports, with no shared identity across sources and no evidence structure. Tech-literate consumers, patient advocates, and busy clinicians understandably reach for general-purpose AI to interpret these files. This shift deserves support rather than restriction, but it carries a human blind spot: unstructured input lets a model produce fluent, plausible, yet incorrect conclusions with nothing to check them against. GKS unlocks a structured layer beneath that interpretation: VRS gives every variant a stable, content-addressed identity; Cat-VRS places each variant into computable categories defined by shared properties, so category-level knowledge attaches correctly; and VA-Spec records what is claimed about a variant as statements backed by nested evidence lines, each carrying an explicit strength, confidence, and provenance. The framework does not decide for the reader. It exposes the chain of evidence and how strong it is, so a person or a downstream reasoning tool can check any AI-generated summary against the underlying statements rather than trusting prose alone. The immediate payoff is a more reproducible, auditable path through the rare-disease diagnostic odyssey, and the same structure carries over to pharmacogenomics and polygenic scores while providing a semantic foundation for secure, federated reuse without redundant re-interpretation.

**At a glance**

- **Implementer:** Individual-Centric Genomics Platform JPN
- **Products:** <span class="gks-product-label gks-product-label--vrs">VRS <small>2.0</small></span> <span class="gks-product-label gks-product-label--cat-vrs">Cat-VRS <small>1.0</small></span> <span class="gks-product-label gks-product-label--va-spec">VA-Spec <small>1.0</small></span>
- **Pattern:** Clinical evidence sharing
- **Tools:** [VRS-Python](https://github.com/ga4gh/vrs-python)
- **Status:** <span class="gks-status gks-status--proposal">proposal</span>

---

## The story

Genomic information belongs to the individual, and whether a person is currently a "patient" or a "healthy consumer" is largely a matter of timing. As ownership of genomic data shifts to the person, the right response to the resulting turn toward AI is not to hold that shift back. It is to build a framework, together with the people it serves, in which anyone can engage with their own genomic data on their own terms without being misled.

Doing so means taking one human blind spot seriously. The danger is not that an AI refuses to answer; it is that it answers fluently and wrongly, and that the people most comfortable with these tools are often the least likely to catch it. Given unstructured input, a model has nothing to check itself against, and the risk tends to be greatest where the input is least structured. Placing a verifiable layer before interpretation is what begins to change this.

This pilot builds that layer using three GKS standards in combination. VRS establishes a stable identity for each variant, Cat-VRS situates it within computable categories so that curated category-level knowledge attaches to the individual's variant, and VA-Spec records the resulting claims as statements supported by nested evidence lines, each with an explicit strength, confidence, and provenance. As a worked example, a heterozygous APOB variant is asserted to carry pathogenic status for familial hypobetalipoproteinemia, supported by the combination of the sequencing result, the variant's category, the reported gene and disease association, the pathogenicity report, and the variant's rarity, with the overall claim carrying a stated strength and confidence rather than an unqualified verdict.

This restraint is deliberate: the framework does not collapse the evidence into a single answer. It keeps the strength and provenance of every claim visible, so that any natural-language summary can be checked against the structured statements behind it. This is what lets a person engage with their data without being misled: a claim can be trusted because its basis can be traced, not merely believed. The sensitive profile can stay secured locally, while this structured layer supplies the common semantics that, combined with other GA4GH frameworks, could then let knowledge be reused across networks without being interpreted from scratch each time. The rare-disease diagnostic odyssey is the primary example, and the same architecture extends to pharmacogenomics and polygenic scores.

## The tools used

- [VRS-Python](https://github.com/ga4gh/vrs-python)

## Relevant links

- [Cat-VRS](https://doi.org/10.64898/2026.02.10.705161)
- [VA-Spec](https://va-spec.ga4gh.org/en/latest/index.html)
- [Individual-Centric Genomics Platform JPN: A 2025 Implementation Progress Report](https://zenodo.org/records/18371935)
