# Terminology

The public API uses a small bakery vocabulary and provides conventional aliases
for themed operations:

| Name | Alias | Description | Bakery or bun meaning |
| --- | --- | --- | --- |
| `gkm.starter` | — | The package namespace for loading and working with GKM Bundles. | A starter is the culture that helps dough rise. |
| `Bun` | GKM Bundle | One GKM Bundle loaded in memory. | A bun is the finished unit produced from the starter. |
| `BunCatalog` | — | A catalog of named bun registrations available for loading. | A bakery catalog lists the buns available by name. |
| `unwrap()` | `resolve()` | Follow one bun-local JSON Pointer and return its target. | Unwrapping exposes the object held inside a bun-local reference. |
| `unwrap_all()` | `dereference()` | Inline every reachable bun-local reference, except pointers that close cycles. | Removing all wrapping exposes the bun's reachable contents. |
| `bake()` | `write()` | Serialize the current bun to a JSON file. | Baking produces the finished bun that is ready to distribute. |

The bakery name is the branded API; the alias communicates the conventional
software operation.
