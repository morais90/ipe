---
name: openapi-spec
description: >
  Complete OpenAPI 3.0.3 and 3.1.0 specification reference. Use when building
  or modifying the OpenAPI parser, models, validator, or resolver. Contains all
  objects, fields, types, constraints, and version differences.
user-invocable: true
---

# OpenAPI Specification Reference

Ipê supports OpenAPI 3.0.x (3.0.0–3.0.3) and 3.1.x (3.1.0+). Swagger 2.0 is rejected.

Internal model is based on **3.1.0** (the superset). When parsing 3.0.x, normalize to 3.1.0.

## Data Types

| type | format | Notes |
|------|--------|-------|
| `integer` | `int32` | Signed 32 bits |
| `integer` | `int64` | Signed 64 bits |
| `number` | `float` | |
| `number` | `double` | |
| `string` | — | Plain string |
| `string` | `byte` | Base64 (3.0.x); use `contentEncoding` in 3.1.x |
| `string` | `binary` | Octet stream |
| `string` | `date` | RFC3339 full-date |
| `string` | `date-time` | RFC3339 date-time |
| `string` | `password` | UI hint |
| `string` | `uuid` | Common extension |
| `string` | `email` | Common extension |
| `boolean` | — | |
| `null` | — | **3.1.x only** as standalone type |

---

## Objects

Legend: **R** = Required, **O** = Optional, **C** = Conditional

### OpenAPI Object (root)

| Field | Type | 3.0 | 3.1 | Notes |
|-------|------|-----|-----|-------|
| `openapi` | string | **R** | **R** | Semver: `"3.0.3"` or `"3.1.0"` |
| `info` | Info | **R** | **R** | |
| `servers` | [Server] | O | O | Default: `[{url: "/"}]` |
| `paths` | Paths | **R** | O | 3.1: must have ≥1 of paths/components/webhooks |
| `components` | Components | O | O | |
| `security` | [SecurityRequirement] | O | O | Global; ops can override |
| `tags` | [Tag] | O | O | Names must be unique |
| `externalDocs` | ExternalDocs | O | O | |
| `jsonSchemaDialect` | string | — | O | **3.1 only.** Default schema dialect URI |
| `webhooks` | Map[string, PathItem\|Ref] | — | O | **3.1 only.** Incoming webhooks |

### Info Object

| Field | Type | 3.0 | 3.1 |
|-------|------|-----|-----|
| `title` | string | **R** | **R** |
| `summary` | string | — | O | **3.1 only** |
| `description` | string | O | O |
| `termsOfService` | string (URL) | O | O |
| `contact` | Contact | O | O |
| `license` | License | O | O |
| `version` | string | **R** | **R** |

### Contact Object

| Field | Type | Req |
|-------|------|-----|
| `name` | string | O |
| `url` | string (URL) | O |
| `email` | string (email) | O |

### License Object

| Field | Type | 3.0 | 3.1 | Notes |
|-------|------|-----|-----|-------|
| `name` | string | **R** | **R** | |
| `url` | string (URL) | O | O | 3.1: mutually exclusive with `identifier` |
| `identifier` | string | — | O | **3.1 only.** SPDX expression |

### Server Object

| Field | Type | Req |
|-------|------|-----|
| `url` | string | **R** | Supports `{variables}`; may be relative |
| `description` | string | O |
| `variables` | Map[string, ServerVariable] | O |

### Server Variable Object

| Field | Type | Req |
|-------|------|-----|
| `enum` | [string] | O | Should not be empty |
| `default` | string | **R** | Must be in enum if enum exists |
| `description` | string | O |

### Components Object

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `schemas` | Map[string, Schema\|Ref] | O | |
| `responses` | Map[string, Response\|Ref] | O | |
| `parameters` | Map[string, Parameter\|Ref] | O | |
| `examples` | Map[string, Example\|Ref] | O | |
| `requestBodies` | Map[string, RequestBody\|Ref] | O | |
| `headers` | Map[string, Header\|Ref] | O | |
| `securitySchemes` | Map[string, SecurityScheme\|Ref] | O | |
| `links` | Map[string, Link\|Ref] | O | |
| `callbacks` | Map[string, Callback\|Ref] | O | |
| `pathItems` | Map[string, PathItem\|Ref] | — | **3.1 only** |

Key names must match `^[a-zA-Z0-9\.\-_]+$`.

### Paths Object

Patterned field: `/{path}` → PathItem. Path must begin with `/`. Concrete paths match before templated.

