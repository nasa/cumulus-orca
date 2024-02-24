---
id: documentation-style-guide
title: Documentation Style Guide
description: Provide markdown guidance for ORCA documentation.
---

You can write markdown content using the [GitHub-flavored Markdown syntax](https://github.github.com/gfm/).
The sections below provide brief highlights on writing key markdown syntax with
examples.

## Markdown Syntax

The following sections detail how to use various markdown syntax.


## Headers

Headers are used to identify various broad sections in and environment. Docusaurus
uses headings to create a table of contents for the page. Since the *title metadata*
of the page is expected as part of creating a page, heading 2 `## H2` should be used
to identify main sections instead of heading 1 `# H1` on documentation pages.

Sections can be nested as seen below.

```md
# H1 - Create the best documentation

## H2 - Create the best documentation

### H3 - Create the best documentation

#### H4 - Create the best documentation

##### H5 - Create the best documentation

###### H6 - Create the best documentation
```

# H1 - Create the best documentation

## H2 - Create the best documentation

### H3 - Create the best documentation

#### H4 - Create the best documentation

##### H5 - Create the best documentation

###### H6 - Create the best documentation

---

## Emphasis

Emphasis, aka italics, with *asterisks* `*asterisks*` or _underscores_ `_underscores_`.

Strong emphasis, aka bold, with **double asterisks** `**double asterisks**` or
__double underscores__ `__double underscores__`.

Combined emphasis with **both asterisks and _underscores_** `**both asterisks and _underscores_**`.

Strike through uses two tildes. For example: `~~Scratch this.~~` ~~Scratch this.~~

---

## Lists


### Ordered Lists

Ordered lists use numbers. It does not matter what the number is.


#### Ordered list example with 1 number

```md
1. Ordered List Using only 1 number
1. Another item
```

1. Ordered List Using only 1 number
1. Another item


#### Ordered list example with multiple numbers
```md
1. Ordered list using numbers in order
2. Another item
```

1. Ordered list using numbers in order
2. Another item


#### Ordered list example with ordered sub-items

```md
1. Ordered list with ordered sub-items
   1. Ordered sub-item 1
   1. Another subitem
   1. Another subitem
2. Another item
```

1. Ordered list with ordered sub-items
   1. Ordered sub-item 1
   1. Another subitem
   1. Another subitem
2. Another item


#### Ordered list example with un-ordered sub-items
```md
1. Ordered list with unordered sub-items
   - Un-ordered sub-item 1
   + Another subitem
   * Another subitem
2. Another item
```

1. Ordered list with unordered sub-items
   - Un-ordered sub-item 1
   + Another subitem
   * Another subitem
2. Another item


#### Ordered list example with mixed sub-items
```md
1. Ordered list with mixed sub-items
   - Un-ordered sub-item 1
   + Another subitem
2. Another item
   1. Ordered sub item
      - Unordered
      - anoterh
   1. another item
```

1. Ordered list with mixed sub-items
   - Un-ordered sub-item 1
   + Another subitem
2. Another item
   1. Ordered sub item
      - Unordered
      - anoterh
   1. another item


### Un-Ordered lists

Unordered list can use asterisks `*`, minuses `-`, or pluses `+`.

#### Un-Ordered list example
```md
* An un-ordred list
+ Another item
- Another item
```

* An un-ordred list
+ Another item
- Another item


#### Un-Ordred list example with sub-tems
```md
* An un-ordred list with subitems
  - Another item
  - Another item
* Another item
  + something else
  + something else
* Another item
  * something else
  * something else
```

* An un-ordred list with subitems
  - Another item
  - Another item
* Another item
  + something else
  + something else
* Another item
  * something else
  * something else


---

## Links

Links allow you to reference other websites and documents within the site. Links
can be inline, via a reference, or direct.

### Inline Links Examples
```md
[I'm an inline-style link to external site](https://www.google.com/)

[I'm an inline-style link to external site with title](https://www.google.com/ "Google's Homepage")

[I'm an inline-style link to to another relative document](documentation-intro.md)
```

[I'm an inline-style link to external site](https://www.google.com/)

[I'm an inline-style link to external site with title](https://www.google.com/ "Google's Homepage")

[I'm an inline-style link to to another relative document](documentation-intro.md)


### Referenced Links Example
```md
[I'm a reference-style link][arbitrary case-insensitive reference text]

[You can use numbers for reference-style link definitions][1]

Or leave it empty and use the [link text itself].


Some text to show that the reference links can follow later.

[arbitrary case-insensitive reference text]: https://www.mozilla.org/
[1]: http://slashdot.org/
[link text itself]: http://www.reddit.com/
```

[I'm a reference-style link][arbitrary case-insensitive reference text]

[You can use numbers for reference-style link definitions][1]

Or leave it empty and use the [link text itself].


Some text to show that the reference links can follow later.

[arbitrary case-insensitive reference text]: https://www.mozilla.org/
[1]: http://slashdot.org/
[link text itself]: http://www.reddit.com/


### Direct Links

URLs and URLs in angle brackets will automatically get turned into links.
`[http://www.example.com/](http://www.example.com/)`, `[http://example.com/](http://example.com/)` 
and sometimes example.com (but not on GitHub, for example).


---

## Images

Images references are similar to links. The syntax for an image is as follows:

```md
![Image alternate text](Image location or reference. 'Image title text')
```

Images from any folder can be used by providing path to file. Path should be
relative to markdown file. It is recommended that when using images that you
create an **MDX** file and use Docusarus objects. See the [adding new content](documentation-add-content.md)
and [template](documentaion-templates.md) documentation for more information.

### Image inline example
```md

Inline-style: ![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png 'Logo Title Text 1')

```

Inline-style: ![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png 'Logo Title Text 1')

### Image reference example
```md

Reference-style: ![alt text][logo]

[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png 'Logo Title Text 2'

```

Reference-style: ![alt text][logo]

[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png 'Logo Title Text 2'


---

## Code

Code blocks can be used to display code and include syntax highlighting and
line highlighting. To create a code block use three tick marks <code>```</code> followed
by an optional language. In addition, a line number can be provided in curly brackets
to highlight a line. The examples below show code blocks in use.


### Python
    ```python
    s = "Python syntax highlighting"
    print(s)
    ```

```python
s = "Python syntax highlighting"
print(s)
```

### No Language
    ```
    No language indicated, so no syntax highlighting.
    But let's throw in a <b>tag</b>.
    ```

```
No language indicated, so no syntax highlighting.
But let's throw in a <b>tag</b>.
```

### Highlighting a Line
    ```javascript {2}
    function highlightMe() {
      console.log('This line can be highlighted!');
    }
    ```

```javascript {2}
function highlightMe() {
  console.log('This line can be highlighted!');
}
```


---

## Tables

Colons can be used to align columns.

```md

| Tables        |      Are      |    Cool |
| ------------- | :-----------: | ------: |
| column 1 is   | left-aligned  | \16,000 |
| column 2 is   |   centered    |  \$1600 |
| column 3 is   | right-aligned |   \$160 |
| Default is    | left-aligned  |    \$16 |
| zebra stripes |   are neat    |     \$1 |

```

| Tables        |      Are      |    Cool |
| ------------- | :-----------: | ------: |
| column 1 is   | left-aligned  | \16,000 |
| column 2 is   |   centered    |  \$1600 |
| column 3 is   | right-aligned |   \$160 |
| Default is    | left-aligned  |    \$16 |
| zebra stripes |   are neat    |     \$1 |

There must be at least 3 dashes separating each header cell. The outer pipes (|)
are optional, and you don't need to make the raw Markdown line up prettily. You
can also use inline Markdown.

```md
| Markdown | Less      | Pretty     |
| -------- | --------- | ---------- |
| _Still_  | `renders` | **nicely** |
| 1        | 2         | 3          |

```

| Markdown | Less      | Pretty     |
| -------- | --------- | ---------- |
| _Still_  | `renders` | **nicely** |
| 1        | 2         | 3          |

---

## Blockquotes

Blockquotes require the use of a `>` sign.

```md

> Blockquotes are very handy in email to emulate reply text. This line is part of the same quote.

```

> Blockquotes are very handy in email to emulate reply text. This line is part of the same quote.

Quotes will break based on page width.

```md

> This is a very long line that will still be quoted properly when it wraps. Oh boy let's keep writing to make sure this is long enough to actually wrap for everyone. Oh, you can _put_ **Markdown** into a blockquote.

```
> This is a very long line that will still be quoted properly when it wraps. Oh boy let's keep writing to make sure this is long enough to actually wrap for everyone. Oh, you can _put_ **Markdown** into a blockquote.

---

## Inline HTML

Inline HTML can also be used in markdown language.

```html
<dl>
  <dt>Definition list</dt>
  <dd>Is something people use sometimes.</dd>

  <dt>Markdown in HTML</dt>
  <dd>Does *not* work **very** well. Use HTML <em>tags</em>.</dd>
</dl>
```

<dl>
  <dt>Definition list</dt>
  <dd>Is something people use sometimes.</dd>

  <dt>Markdown in HTML</dt>
  <dd>Does *not* work **very** well. Use HTML <em>tags</em>.</dd>
</dl>

---

## Line Breaks

Here's a line for us to start with.

This line is separated from the one above by two newlines, so it will be a _separate paragraph_.

This line is also a separate paragraph, but... This line is only separated by
a single newline, so it's a separate line in the _same paragraph_.

---

## Admonitions

Admotions provide additional information and can be labeled with a title.

```md
:::note My Note

This is a note

:::
```

:::note My Note

This is a note

:::

```md
:::tip

This is a tip

:::
```

:::tip

This is a tip

:::

```md
:::important

This is important

:::
```

:::important

This is important

:::

```md
:::caution

This is a caution

:::
```

:::caution

This is a caution

:::

```md
:::warning

This is a warning

:::
```

:::warning

This is a warning

:::
