---
title: Sharing oncogenicity knowledge with GA4GH GKM
slug: civic-oncogenicity-gkm
summary: "CIViC represents oncogenicity classifications and their supporting evidence with GA4GH GKM for exchange, reuse, and workflows such as ClinVar submission."
products:
  - name: GKS-Core
    version: 1.1.0
  - name: VRS
    version: 2.1.0-snapshot.2026-02.2
  - name: Cat-VRS
    version: 1.1.0-snapshot.2026-02.3
  - name: VA-Spec
    version: 1.1.0-snapshot.2026-06.1
pattern: knowledgebase-exchange
implementer: CIViC
notebook:
  path: civic/civic-oncogenicity-gkm/notebook.md
status: pilot
last_updated: 2026-09
---

# Sharing oncogenicity knowledge with GA4GH GKM

**Why this matters**

[Clinical Interpretation of Variants in Cancer (CIViC)](https://civicdb.org/welcome) is a public, community-driven knowledgebase for curating evidence about how genomic variants relate to cancer. It organizes that evidence into interpretations, including oncogenicity classifications, that researchers and clinical applications can review and reuse.

CIViC curates oncogenicity classifications and their supporting evidence. To use a classification outside CIViC, another system needs its variant, claim, supporting evidence, and provenance. The GA4GH Genomic Knowledge Model provides a common, computable representation for these connected records so interpretations retain their meaning across systems and can support workflows such as ClinVar submission.

**At a glance**

* **Implementer:** CIViC
* **Products:** <span class="gks-product-label gks-product-label--gks-core">GKS-Core <small>1.1.0</small></span> <span class="gks-product-label gks-product-label--vrs">VRS <small>2.1.0-snapshot.2026-02.2</small></span> <span class="gks-product-label gks-product-label--cat-vrs">Cat-VRS <small>1.1.0-snapshot.2026-02.3</small></span> <span class="gks-product-label gks-product-label--va-spec">VA-Spec <small>1.1.0-snapshot.2026-06.1</small></span>
* **Pattern:** Knowledgebase exchange
* **Tools:** [CIViCpy](https://github.com/griffithlab/civicpy), [ClinVar This](https://github.com/clingen-data-model/clinvar-this)
* **Notebook:** [Explore the example](../notebook.md)
* **Status:** <span class="gks-status gks-status--pilot">pilot</span>

---

## The challenge

CIViC curators use the ClinGen/CGC/VICC framework to classify whether somatic variants may contribute to cancer. An interpretation combines a variant and disease context with evidence evaluated against oncogenicity criteria. It produces classifications such as *Oncogenic*, *Likely Oncogenic*, or *Uncertain Significance*, plus the supporting evidence and provenance needed to interpret the result.

CIViC and other resources represent variants, evidence, assertions, and curation provenance differently. Without GKM, every destination needs a CIViC-specific transformation. Each integration must then account for both data models, limiting reuse of the structured interpretation.

## What GKM enables for CIViC

CIViCpy maps CIViC records, including Variants, Molecular Profiles, Evidence Items, and Assertions, into GKM-formatted data. Cat-VRS represents CIViC Molecular Profiles as CategoricalVariants. VRS represents the sequence-level variation within their CIViC Variant contexts. VA-Spec represents claims made by Evidence Items and Assertions, with their classifications, evidence assessments, supporting documents, and provenance.

This gives CIViC one shared representation instead of a separate CIViC-specific transformation for each downstream workflow. The data can be serialized as JSON for exchange. For example, [ClinVar This](https://github.com/clingen-data-model/clinvar-this) can use GKM-formatted JSON to prepare and track ClinVar submissions. Other GKM-capable applications can use the same linked claim, classification, evidence, and provenance without implementing CIViC's internal data model.

## The data

CIViCpy represents an oncogenicity interpretation as connected GKM objects: Cat-VRS for the molecular profile, VRS for the underlying alleles, and VA-Spec for the proposition, assertion, evidence assessments, and provenance. This preserves the links between the variant, its context, the classification, and its evidence. The following shortened example is adapted from [CIViC Assertion 251](../../../data/bundles/civic-assertion-251-bundle.json){ target="_blank" rel="noopener" }. The linked bundle contains the full record.

### Connected GKM representation

The example places the Molecular Profile, claim, source document, and assertion in one connected representation. The sections that follow explain the most important relationships in the JSON.

```json
{
  "molecularProfile": {
    "civic.mpid:82": {
      "type": "CategoricalVariant",
      "name": "MAP2K1 P124S",
      "members": [
        "#/variant/civic.vid:82/genomic/ga4gh:VA.5tTLvjSAjWhE0tW_z0aAzsk5WlWKZrCR", // NC_000015.9:g.66729162C>T
        "#/variant/civic.vid:82/coding/ga4gh:VA.fcZSo_OetJhIFnc6fx5LC6oPVQZZA9MR", // NM_002755.3:c.370C>T
        "#/variant/civic.vid:82/protein/ga4gh:VA.gI5daa-xbJJEiE4IAXyJUjJRgI-DYK8u" // NP_002746.1:p.Pro124Ser
      ]
    }
  },
  "proposition": {
    "civic.proposition:1VqM04P0kzvUa1aj63ujSB9DGZNFDyE4": {
      "type": "VariantOncogenicityProposition",
      "subjectVariant": "#/molecularProfile/civic.mpid:82",
      "geneContextQualifier": "#/feature/civic.gid:31", // MAP2K1
      "alleleOriginQualifier": "#/variantOrigin/civic.variantOrigin:SOMATIC",
      "predicate": "isOncogenicFor",
      "objectTumorType": "#/disease/civic.did:216" // Cancer
    }
  },
  "source": {
    "civic.sid:5629": {
      "id": "civic.sid:5629",
      "type": "Document",
      "name": "Nikolaev et al., 2011",
      "title": "Exome sequencing identifies recurrent somatic MAP2K1 and MAP2K2 mutations in melanoma.",
      "urls": [
        "https://civicdb.org/links/evidence/12986", // CIViC Evidence Item
        "https://civicdb.org/links/source/5629",
        "http://www.ncbi.nlm.nih.gov/pubmed/22197931"
      ],
      "pmid": "22197931"
    }
  },
  "assertion": {
    "civic.aid:251": {
      "type": "Statement",
      "proposition": "#/proposition/civic.proposition:1VqM04P0kzvUa1aj63ujSB9DGZNFDyE4",
      "classification": {
        "primaryCoding": {
          "system": "ClinGen/CGC/VICC Guidelines for Oncogenicity, 2022",
          "code": "likely oncogenic"
        }
      },
      "reportedIn": [
        "https://civicdb.org/links/assertion/251",
        "#/source/civic.sid:5629"
      ],
      "hasEvidenceLines": [
        { "evidenceOutcome": "OS2", "scoreOfEvidenceProvided": 4, ... },
        { "evidenceOutcome": "OM3", "scoreOfEvidenceProvided": 2, ... },
        { "evidenceOutcome": "OP4", "scoreOfEvidenceProvided": 1, ... }
      ]
    }
  }
}
```

### Storing the molecular profile and its variant context

CIViCpy represents the CIViC Molecular Profile as the Cat-VRS CategoricalVariant `civic.mpid:82`. It retains the profile's grouping of one or more CIViC Variants and serves as the proposition's `subjectVariant`.

CIViC stores the genomic, coding, and protein sequence representations under one CIViC Variant ID. In this example, each `members` path begins with `civic.vid:82`. The CategoricalVariant preserves that context through VRS Allele members, each with a precise, computable representation.

### Classification rationale and sources

Together, these objects form a reusable statement: Somatic **RET M918T is likely oncogenic for Medullary Thyroid Carcinoma**, evaluated under the ClinGen/CGC/VICC Guidelines for Oncogenicity, 2022 framework. The classification has a score of 9 and is supported by functional domain location (OM1), functional assay (OS2), population frequency (OP4), computational prediction (OP1), somatic hotspot recurrence (OP3) evidence.

CIViC stores oncogenicity codes on the assertion, but does not link each code to an Evidence Item. Curators may mention both in free text, for example `(civic.EID:12709, OS2)`, but conventions vary. CIViCpy cannot reliably infer those links, so `EvidenceLine.hasEvidenceItems` is empty. The Evidence Item URL (`https://civicdb.org/links/evidence/12986`) remains in the source document referenced by `Statement.reportedIn`.

## The tools used

* [CIViC](https://civicdb.org/): source knowledgebase for curated cancer variant evidence and oncogenicity classifications.
* [CIViCpy](https://github.com/griffithlab/civicpy): maps CIViC entities into GKM representations.
* [ClinVar This](https://github.com/clingen-data-model/clinvar-this): an example application that uses GKM representations to support ClinVar submission and tracking.

## Explore the example

The accompanying [CIViC oncogenicity notebook](../notebook.md) walks through
the same interpretation in executable Python. Use it as a starting point for
loading CIViC data, following its linked records, and preparing a connected
representation for your own application.