### Path Item Object

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `$ref` | string | O | External path item ref |
| `summary` | string | O | Applies to all ops |
| `description` | string | O | |
| `get` | Operation | O | |
| `put` | Operation | O | |
| `post` | Operation | O | |
| `delete` | Operation | O | |
| `options` | Operation | O | |
| `head` | Operation | O | |
| `patch` | Operation | O | |
| `trace` | Operation | O | |
| `servers` | [Server] | O | |
| `parameters` | [Parameter\|Ref] | O | Unique by name+location |

### Operation Object

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `tags` | [string] | O | Grouping |
| `summary` | string | O | |
| `description` | string | O | |
| `externalDocs` | ExternalDocs | O | |
| `operationId` | string | O | Must be unique across entire API |
| `parameters` | [Parameter\|Ref] | O | Overrides path-level |
| `requestBody` | RequestBody\|Ref | O | |
| `responses` | Responses | **R** | |
| `callbacks` | Map[string, Callback\|Ref] | O | |
| `deprecated` | boolean | O | Default: false |
| `security` | [SecurityRequirement] | O | Overrides global; `[]` removes |
| `servers` | [Server] | O | |

### Parameter Object

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `name` | string | **R** | Case-sensitive |
| `in` | string | **R** | `query`, `header`, `path`, `cookie` |
| `description` | string | O | |
| `required` | boolean | **C** | **Must be true** for `in=path`; default false |
| `deprecated` | boolean | O | Default: false |
| `allowEmptyValue` | boolean | O | Query only; NOT RECOMMENDED |
| `style` | string | O | Default: query=`form`, path=`simple`, header=`simple`, cookie=`form` |
| `explode` | boolean | O | Default: true for `form`, false otherwise |
| `allowReserved` | boolean | O | Query only; default false |
| `schema` | Schema\|Ref | O | Must have `schema` XOR `content` |
| `example` | Any | O | Mutually exclusive with `examples` |
| `examples` | Map[string, Example\|Ref] | O | |
| `content` | Map[string, MediaType] | O | Exactly 1 entry; alternative to schema |

**Style values:** `matrix` (path), `label` (path), `form` (query/cookie), `simple` (path/header), `spaceDelimited` (query), `pipeDelimited` (query), `deepObject` (query).

### Request Body Object

| Field | Type | Req |
|-------|------|-----|
| `description` | string | O |
| `content` | Map[string, MediaType] | **R** |
| `required` | boolean | O | Default: false |

### Media Type Object

| Field | Type | Req |
|-------|------|-----|
| `schema` | Schema\|Ref | O |
| `example` | Any | O | Mutually exclusive with `examples` |
| `examples` | Map[string, Example\|Ref] | O |
| `encoding` | Map[string, Encoding] | O | Only for multipart/form-urlencoded |

### Encoding Object

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `contentType` | string | O | Default depends on property type |
| `headers` | Map[string, Header\|Ref] | O | Multipart only |
| `style` | string | O | Form-urlencoded only |
| `explode` | boolean | O | |
| `allowReserved` | boolean | O | |

### Responses Object

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `default` | Response\|Ref | O | Fallback |
| `{HTTP status}` | Response\|Ref | O | `"200"`, `"404"`, ranges: `1XX`–`5XX` |

Must have ≥1 response. Explicit codes > ranges.

### Response Object

| Field | Type | Req |
|-------|------|-----|
| `description` | string | **R** |
| `headers` | Map[string, Header\|Ref] | O |
| `content` | Map[string, MediaType] | O |
| `links` | Map[string, Link\|Ref] | O |

### Header Object

Same as Parameter Object, but `name` and `in` must NOT be specified (implicit from map key and `header` location). Style default: `simple`.

### Tag Object

| Field | Type | Req |
|-------|------|-----|
| `name` | string | **R** |
| `description` | string | O |
| `externalDocs` | ExternalDocs | O |

### Reference Object

| Field | Type | 3.0 | 3.1 | Notes |
|-------|------|-----|-----|-------|
| `$ref` | string | **R** | **R** | JSON Reference pointer |
| `summary` | string | — | O | **3.1 only.** Overrides referenced component |
| `description` | string | — | O | **3.1 only.** Overrides referenced component |

**3.0.x:** All sibling properties to `$ref` MUST be ignored.
**3.1.x:** In Schema Objects, sibling keywords ARE applied alongside `$ref` (JSON Schema 2020-12).

### External Documentation Object

| Field | Type | Req |
|-------|------|-----|
| `description` | string | O |
| `url` | string (URL) | **R** |

### Example Object

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `summary` | string | O | |
| `description` | string | O | |
| `value` | Any | O | Mutually exclusive with `externalValue` |
| `externalValue` | string (URL) | O | |

### Link Object

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `operationRef` | string | O | Mutually exclusive with `operationId` |
| `operationId` | string | O | |
| `parameters` | Map[string, Any] | O | |
| `requestBody` | Any | O | |
| `description` | string | O | |
| `server` | Server | O | |

### Callback Object

Patterned field: `{runtime expression}` → PathItem. Expression can access request/response parts.

### Schema Object

**JSON Schema validation keywords (both versions):**

| Field | Type | Notes |
|-------|------|-------|
| `title` | string | |
| `description` | string | |
| `default` | Any | Must conform to type |
| `enum` | [Any] | Allowed values |
| `const` | Any | **3.1 only.** Single allowed value |
| `multipleOf` | number | > 0 |
| `maximum` | number | |
| `minimum` | number | |
| `maxLength` | integer | ≥ 0 |
| `minLength` | integer | ≥ 0, default 0 |
| `pattern` | string | Regex (ECMA-262) |
| `maxItems` | integer | ≥ 0 |
| `minItems` | integer | ≥ 0, default 0 |
| `uniqueItems` | boolean | Default: false |
| `maxProperties` | integer | ≥ 0 |
| `minProperties` | integer | ≥ 0, default 0 |
| `required` | [string] | Required property names |

**Type and composition:**

| Field | Type | 3.0 | 3.1 | Notes |
|-------|------|-----|-----|-------|
| `type` | string | string only | string \| [string] | 3.1: array allows `["string", "null"]` |
| `nullable` | boolean | O | — | **3.0 only.** Removed in 3.1; use type array |
| `allOf` | [Schema\|Ref] | O | O | Must match ALL |
| `oneOf` | [Schema\|Ref] | O | O | Must match EXACTLY ONE |
| `anyOf` | [Schema\|Ref] | O | O | Must match ≥1 |
| `not` | Schema\|Ref | O | O | Must NOT match |
| `items` | Schema\|Ref | O | O | 3.0: required if type=array. 3.1: single schema or bool |
| `prefixItems` | [Schema\|Ref] | — | O | **3.1 only.** Tuple validation (replaces items-as-array) |
| `properties` | Map[string, Schema\|Ref] | O | O | |
| `additionalProperties` | bool \| Schema\|Ref | O | O | Default: true |
| `if` / `then` / `else` | Schema\|Ref | — | O | **3.1 only.** Conditional |
| `dependentSchemas` | Map[string, Schema\|Ref] | — | O | **3.1 only** |
| `dependentRequired` | Map[string, [string]] | — | O | **3.1 only** |

**Exclusive bounds (VERSION DIFFERENCE):**

| Field | 3.0.x type | 3.1.x type | Normalization |
|-------|-----------|-----------|---------------|
| `exclusiveMinimum` | boolean | number | `{min: 0, exclusiveMin: true}` → `{exclusiveMin: 0}` |
| `exclusiveMaximum` | boolean | number | `{max: 100, exclusiveMax: true}` → `{exclusiveMax: 100}` |

**Format and content:**

| Field | Type | 3.0 | 3.1 | Notes |
|-------|------|-----|-----|-------|
| `format` | string | O | O | `int32`, `int64`, `float`, `double`, `date`, `date-time`, `password`, `byte`, `binary`, `email`, `uuid` |
| `contentEncoding` | string | — | O | **3.1 only.** e.g. `base64` |
| `contentMediaType` | string | — | O | **3.1 only** |
| `contentSchema` | Schema\|Ref | — | O | **3.1 only** |

**OAS-specific fields:**

| Field | Type | 3.0 | 3.1 | Notes |
|-------|------|-----|-----|-------|
| `discriminator` | Discriminator | O | O | For polymorphism with oneOf/anyOf/allOf |
| `readOnly` | boolean | O | O | Response only; default false |
| `writeOnly` | boolean | O | O | Request only; default false |
| `xml` | XML | O | O | |
| `externalDocs` | ExternalDocs | O | O | |
| `example` | Any | O | **Deprecated** | 3.1: use `examples: [Any]` (JSON Schema array) |
| `examples` | [Any] | — | O | **3.1 only.** JSON Schema examples (NOT OAS Example Objects) |
| `deprecated` | boolean | O | O | Default: false |

**3.1 JSON Schema keywords (additional):**

| Field | Notes |
|-------|-------|
| `$schema` | Dialect URI |
| `$id` | Schema identification / base URI |
| `$anchor` | Named anchor |
| `$defs` | Inline schema definitions |
| `$comment` | Informational |
| `$dynamicRef` / `$dynamicAnchor` | Recursive patterns |
| `$vocabulary` | Required/optional vocabularies |

### Discriminator Object

| Field | Type | Req |
|-------|------|-----|
| `propertyName` | string | **R** | Must be in `required` |
| `mapping` | Map[string, string] | O | Value → schema name or $ref |

### XML Object

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `name` | string | O | Element/attribute name override |
| `namespace` | string (URI) | O | Absolute URI |
| `prefix` | string | O | |
| `attribute` | boolean | O | Default: false |
| `wrapped` | boolean | O | Arrays only; default: false |

### Security Scheme Object

| Field | Type | Applies To | Req |
|-------|------|-----------|-----|
| `type` | string | All | **R** | `apiKey`, `http`, `mutualTLS` (3.1), `oauth2`, `openIdConnect` |
| `description` | string | All | O |
| `name` | string | apiKey | **R** | Header/query/cookie param name |
| `in` | string | apiKey | **R** | `query`, `header`, `cookie` |
| `scheme` | string | http | **R** | e.g. `bearer`, `basic` |
| `bearerFormat` | string | http(bearer) | O | |
| `flows` | OAuthFlows | oauth2 | **R** | |
| `openIdConnectUrl` | string (URL) | openIdConnect | **R** | |

**3.1 addition:** `mutualTLS` type (client certificate auth, no additional fields needed).

### OAuth Flows Object

| Field | Type | Req |
|-------|------|-----|
| `implicit` | OAuthFlow | O |
| `password` | OAuthFlow | O |
| `clientCredentials` | OAuthFlow | O |
| `authorizationCode` | OAuthFlow | O |

### OAuth Flow Object

| Field | Type | Applies To | Req |
|-------|------|-----------|-----|
| `authorizationUrl` | string (URL) | implicit, authorizationCode | **R** |
| `tokenUrl` | string (URL) | password, clientCredentials, authorizationCode | **R** |
| `refreshUrl` | string (URL) | All | O |
| `scopes` | Map[string, string] | All | **R** | May be empty |

### Security Requirement Object

Patterned field: `{scheme name}` → [string]. Key must match `components/securitySchemes`. Value is scopes array (empty for non-oauth). Multiple schemes in one object = AND. Multiple objects in array = OR. `{}` = optional.

---

## 3.0.x → 3.1.x Normalization Rules

Parser must normalize 3.0.x input to 3.1.0 internal representation:

| 3.0.x Input | Normalized Internal (3.1.0) |
|---|---|
| `nullable: true` + `type: T` | `type: [T, "null"]` |
| `exclusiveMinimum: true` + `minimum: N` | `exclusiveMinimum: N` (remove minimum) |
| `exclusiveMaximum: true` + `maximum: N` | `exclusiveMaximum: N` (remove maximum) |
| `example: X` on Schema | `examples: [X]` |
| `$ref` with sibling props (Schema) | Strip siblings (3.0 rule) |
| `items: [A, B]` (tuple) | `prefixItems: [A, B]` |
| `format: byte` | Consider `contentEncoding: base64` |
| `paths` required | Validate presence |

### Structural Differences Summary

| Feature | 3.0.x | 3.1.x |
|---------|-------|-------|
| `paths` | Required | Optional (need paths OR components OR webhooks) |
| `webhooks` | Not available | Top-level object |
| `pathItems` in Components | Not available | Available |
| Info `summary` | Not available | Optional field |
| License `identifier` | Not available | SPDX expression (XOR with url) |
| `jsonSchemaDialect` | Not available | Root-level dialect URI |
| `$ref` summary/description | Not allowed | Override referenced component |
| `$ref` siblings in Schema | Ignored | Applied (JSON Schema 2020-12) |
| `mutualTLS` security type | Not available | Available |
| Schema `nullable` | Boolean field | Not available (use type array) |
| Schema `type` | String only | String or array of strings |
| Schema `exclusiveMin/Max` | Boolean modifier | Number value |
| Schema `example` | Standard | Deprecated (use `examples` array) |
| Schema `const` | Not available | Available |
| Schema `if/then/else` | Not available | Available |
| Schema `$defs` | Not available | Available |
| Schema `prefixItems` | Not available | Tuple validation |
| Schema boolean values | Not valid | `true`/`false` as schemas |

### Priority for Ipê v0.1

**Must implement:**
- Type arrays + nullable normalization
- exclusiveMin/Max normalization
- `$ref` sibling behavior per version
- Version detection (3.0.x vs 3.1.x vs Swagger 2.0)
- All objects listed above with required field validation

**Deferred (future):**
- webhooks, callbacks, links
- `discriminator` mapping
- `if/then/else`, `$defs`, `$dynamicRef`
- Multi-file `$ref` (relative/remote)
- XML Object
- `contentEncoding`/`contentMediaType`/`contentSchema`

---

## Specification Extensions

All objects (except Reference and SecurityRequirement) accept `x-` prefixed fields. In 3.1.x Schema Objects, non-`x-` additional properties are also valid (full JSON Schema).
